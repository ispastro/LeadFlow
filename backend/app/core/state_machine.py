import logging
from enum import Enum
from typing import Optional, Tuple

from app.services.groq_client import groq_service
from app.utils.text_processing import extract_email

logger = logging.getLogger(__name__)


class ConversationStage(str, Enum):
    NEW = "NEW"
    GREETED = "GREETED"
    DISCOVERY = "DISCOVERY"
    INTENT_DETECTED = "INTENT_DETECTED"
    EMAIL_REQUESTED = "EMAIL_REQUESTED"
    CAPTURED = "CAPTURED"
    POST_CAPTURE = "POST_CAPTURE"


class StateMachine:

    def detect_intent(self, message: str) -> str:
        """Lightweight LLM intent classifier — returns HIGH_INTEREST | INFORMATION_SEEKING | LOW_INTEREST."""
        prompt = (
            'Classify user intent as HIGH_INTEREST, INFORMATION_SEEKING, or LOW_INTEREST.\n\n'
            'HIGH_INTEREST: pricing, cost, plans, demo, trial, buying, signing up, getting started, '
            'integrations, features, or follow-up interest.\n'
            'INFORMATION_SEEKING: general questions like "what is this", "tell me about", first-time greeting.\n'
            'LOW_INTEREST: "no thanks", "not interested", "just browsing".\n\n'
            f'Message: "{message}"\n\n'
            'Classify as ONE word only:'
        )
        try:
            response = groq_service.chat_completion(
                [{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10,
            )
            intent = response.strip().upper()
            logger.debug("Intent detected: %s for message='%.60s'", intent, message)
            return intent
        except Exception as exc:
            logger.warning("Intent detection failed: %s — defaulting to INFORMATION_SEEKING", exc)
            return "INFORMATION_SEEKING"

    def transition(
        self,
        current_stage: ConversationStage,
        message: str,
        email_captured: bool,
        message_count: int,
    ) -> Tuple[ConversationStage, Optional[str]]:
        """
        Compute next stage given current context.
        Returns (new_stage, extracted_email_or_None).
        """
        # Terminal: already have the email
        if email_captured or current_stage == ConversationStage.POST_CAPTURE:
            return ConversationStage.POST_CAPTURE, None

        # Waiting for email → try to extract one
        if current_stage == ConversationStage.EMAIL_REQUESTED:
            email = extract_email(message)
            if email:
                return ConversationStage.CAPTURED, email
            return ConversationStage.EMAIL_REQUESTED, None

        # First message ever
        if current_stage == ConversationStage.NEW and message_count == 0:
            return ConversationStage.GREETED, None

        # Discover intent after greeting / during discovery
        if current_stage in (ConversationStage.GREETED, ConversationStage.DISCOVERY):
            intent = self.detect_intent(message)
            if intent == "HIGH_INTEREST" or message_count >= 2:
                return ConversationStage.INTENT_DETECTED, None
            return ConversationStage.DISCOVERY, None

        # High-intent confirmed → request email
        if current_stage == ConversationStage.INTENT_DETECTED:
            return ConversationStage.EMAIL_REQUESTED, None

        return current_stage, None

    # ------------------------------------------------------------------
    # Stage-specific instruction helpers
    # ------------------------------------------------------------------

    def get_system_instructions(self, stage: ConversationStage) -> str:
        instructions = {
            ConversationStage.NEW: "",
            ConversationStage.GREETED: "Greet the user warmly and ask how you can help them today.",
            ConversationStage.DISCOVERY: (
                "Answer their questions accurately using the knowledge base. Be helpful and build trust."
            ),
            ConversationStage.INTENT_DETECTED: (
                "They're showing high interest! Answer their question thoroughly and professionally."
            ),
            ConversationStage.EMAIL_REQUESTED: (
                "Gently ask: 'To get you started, what's your name and email address?'"
            ),
            ConversationStage.CAPTURED: "Email captured! Confirm receipt and offer continued assistance.",
            ConversationStage.POST_CAPTURE: "Continue being helpful. Answer any remaining questions.",
        }
        return instructions.get(stage, "")

    def should_append_email_ask(self, stage: ConversationStage) -> bool:
        return stage == ConversationStage.EMAIL_REQUESTED

    def get_email_ask_text(self) -> str:
        return "\n\nTo get you started, what's your name and email address?"

    def get_capture_confirmation(self, email: str) -> str:
        return (
            f"Perfect! I've sent the setup details to {email}. "
            "Our team will reach out within the next few hours.\n\n"
            "Do you have any other questions in the meantime?"
        )


# Singleton
state_machine = StateMachine()
