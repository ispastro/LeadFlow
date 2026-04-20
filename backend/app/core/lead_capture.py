from typing import Dict, Optional, List
from app.services.groq_client import groq_service


class LeadCaptureService:
    
    def detect_intent(self, user_message: str, conversation_history: List[Dict] = None) -> Dict:
        """Detect user intent and buying signals"""
        import time
        t_start = time.time()
        
        prompt = f"""Analyze this user message and determine their intent.

User message: "{user_message}"

Classify the intent as one of:
- INFORMATION_SEEKING: Just asking questions
- HIGH_INTEREST: Showing strong buying signals (pricing, demo, trial, contact)
- READY_TO_BUY: Ready to purchase or sign up
- SUPPORT: Needs help with existing product

Also rate the lead quality (LOW, MEDIUM, HIGH).

Respond in this exact format:
INTENT: [intent]
QUALITY: [quality]
REASON: [brief reason]
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = groq_service.chat_completion(
            messages,
            model="llama-3.1-8b-instant",  # Faster model for intent detection
            temperature=0.3,
            max_tokens=150
        )
        print(f"  ➡️ Intent LLM call [{(time.time()-t_start)*1000:.0f}ms]")
        
        # Parse response
        intent_data = self._parse_intent_response(response)
        return intent_data
    
    def _parse_intent_response(self, response: str) -> Dict:
        """Parse intent detection response"""
        lines = response.strip().split('\n')
        intent_data = {
            'intent': 'INFORMATION_SEEKING',
            'quality': 'LOW',
            'reason': ''
        }
        
        for line in lines:
            if line.startswith('INTENT:'):
                intent_data['intent'] = line.split(':', 1)[1].strip()
            elif line.startswith('QUALITY:'):
                intent_data['quality'] = line.split(':', 1)[1].strip()
            elif line.startswith('REASON:'):
                intent_data['reason'] = line.split(':', 1)[1].strip()
        
        return intent_data
    
    def should_capture_lead(
        self,
        message_count: int,
        intent_data: Dict,
        lead_already_captured: bool
    ) -> bool:
        """Determine if we should ask for contact info"""
        
        if lead_already_captured:
            return False
        
        # Capture after 2 messages OR if high interest detected
        if message_count >= 2:
            return True
        
        if intent_data.get('intent') in ['HIGH_INTEREST', 'READY_TO_BUY']:
            return True
        
        return False
    
    def generate_lead_capture_prompt(self, intent_data: Dict) -> str:
        """Generate natural lead capture message"""
        
        intent = intent_data.get('intent', 'INFORMATION_SEEKING')
        
        if intent == 'READY_TO_BUY':
            return "I'd love to help you get started! Could you share your name and email so I can send you the details?"
        elif intent == 'HIGH_INTEREST':
            return "I can provide you with more detailed information. What's your email address so I can send you everything you need?"
        else:
            return "I'm here to help! If you'd like me to follow up with more information, could you share your name and email?"


# Singleton instance
lead_capture_service = LeadCaptureService()
