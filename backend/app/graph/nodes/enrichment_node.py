import json
import logging
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage

from app.schemas.graph_state import GraphState
from app.services.groq_client import get_json_llm
from app.utils.prompts import ENRICHMENT_PROMPT
from app.utils.text_processing import extract_email, extract_name

logger = logging.getLogger(__name__)


def _enrich_mock(email: str, name: Optional[str], conversation_text: str) -> dict:
    """
    LLM-based mock enrichment. Infers company/role from email domain + context.
    Replace this function body with a real API call (Clearbit, Apollo, Hunter)
    when ready — the interface stays the same.
    """
    llm = get_json_llm(temperature=0.1)
    prompt = (
        f"Email: {email}\n"
        f"Name: {name or 'unknown'}\n"
        f"Conversation snippet: {conversation_text[:400]}\n\n"
        "Infer company and role information."
    )
    messages = [
        SystemMessage(content=ENRICHMENT_PROMPT),
        HumanMessage(content=prompt),
    ]
    result = llm.invoke(messages)
    return json.loads(result.content)


def enrichment_node(state: GraphState) -> GraphState:
    """Enrich the lead with company/role data."""
    conversation_history = state.get("conversation_history", [])
    conversation_text = " ".join(m.get("content", "") for m in conversation_history)

    # Extract email from conversation if not already in state
    lead_email = state.get("lead_email")
    lead_name = state.get("lead_name")

    if not lead_email:
        # Scan full conversation for an email address
        for msg in conversation_history:
            found = extract_email(msg.get("content", ""))
            if found:
                lead_email = found
                break
        # Also check current message
        if not lead_email:
            lead_email = extract_email(state.get("user_message", ""))

    if not lead_name and lead_email:
        lead_name = extract_name(state.get("user_message", ""))

    if not lead_email:
        # No email yet — enrichment is a no-op at this stage
        logger.debug("enrichment_node | no email yet, skipping enrichment")
        return {**state, "current_node": "enrichment_node"}

    try:
        data = _enrich_mock(lead_email, lead_name, conversation_text)
        logger.info(
            "enrichment_node | email=%s company=%s role=%s source=%s",
            lead_email,
            data.get("company_name"),
            data.get("lead_role"),
            data.get("enrichment_source"),
        )
        return {
            **state,
            "lead_email": lead_email,
            "lead_name": lead_name,
            "company_name": data.get("company_name"),
            "company_size": data.get("company_size"),
            "company_industry": data.get("company_industry"),
            "lead_role": data.get("lead_role"),
            "enrichment_source": data.get("enrichment_source", "mock"),
            "current_node": "enrichment_node",
        }
    except Exception as exc:
        # Fail-safe: log and continue without enrichment data
        logger.warning("enrichment_node | failed for %s: %s — continuing", lead_email, exc)
        return {
            **state,
            "lead_email": lead_email,
            "lead_name": lead_name,
            "enrichment_source": "failed",
            "error": str(exc),
            "current_node": "enrichment_node",
        }
