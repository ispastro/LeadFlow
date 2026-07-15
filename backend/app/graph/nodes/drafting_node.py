import logging

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from app.core.rag import rag_retrieve
from app.schemas.graph_state import GraphState
from app.services.groq_client import get_llm
from app.utils.prompts import DRAFTING_SYSTEM_PROMPT
from app.core.state_machine import state_machine, ConversationStage

logger = logging.getLogger(__name__)

_MAX_REVISIONS = 2


def drafting_node(state: GraphState) -> GraphState:
    """Generate a candidate AI response using RAG context."""
    user_message = state.get("user_message", "")
    revision_count = state.get("critic_revision_count", 0)
    critic_feedback = state.get("critic_feedback")

    # --- Determine stage-specific instructions --------------------------------
    try:
        stage = ConversationStage(state.get("legacy_stage", "DISCOVERY"))
    except ValueError:
        stage = ConversationStage.DISCOVERY

    stage_instructions = state_machine.get_system_instructions(stage)

    # Inject critic feedback into the next draft when revising
    revision_note = ""
    if critic_feedback and revision_count > 0:
        revision_note = (
            f"\n\nPREVIOUS DRAFT WAS REJECTED. Critic feedback:\n"
            f"{critic_feedback}\n"
            "Rewrite the response addressing this feedback exactly."
        )

    # --- Retrieve RAG context (traced as a tool span in LangSmith) -----------
    try:
        context = rag_retrieve.invoke(user_message)
        rag_sources = ["knowledge_base"]
    except Exception as exc:
        logger.warning("drafting_node | RAG retrieve failed: %s — using fallback", exc)
        context = "LeadFlow AI converts website visitors into qualified leads automatically."
        rag_sources = ["fallback"]

    # --- Build prompt ---------------------------------------------------------
    system_content = DRAFTING_SYSTEM_PROMPT.format(
        additional_instructions=stage_instructions + revision_note,
        context=context,
    )

    # Build message list from conversation history
    messages = [SystemMessage(content=system_content)]
    for msg in state.get("conversation_history", [])[-4:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))
    messages.append(HumanMessage(content=user_message))

    # --- LLM call (auto-traced by LangSmith) ----------------------------------
    try:
        llm = get_llm(temperature=0.3)
        result = llm.invoke(messages)
        draft = result.content.strip()
    except Exception as exc:
        logger.error("drafting_node | LLM call failed: %s", exc)
        draft = (
            "I'm sorry, I'm having trouble responding right now. "
            "A member of our team will follow up with you shortly."
        )

    # Append email ask if stage requires it and email not yet captured
    if (
        stage == ConversationStage.EMAIL_REQUESTED
        and not state.get("email_captured")
    ):
        draft += state_machine.get_email_ask_text()

    logger.info(
        "drafting_node | revision=%d draft_len=%d session=%s",
        revision_count, len(draft), state.get("session_id"),
    )

    return {
        **state,
        "draft_response": draft,
        "rag_sources": rag_sources,
        "messages": [AIMessage(content=draft)],
        "current_node": "drafting_node",
    }
