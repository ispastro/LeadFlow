from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class GraphState(TypedDict, total=False):
    # -----------------------------------------------------------------------
    # Input (populated by input_node)
    # -----------------------------------------------------------------------
    session_id: str
    user_message: str                      # sanitised user input
    conversation_id: str
    conversation_history: List[Dict]       # [{role, content}, ...]
    message_count: int

    # -----------------------------------------------------------------------
    # LangChain message list (for LLM calls with full context)
    # Uses add_messages reducer — appends rather than replaces
    # -----------------------------------------------------------------------
    messages: Annotated[List[BaseMessage], add_messages]

    # -----------------------------------------------------------------------
    # Enrichment (populated by enrichment_node)
    # -----------------------------------------------------------------------
    lead_email: Optional[str]
    lead_name: Optional[str]
    company_name: Optional[str]
    company_size: Optional[str]            # "1-10" | "11-50" | "51-200" | "200+"
    company_industry: Optional[str]
    lead_role: Optional[str]               # inferred from email/domain
    enrichment_source: Optional[str]       # "mock" | "clearbit" | "apollo"

    # -----------------------------------------------------------------------
    # Qualification (populated by qualification_node)
    # -----------------------------------------------------------------------
    qualification_score: Optional[int]     # 0-100
    qualification_reasoning: Optional[str]
    qualification_tier: Optional[str]      # "hot" | "warm" | "cold"
    intent_signals: Optional[List[str]]    # ["asked_pricing", "mentioned_demo", ...]
    disqualification_reason: Optional[str] # set if score < 20

    # -----------------------------------------------------------------------
    # Drafting (populated by drafting_node)
    # -----------------------------------------------------------------------
    draft_response: Optional[str]
    rag_sources: Optional[List[str]]       # source titles used

    # -----------------------------------------------------------------------
    # Critic (populated by critic_node)
    # -----------------------------------------------------------------------
    critic_approved: Optional[bool]
    critic_feedback: Optional[str]         # reason if rejected
    critic_revision_count: int             # how many revision loops taken
    final_response: Optional[str]

    # -----------------------------------------------------------------------
    # HITL (populated by hitl_node)
    # -----------------------------------------------------------------------
    requires_human_approval: Optional[bool]
    human_approved: Optional[bool]         # None = pending, True/False = decided
    human_reviewer: Optional[str]          # who approved/rejected
    human_notes: Optional[str]

    # -----------------------------------------------------------------------
    # Routing / control
    # -----------------------------------------------------------------------
    current_node: Optional[str]            # last node that ran (for debugging)
    route_to: Optional[str]               # explicit next-node override
    error: Optional[str]                  # last error message
    error_node: Optional[str]             # which node threw
    is_manual_review: bool                 # True = routed to manual_review

    # -----------------------------------------------------------------------
    # Lead persistence (populated by deliver_node)
    # -----------------------------------------------------------------------
    lead_id: Optional[int]
    lead_persisted: bool

    # -----------------------------------------------------------------------
    # Legacy compatibility (old state-machine stage)
    # -----------------------------------------------------------------------
    legacy_stage: Optional[str]
    email_captured: bool
