from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(..., min_length=1)
    user_email: Optional[str] = None
    user_name: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    should_capture_lead: bool = False
    lead_captured: bool = False
    conversation_state: str


class MessageHistory(BaseModel):
    role: str
    content: str
    timestamp: str
