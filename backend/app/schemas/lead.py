"""
LeadRecord — canonical Pydantic model for a captured lead.
Used for DB persistence and API responses.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class LeadRecord(BaseModel):
    id: Optional[int] = None
    conversation_id: str
    business_id: Optional[str] = None
    email: EmailStr
    name: Optional[str] = None
    intent_trigger: Optional[str] = None

    # Qualification data
    qualification_score: Optional[int] = Field(default=None, ge=0, le=100)
    qualification_tier: Optional[str] = None   # hot | warm | cold
    intent_signals: Optional[List[str]] = None
    recommended_action: Optional[str] = None

    # Enrichment data
    company_name: Optional[str] = None
    company_size: Optional[str] = None
    company_industry: Optional[str] = None
    lead_role: Optional[str] = None
    enrichment_source: Optional[str] = None

    # HITL
    requires_human_approval: bool = False
    human_approved: Optional[bool] = None
    human_reviewer: Optional[str] = None
    human_notes: Optional[str] = None

    # Meta
    quality: str = "MEDIUM"
    captured_via: str = "graph"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    captured_at: Optional[datetime] = None
    is_manual_review: bool = False

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Legacy response shape — used by /api/leads endpoint
# ---------------------------------------------------------------------------
class LeadResponse(BaseModel):
    """Flat response model for the dashboard leads list."""
    id: str
    conversation_id: str
    email: str
    name: Optional[str] = None
    intent: Optional[str] = None
    budget: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    captured_at: Optional[str] = None


class LeadCreate(BaseModel):
    """Legacy lead creation payload."""
    conversation_id: str
    email: str
    name: Optional[str] = None
    intent: Optional[str] = None
    budget: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
