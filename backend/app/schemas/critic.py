from typing import List, Optional
from pydantic import BaseModel, Field


class CriticVerdict(BaseModel):
    """
    Decision produced by the critic_node.
    If approved=False the drafting_node is invoked again with the feedback
    injected into the system prompt (max 2 revision loops).
    """

    approved: bool = Field(
        ...,
        description="True if the draft passes all brand guardrails.",
    )
    feedback: Optional[str] = Field(
        default=None,
        description="If approved=False: specific, actionable feedback for the drafter.",
    )
    violations: List[str] = Field(
        default_factory=list,
        description=(
            "List of violated rules e.g. "
            "['too_pushy', 'unverified_pricing_claim', 'off_brand_tone']"
        ),
    )
    revised_response: Optional[str] = Field(
        default=None,
        description=(
            "If the critic can fix the draft itself (minor edits), "
            "it may supply a revised version here. "
            "If present and approved=True, this is used as final_response."
        ),
    )
