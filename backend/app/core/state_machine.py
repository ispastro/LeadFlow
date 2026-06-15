from enum import Enum
from typing import Dict, Optional, Tuple, List
from app.services.groq_client import groq_service
from app.utils.text_processing import extract_email

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
        """Lightweight LLM intent classifier"""
        prompt = f"""Classify user intent as HIGH_INTEREST, INFORMATION_SEEKING, or LOW_INTEREST.

HIGH_INTEREST: User asks about pricing, cost, plans, demo, trial, buying, signing up, getting started, integrations, features, or wants to learn more after initial question
INFORMATION_SEEKING: General questions like "what is this", "tell me about", first-time greeting
LOW_INTEREST: "no thanks", "not interested", "just browsing"

Message: "{message}"

Classify as ONE word only:"""
        
        try:
            response = groq_service.chat_completion(
                [{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )
            return response.strip().upper()
        except Exception as e:
            print(f"⚠️ Intent detection failed: {e}")
            return "INFORMATION_SEEKING"
    
    def transition(
        self,
        current_stage: ConversationStage,
        message: str,
        email_captured: bool,
        message_count: int
    ) -> Tuple[ConversationStage, Optional[str]]:
        """
        Determine next stage and return email if found
        Returns: (new_stage, extracted_email)
        """
        
        # Terminal state: already captured
        if email_captured or current_stage == ConversationStage.POST_CAPTURE:
            return ConversationStage.POST_CAPTURE, None
        
        # EMAIL_REQUESTED -> Check for email in message
        if current_stage == ConversationStage.EMAIL_REQUESTED:
            email = extract_email(message)
            if email:
                return ConversationStage.CAPTURED, email
            # No email found, stay in EMAIL_REQUESTED
            return ConversationStage.EMAIL_REQUESTED, None
        
        # NEW -> GREETED (first interaction)
        if current_stage == ConversationStage.NEW and message_count == 0:
            return ConversationStage.GREETED, None
        
        # GREETED/DISCOVERY -> Check for high intent
        if current_stage in [ConversationStage.GREETED, ConversationStage.DISCOVERY]:
            intent = self.detect_intent(message)
            
            if intent == "HIGH_INTEREST" or message_count >= 2:
                return ConversationStage.INTENT_DETECTED, None
            
            # Stay in DISCOVERY after greeting
            return ConversationStage.DISCOVERY, None
        
        # INTENT_DETECTED -> EMAIL_REQUESTED (after answering their question)
        if current_stage == ConversationStage.INTENT_DETECTED:
            return ConversationStage.EMAIL_REQUESTED, None
        
        # Default: stay in current stage
        return current_stage, None
    
    def get_system_instructions(self, stage: ConversationStage) -> str:
        """Get stage-specific instructions for RAG"""
        
        if stage == ConversationStage.NEW:
            return ""
        
        elif stage == ConversationStage.GREETED:
            return "Greet the user warmly and ask how you can help them today."
        
        elif stage == ConversationStage.DISCOVERY:
            return "Answer their questions accurately using the knowledge base. Be helpful and build trust."
        
        elif stage == ConversationStage.INTENT_DETECTED:
            return "They're showing high interest! Answer their question thoroughly and professionally."
        
        elif stage == ConversationStage.EMAIL_REQUESTED:
            return "Gently ask: 'To get you started, what's your name and email address?'"
        
        elif stage == ConversationStage.CAPTURED:
            return "Email captured! Confirm receipt and offer continued assistance."
        
        elif stage == ConversationStage.POST_CAPTURE:
            return "Continue being helpful. Answer any remaining questions they have."
        
        return ""
    
    def should_append_email_ask(self, stage: ConversationStage) -> bool:
        """Should we append email request to response?"""
        return stage == ConversationStage.EMAIL_REQUESTED
    
    def get_email_ask_text(self) -> str:
        """Get email request text"""
        return "\n\nTo get you started, what's your name and email address?"
    
    def get_capture_confirmation(self, email: str) -> str:
        """Get confirmation message after email capture"""
        return f"Perfect! I've sent the setup details to {email}. Our team will reach out within the next few hours.\n\nDo you have any other questions in the meantime?"

# Singleton instance
state_machine = StateMachine()
