from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime


class LeadCreate(BaseModel):
    conversation_id: str
    email: EmailStr
    name: Optional[str] = None
    intent: Optional[str] = None
    budget: Optional[str] = None
    metadata: Optional[Dict] = {}


class LeadResponse(BaseModel):
    id: str
    conversation_id: str
    email: str
    name: Optional[str]
    intent: Optional[str]
    budget: Optional[str]
    metadata: Dict
    captured_at: str
