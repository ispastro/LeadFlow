"""
deliver_node — Final delivery node.

Responsibilities:
- Persist the final AI response to the messages table
- Upsert the lead record with all qualification + enrichment data (idempotent)
- Update conversation stage in the legacy table (backwards compatibility)
- Return the final state with `final_response` ready for the API layer

Observability: all lead decisions are captured via LangSmith traces.
Notifications: handled externally via LangSmith alerts or webhook integrations.
"""
from __future__ import annotations

import logging

from app.db import conversations as conv_db
from app.db import messages as msg_db
from app.db import leads as leads_db
from app.schemas.graph_state import GraphState
from app.core.state_machine import ConversationStage

logger = logging.getLogger(__name__)


def deliver_node(state: GraphState) -> GraphState:
    """Persist everything and return the final response."""
    conversation_id = state.get("conversation_id")
    session_id      = state.get("session_id", "unknown")
    final_response  = state.get("final_response") or state.get("draft_response", "")
    lead_email      = state.get("lead_email")

    # Capture confirmation message
    if lead_email and not state.get("email_captured"):
        final_response = (
            f"Perfect! I've noted your details and our team will reach out to "
            f"{lead_email} within a few hours.\n\nDo you have any other questions?"
        )

    # --- Persist AI message --------------------------------------------------
    try:
        msg_db.create_message(conversation_id, "assistant", final_response)
        conv_db.update_conversation_timestamp(conversation_id)
    except Exception as exc:
        logger.error("deliver_node | failed to persist message: %s", exc)

    # --- Update legacy stage -------------------------------------------------
    try:
        new_stage = (
            ConversationStage.CAPTURED.value    if lead_email and not state.get("email_captured")
            else ConversationStage.POST_CAPTURE.value if state.get("email_captured")
            else ConversationStage.DISCOVERY.value
        )
        conv_db.update_conversation_stage(conversation_id, new_stage, bool(lead_email))
    except Exception as exc:
        logger.warning("deliver_node | stage update failed (non-fatal): %s", exc)

    # --- Upsert lead (idempotent) --------------------------------------------
    lead_id = state.get("lead_id")
    if lead_email:
        try:
            lead_id = leads_db.upsert_lead(
                conversation_id=conversation_id,
                email=lead_email,
                name=state.get("lead_name"),
                intent_trigger=(state.get("intent_signals") or ["other"])[0],
                qualification_score=state.get("qualification_score"),
                qualification_tier=state.get("qualification_tier"),
                intent_signals=state.get("intent_signals"),
                company_name=state.get("company_name"),
                company_size=state.get("company_size"),
                company_industry=state.get("company_industry"),
                lead_role=state.get("lead_role"),
                enrichment_source=state.get("enrichment_source"),
                requires_human_approval=state.get("requires_human_approval", False),
                human_approved=state.get("human_approved"),
                human_reviewer=state.get("human_reviewer"),
                human_notes=state.get("human_notes"),
                is_manual_review=False,
            )
            logger.info("deliver_node | lead upserted id=%s email=%s", lead_id, lead_email)
        except Exception as exc:
            logger.error("deliver_node | lead upsert failed: %s", exc)

    logger.info(
        "deliver_node | session=%s response_len=%d lead_id=%s",
        session_id, len(final_response), lead_id,
    )

    return {
        **state,
        "final_response": final_response,
        "lead_id": lead_id,
        "lead_persisted": True,
        "email_captured": bool(lead_email),
        "current_node": "deliver_node",
    }
