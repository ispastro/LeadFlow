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
    
    def get_system_prompt(self, state: ConversationState, context: str = "") -> str:
        """Get system prompt based on conversation state"""
        
        base_context = f"""You are a helpful AI sales and support agent.

Context about the business:
{context}

"""
        
        if state == ConversationState.GREETING:
            return base_context + """This is the first interaction. Greet the user warmly and ask how you can help."""
        
        elif state == ConversationState.ANSWERING:
            return base_context + """Answer the user's questions accurately and helpfully based on the context provided."""
        
        elif state == ConversationState.QUALIFYING:
            return base_context + """The user seems interested. After answering their question, naturally ask for their contact information (name and email) so you can follow up."""
        
        elif state == ConversationState.CAPTURED:
            return base_context + """Lead information has been captured. Continue being helpful and answer any remaining questions."""
        
        return base_context


# Singleton instance
conversation_service = ConversationService()
