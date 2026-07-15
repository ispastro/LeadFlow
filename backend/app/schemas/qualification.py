"""
Structured output schemas for the qualification agent.
Using Pydantic so the LLM is forced to return valid JSON that matches this shape.
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class QualificationResult(BaseModel):
    """
    Deterministic qualification output produced by the qualification_node.
    The LLM is instructed to return ONLY a JSON object matching this schema.
    """

    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Lead quality score from 0 (junk) to 100 (perfect ICP match).",
    )
    tier: str = Field(
        ...,
        description="hot | warm | cold",
    )
    reasoning: str = Field(
        ...,
        description="1-2 sentence explanation of why this score was assigned.",
    )
    intent_signals: List[str] = Field(
        default_factory=list,
        description="List of observed intent signals e.g. ['asked_pricing', 'mentioned_demo']",
    )
    disqualification_reason: Optional[str] = Field(
        default=None,
        description="If score < 20, the primary reason this lead is disqualified.",
    )
    recommended_action: str = Field(
        ...,
        description="next_step: 'nurture' | 'demo_offer' | 'direct_sales' | 'disqualify' | 'manual_review'",
    )

    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v: str) -> str:
        allowed = {"hot", "warm", "cold"}
        v = v.lower().strip()
        if v not in allowed:
            return "warm"   # safe default
        return v

    @field_validator("recommended_action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        allowed = {"nurture", "demo_offer", "direct_sales", "disqualify", "manual_review"}
        v = v.lower().strip()
        return v if v in allowed else "manual_review"
