"""
critic_node — Phase 4 (Brand Guardrails)

The Critic Agent validates every draft response against the Brand Persona
before it is delivered to the user.

Flow:
  draft_response → [critic_node] → approved? → deliver_node
                                 → rejected (revision < 2)? → drafting_node
                                 → rejected (revision >= 2)? → manual_review

The critic can also supply a `revised_response` — a corrected version it
produced inline — which is used as final_response if approved=True.
"""
from __future__ import annotations

import json
import logging

from langchain_core.messages import SystemMessage, HumanMessage

from app.schemas.critic import CriticVerdict
from app.schemas.graph_state import GraphState
from app.services.groq_client import get_json_llm
from app.utils.prompts import BRAND_PERSONA

logger = logging.getLogger(__name__)

_MAX_REVISIONS = 2


def critic_node(state: GraphState) -> GraphState:
    """
    Validate the draft response against the brand persona.
    Returns updated state with critic_approved, critic_feedback, final_response.
    """
    draft = state.get("draft_response", "")
    revision_count = state.get("critic_revision_count", 0)

    if not draft:
        logger.error("critic_node | no draft_response in state — routing to manual_review")
        return {
            **state,
            "critic_approved": False,
            "critic_feedback": "No draft was produced by the drafting node.",
            "route_to": "manual_review",
            "error": "critic_node: missing draft_response",
            "current_node": "critic_node",
        }

    prompt = (
        f"Review this AI-generated response for brand compliance:\n\n"
        f"---\n{draft}\n---\n\n"
        "Return your verdict as JSON."
    )

    try:
        llm = get_json_llm(temperature=0.1)
        messages = [
            SystemMessage(content=BRAND_PERSONA),
            HumanMessage(content=prompt),
        ]
        result = llm.invoke(messages)
        raw = json.loads(result.content)
        verdict = CriticVerdict(**raw)

    except Exception as exc:
        # If the critic itself fails, approve the draft with a warning
        # rather than blocking the user — fail open on critic errors
        logger.warning(
            "critic_node | critic call failed: %s — approving draft (fail-open)", exc
        )
        return {
            **state,
            "critic_approved": True,
            "final_response": draft,
            "critic_feedback": None,
            "current_node": "critic_node",
        }

    if verdict.approved:
        # Use critic's revised version if it provided one, else use draft
        final = verdict.revised_response or draft
        logger.info(
            "critic_node | APPROVED session=%s violations=%s",
            state.get("session_id"),
            verdict.violations,
        )
        return {
            **state,
            "critic_approved": True,
            "final_response": final,
            "critic_feedback": None,
            "current_node": "critic_node",
        }

    # Rejected path
    new_revision_count = revision_count + 1
    logger.warning(
        "critic_node | REJECTED (revision %d/%d) session=%s violations=%s feedback='%s'",
        new_revision_count,
        _MAX_REVISIONS,
        state.get("session_id"),
        verdict.violations,
        verdict.feedback,
    )

    if new_revision_count >= _MAX_REVISIONS:
        # Exhausted revisions — route to manual review (fail-safe)
        logger.error(
            "critic_node | max revisions reached — routing to manual_review session=%s",
            state.get("session_id"),
        )
        return {
            **state,
            "critic_approved": False,
            "critic_feedback": verdict.feedback,
            "critic_revision_count": new_revision_count,
            "route_to": "manual_review",
            "error": "critic_failed: max revisions exceeded",
            "error_node": "critic_node",
            "current_node": "critic_node",
        }

    # Send back for revision
    return {
        **state,
        "critic_approved": False,
        "critic_feedback": verdict.feedback,
        "critic_revision_count": new_revision_count,
        "route_to": "drafting_node",   # graph router reads this
        "current_node": "critic_node",
    }
