import html
import logging
import re

from langchain_core.messages import HumanMessage

from app.db import conversations as conv_db
from app.db import messages as msg_db
from app.schemas.graph_state import GraphState

logger = logging.getLogger(__name__)


def _sanitise(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def input_node(state: GraphState) -> GraphState:
    """Sanitise input and load conversation context."""
    session_id = state["session_id"]
    raw_message = state.get("user_message", "")

    clean_message = _sanitise(raw_message)
    if not clean_message:
        logger.warning("input_node | empty message after sanitisation session=%s", session_id)
        return {
            **state,
            "user_message": clean_message,
            "route_to": "manual_review",
            "error": "Empty message after sanitisation",
            "error_node": "input_node",
            "current_node": "input_node",
        }

    # Load or create conversation
    try:
        conversation = conv_db.get_or_create_conversation(session_id)
        conversation_id = conversation["id"]
        history = msg_db.get_conversation_history(conversation_id, limit=6)
        message_count = msg_db.count_user_messages(conversation_id)

        # Persist this user message immediately
        msg_db.create_message(conversation_id, "user", clean_message)
    except Exception as exc:
        logger.error("input_node | DB error session=%s: %s", session_id, exc)
        return {
            **state,
            "user_message": clean_message,
            "route_to": "manual_review",
            "error": str(exc),
            "error_node": "input_node",
            "current_node": "input_node",
        }

    logger.info(
        "input_node | session=%s conv=%s msgs=%d",
        session_id, conversation_id, message_count,
    )

    return {
        **state,
        "user_message": clean_message,
        "conversation_id": conversation_id,
        "conversation_history": history,
        "message_count": message_count,
        "email_captured": conversation.get("email_captured", False),
        "legacy_stage": conversation.get("stage", "NEW"),
        "messages": [HumanMessage(content=clean_message)],
        "current_node": "input_node",
        "is_manual_review": False,
        "lead_persisted": False,
        "critic_revision_count": state.get("critic_revision_count", 0),
    }
