import json
import logging

from langchain_core.messages import SystemMessage, HumanMessage

from app.schemas.graph_state import GraphState
from app.schemas.qualification import QualificationResult
from app.services.groq_client import get_json_llm
from app.utils.prompts import QUALIFICATION_PROMPT

logger = logging.getLogger(__name__)


def _build_qualification_payload(state: GraphState) -> str:
    """Build the human message payload sent to the qualification LLM."""
    lines = [
        f"Email: {state.get('lead_email', 'unknown')}",
        f"Name: {state.get('lead_name', 'unknown')}",
        f"Company: {state.get('company_name', 'unknown')}",
        f"Company size: {state.get('company_size', 'unknown')}",
        f"Industry: {state.get('company_industry', 'unknown')}",
        f"Role: {state.get('lead_role', 'unknown')}",
        f"Message count: {state.get('message_count', 0)}",
        "",
        "CONVERSATION TRANSCRIPT:",
    ]
    for msg in state.get("conversation_history", [])[-8:]:
        role = msg.get("role", "user").upper()
        content = msg.get("content", "")[:300]
        lines.append(f"  [{role}]: {content}")

    lines += [
        "",
        "Current user message:",
        f"  {state.get('user_message', '')}",
    ]
    return "\n".join(lines)


def qualification_node(state: GraphState) -> GraphState:
    """Score the lead and determine routing tier."""

    # Skip qualification if no email has been captured yet
    if not state.get("lead_email"):
        logger.debug("qualification_node | no email yet, skipping scoring")
        return {
            **state,
            "qualification_score": None,
            "qualification_tier": "cold",
            "current_node": "qualification_node",
        }

    payload = _build_qualification_payload(state)

    try:
        llm = get_json_llm(temperature=0.1)
        messages = [
            SystemMessage(content=QUALIFICATION_PROMPT),
            HumanMessage(content=payload),
        ]
        result = llm.invoke(messages)
        raw = json.loads(result.content)

        # Pydantic validation — enforces schema and normalises values
        qual = QualificationResult(**raw)

        logger.info(
            "qualification_node | email=%s score=%d tier=%s action=%s",
            state.get("lead_email"),
            qual.score,
            qual.tier,
            qual.recommended_action,
        )

        return {
            **state,
            "qualification_score": qual.score,
            "qualification_tier": qual.tier,
            "qualification_reasoning": qual.reasoning,
            "intent_signals": qual.intent_signals,
            "disqualification_reason": qual.disqualification_reason,
            "current_node": "qualification_node",
        }

    except Exception as exc:
        # Fail-safe: route to manual_review, never discard the lead
        logger.error(
            "qualification_node | FAILED for %s: %s — routing to manual_review",
            state.get("lead_email"),
            exc,
        )
        return {
            **state,
            "qualification_score": None,
            "qualification_tier": "warm",       # safe default
            "route_to": "manual_review",
            "error": f"qualification_failed: {exc}",
            "error_node": "qualification_node",
            "current_node": "qualification_node",
        }
