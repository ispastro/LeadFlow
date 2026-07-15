import logging

from app.db import messages as msg_db
from app.db import conversations as conv_db
from app.db import leads as leads_db
from app.schemas.graph_state import GraphState
from app.utils.prompts import MANUAL_REVIEW_REASON_MAP

logger = logging.getLogger(__name__)

_FALLBACK_USER_MESSAGE = (
    "Thanks for reaching out! I want to make sure you get the best possible answer. "
    "A member of our team will personally follow up with you very shortly."
)


def manual_review_node(state: GraphState) -> GraphState:
    """Mark lead for manual review and return a safe fallback response."""
    session_id = state.get("session_id", "unknown")
    conversation_id = state.get("conversation_id")
    error = state.get("error", "unknown")
    error_node = state.get("error_node", "unknown")
    lead_email = state.get("lead_email")

    # Determine human-readable reason
    reason_key = error.split(":")[0] if error else "unknown"
    reason = MANUAL_REVIEW_REASON_MAP.get(reason_key, MANUAL_REVIEW_REASON_MAP["unknown"])

    logger.error(
        "manual_review_node | session=%s error_node=%s error='%s' reason='%s' email=%s",
        session_id, error_node, error, reason, lead_email,
    )

    # --- Upsert lead as manual_review (idempotent) ---------------------------
    lead_id = state.get("lead_id")
    if lead_email and conversation_id:
        try:
            lead_id = leads_db.upsert_lead(
                conversation_id=conversation_id,
                email=lead_email,
                name=state.get("lead_name"),
                intent_trigger="manual_review",
                qualification_score=state.get("qualification_score"),
                qualification_tier=state.get("qualification_tier", "warm"),
                is_manual_review=True,
                metadata={
                    "error": error,
                    "error_node": error_node,
                    "reason": reason,
                },
            )
            logger.info(
                "manual_review_node | lead upserted id=%s is_manual_review=True",
                lead_id,
            )
        except Exception as exc:
            logger.error(
                "manual_review_node | lead upsert also failed: %s — lead may be lost! "
                "session=%s email=%s",
                exc, session_id, lead_email,
            )

    # --- Persist fallback AI message -----------------------------------------
    if conversation_id:
        try:
            msg_db.create_message(conversation_id, "assistant", _FALLBACK_USER_MESSAGE)
            conv_db.update_conversation_timestamp(conversation_id)
        except Exception as exc:
            logger.error("manual_review_node | message persist failed: %s", exc)

    return {
        **state,
        "final_response": _FALLBACK_USER_MESSAGE,
        "is_manual_review": True,
        "lead_id": lead_id,
        "lead_persisted": True,
        "current_node": "manual_review_node",
    }
