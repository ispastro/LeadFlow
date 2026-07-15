"""
hitl_node — Phase 5 (Human-in-the-Loop Governance)

Triggered when qualification_score >= HITL_SCORE_THRESHOLD (default 90).

Uses LangGraph's `interrupt()` to pause the graph execution at this node.
The graph state is checkpointed to Postgres. Execution resumes only when
the approval API endpoint calls `graph.update_state()` with the human decision.

Approval flow:
  POST /api/graph/approve/{thread_id}  { "approved": true/false, "reviewer": "...", "notes": "..." }
    → graph.update_state(config, {"human_approved": True/False, ...})
    → graph.invoke(None, config)   ← resumes from hitl_node
    → routes to deliver_node (approved) or manual_review_node (rejected)
"""
from __future__ import annotations

import logging

from langgraph.types import interrupt

from app.schemas.graph_state import GraphState
from config import settings

logger = logging.getLogger(__name__)


def hitl_node(state: GraphState) -> GraphState:
    """
    Pause graph for human approval on high-value leads.

    On first entry: interrupt() suspends execution and returns control
    to the caller. The graph is checkpointed.

    On resume (after update_state): human_approved will be set.
    Route accordingly.
    """
    score = state.get("qualification_score", 0)
    session_id = state.get("session_id", "unknown")
    email = state.get("lead_email", "unknown")

    # If we already have a human decision (resumed after interrupt), route now
    human_approved = state.get("human_approved")
    if human_approved is not None:
        if human_approved:
            logger.info(
                "hitl_node | APPROVED by %s for session=%s email=%s score=%d",
                state.get("human_reviewer", "unknown"),
                session_id, email, score,
            )
            return {
                **state,
                "route_to": "deliver",
                "current_node": "hitl_node",
            }
        else:
            logger.info(
                "hitl_node | REJECTED by %s for session=%s email=%s score=%d notes='%s'",
                state.get("human_reviewer", "unknown"),
                session_id, email, score,
                state.get("human_notes", ""),
            )
            return {
                **state,
                "route_to": "manual_review",
                "error": "hitl_rejected",
                "current_node": "hitl_node",
            }

    # First entry — interrupt and wait for human signal
    logger.info(
        "hitl_node | INTERRUPTING for human approval session=%s email=%s score=%d",
        session_id, email, score,
    )

    # interrupt() raises a special LangGraph exception that checkpoints the
    # state and suspends execution. The value passed is surfaced to the caller
    # via the graph's stream/invoke return.
    interrupt({
        "reason": "high_value_lead_requires_approval",
        "session_id": session_id,
        "lead_email": email,
        "qualification_score": score,
        "qualification_tier": state.get("qualification_tier"),
        "message": (
            f"Lead {email} scored {score}/100. "
            f"Approve to route to sales, reject to send to manual review."
        ),
    })

    # Execution never reaches here on first entry.
    # This return is only reached after resume — but human_approved check above
    # handles that case, so this is truly unreachable. Kept for type safety.
    return {**state, "current_node": "hitl_node"}
