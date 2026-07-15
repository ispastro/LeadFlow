import html
import logging
import re
import time
from collections import defaultdict
from threading import Lock

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request

from app.schemas.chat import ChatRequest, ChatResponse
from app.core.rag import rag_service
from app.core.state_machine import state_machine, ConversationStage
from app.db import conversations as conv_db
from app.db import messages as msg_db
from app.db import leads as leads_db
from app.utils.text_processing import extract_name
from app.services.email_service import email_service
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# ---------------------------------------------------------------------------
# Simple in-process rate limiter (per session_id, sliding window)
# For multi-process/multi-worker deployments replace with Redis-backed limiter.
# ---------------------------------------------------------------------------
_rate_buckets: dict[str, list[float]] = defaultdict(list)
_rate_lock = Lock()
_WINDOW_SECONDS = 60


def _check_rate_limit(session_id: str) -> None:
    """Raise 429 if session_id exceeds chat_rate_limit_per_minute."""
    limit = settings.chat_rate_limit_per_minute
    now = time.time()
    cutoff = now - _WINDOW_SECONDS

    with _rate_lock:
        timestamps = _rate_buckets[session_id]
        # Evict old timestamps
        _rate_buckets[session_id] = [t for t in timestamps if t > cutoff]
        if len(_rate_buckets[session_id]) >= limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded — maximum {limit} messages per minute.",
            )
        _rate_buckets[session_id].append(now)


def _sanitise_message(text: str) -> str:
    """Strip HTML tags, collapse whitespace, and normalise the input."""
    # Unescape any HTML entities first, then strip tags
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)          # strip HTML tags
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)  # control chars
    text = re.sub(r"\s+", " ", text).strip()
    return text


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks, http_request: Request):
    """State-machine-driven chat endpoint (public — no auth required)."""
    # ---- Rate limiting -------------------------------------------------------
    _check_rate_limit(request.session_id)

    # ---- Input sanitisation --------------------------------------------------
    clean_message = _sanitise_message(request.message)
    if not clean_message:
        raise HTTPException(status_code=422, detail="Message is empty after sanitisation.")

    start_time = time.time()
    logger.info("Chat | session=%s stage=? msg='%.60s'", request.session_id, clean_message)

    try:
        # 1. Load / create conversation
        conversation = conv_db.get_or_create_conversation(request.session_id)
        conversation_id = conversation["id"]
        current_stage = ConversationStage(conversation["stage"])
        email_captured = conversation["email_captured"]

        # 2. History + message count
        history = msg_db.get_conversation_history(conversation_id, limit=4)
        message_count = msg_db.count_user_messages(conversation_id)

        # 3. Persist user message
        msg_db.create_message(conversation_id, "user", clean_message)

        # 4. State transition
        new_stage, extracted_email = state_machine.transition(
            current_stage=current_stage,
            message=clean_message,
            email_captured=email_captured,
            message_count=message_count,
        )
        logger.info(
            "Chat | session=%s transition %s → %s",
            request.session_id,
            current_stage.value,
            new_stage.value,
        )

        # 5. Lead capture
        if extracted_email and not email_captured:
            name = extract_name(clean_message)

            # Infer intent from full conversation text
            all_messages = msg_db.get_conversation_history(conversation_id, limit=10)
            conversation_text = " ".join(m["content"].lower() for m in all_messages)

            if any(w in conversation_text for w in ["price", "pricing", "cost", "plan", "subscription", "pay"]):
                intent_trigger = "pricing"
            elif any(w in conversation_text for w in ["demo", "trial", "test", "try"]):
                intent_trigger = "demo"
            elif any(w in conversation_text for w in ["integrate", "integration", "api", "connect", "hubspot", "salesforce"]):
                intent_trigger = "integration"
            elif new_stage == ConversationStage.DISCOVERY:
                intent_trigger = "unprompted"
            else:
                intent_trigger = "other"

            lead_id = leads_db.create_lead(
                conversation_id=conversation_id,
                email=extracted_email,
                name=name,
                intent=intent_trigger,
                metadata={"stage": new_stage.value},
            )

            email_captured = True
            new_stage = ConversationStage.CAPTURED

            background_tasks.add_task(
                email_service.send_lead_notification,
                lead_email=extracted_email,
                lead_name=name,
                intent=intent_trigger,
                quality="MEDIUM",
                conversation_id=conversation_id,
                lead_id=lead_id,
            )
            logger.info("Lead captured | email=%s lead_id=%s", extracted_email, lead_id)

        # 6. Persist new stage
        conv_db.update_conversation_stage(conversation_id, new_stage.value, email_captured)

        # 7. Generate RAG response
        system_instructions = state_machine.get_system_instructions(new_stage)
        ai_response = rag_service.generate_response(
            user_message=clean_message,
            conversation_history=history[:-1],
            additional_instructions=system_instructions,
        )

        # 8. Append email ask if needed
        if state_machine.should_append_email_ask(new_stage) and not email_captured:
            ai_response += state_machine.get_email_ask_text()

        # 9. Override with capture confirmation
        if new_stage == ConversationStage.CAPTURED:
            ai_response = state_machine.get_capture_confirmation(extracted_email)

        # 10. Persist AI message
        msg_db.create_message(conversation_id, "assistant", ai_response)
        conv_db.update_conversation_timestamp(conversation_id)

        elapsed_ms = (time.time() - start_time) * 1000
        logger.info("Chat | session=%s done in %.0fms", request.session_id, elapsed_ms)

        return ChatResponse(
            response=ai_response,
            session_id=request.session_id,
            should_capture_lead=new_stage == ConversationStage.EMAIL_REQUESTED,
            lead_captured=email_captured,
            conversation_state=new_stage.value,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "Chat error | session=%s: %s",
            request.session_id,
            exc,
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="An error occurred processing your message.")
