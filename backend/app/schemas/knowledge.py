"""
Knowledge base Pydantic models.
"""
from pydantic import BaseModel
from typing import Optional, Dict


class KnowledgeCreate(BaseModel):
    title: str
    content: str
    category: str
    source: Optional[str] = "manual"
    metadata: Optional[Dict] = {}


class KnowledgeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    metadata: Optional[Dict] = None


class KnowledgeResponse(BaseModel):
    id: str
    business_id: str
    title: str
    content: str
    category: str
    source: str
    metadata: Dict
    created_at: str
    updated_at: str


class KnowledgeSyncResponse(BaseModel):
    success: bool
    documents_synced: int
    message: str
