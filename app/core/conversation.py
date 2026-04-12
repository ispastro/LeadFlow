from typing import Dict, List, Optional
from enum import Enum


class ConversationState(str, Enum):
    GREETING = "greeting"
    ANSWERING = "answering"
    QUALIFYING = "qualifying"
    CAPTURED = "captured"


class ConversationService:
    
    def get_state(
        self,
        message_count: int,
        lead_captured: bool,
        intent_data: Dict = None
    ) -> ConversationState:
        """Determine current conversation state"""
        
        if lead_captured:
            return ConversationState.CAPTURED
        
        if message_count == 0:
            return ConversationState.GREETING
        
        # Check if we should qualify
        if intent_data:
            if intent_data.get('intent') in ['HIGH_INTEREST', 'READY_TO_BUY']:
                return ConversationState.QUALIFYING
        
        if message_count >= 2:
            return ConversationState.QUALIFYING
        
        return ConversationState.ANSWERING
    
    def get_state_instructions(self, state: ConversationState) -> str:
        """Get additional instructions based on conversation state"""
        
        if state == ConversationState.GREETING:
            return "This is the first interaction. Greet the user warmly and ask how you can help."
        
        elif state == ConversationState.ANSWERING:
            return "Answer the user's questions accurately and helpfully."
        
        elif state == ConversationState.QUALIFYING:
            return "The user seems interested. After answering their question, naturally ask for their contact information (name and email) so you can follow up."
        
        elif state == ConversationState.CAPTURED:
            return "Lead information has been captured. Continue being helpful and answer any remaining questions."
        
        return ""


# Singleton instance
conversation_service = ConversationService()
