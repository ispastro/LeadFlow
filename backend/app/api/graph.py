"""
graph.py — RevOps Graph API (Phase 6)

Three endpoints:

  POST /api/graph/invoke
    Primary chat entry point. Invokes the graph for a session.
    If the graph is interrupted at hitl_node, returns status=pending_approval.

  GET  /api/graph/state/{session_id}
    Returns the current checkpointed state for a session.
    Used by the dashboard to show live graph progress.

  POST /api/graph/approve/{session_id}
    HITL webhook. Injects the human decision into the checkpointed state
    and resumes graph execution from hitl_node.
    Protected by JWT (dashboard-only action).
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from app.api.auth import get_current_user
from app.db.leads import update_lead_approval
from app.graph.builder import get_graph

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class GraphInvokeRequest(BaseModel):
    session_id: str
    message: str
    # Optional pre-known lead info (e.g. from embedded widget form)
    lead_email: Optional[str] = None
    lead_name: Optional[str] = None


class GraphInvokeResponse(BaseModel):
    session_id: str
    response: str
    status: str                          # "complete" | "pending_approval" | "manual_review"
    conversation_state: Optional[str] = None
    qualification_score: Optional[int] = None
    qualification_tier: Optional[str] = None
    lead_captured: bool = False
    requires_human_approval: bool = False
    is_manual_review: bool = False
    elapsed_ms: float = 0


class ApprovalRequest(BaseModel):
    approved: bool
    reviewer: Optional[str] = None
    notes: Optional[str] = None


class ApprovalResponse(BaseModel):
    session_id: str
    approved: bool
    status: str                          # "resumed" | "manual_review"
    final_response: Optional[str] = None


# ---------------------------------------------------------------------------
# POST /api/graph/invoke  (public — same as /api/chat, no auth)
# ---------------------------------------------------------------------------

@router.post("/graph/invoke", response_model=GraphInvokeResponse)
async def graph_invoke(request: GraphInvokeRequest):
    """
    Invoke the RevOps graph for a session.

    - If the lead scores >= HITL_SCORE_THRESHOLD the graph is interrupted
      and this endpoint returns status='pending_approval'.
    - Otherwise returns status='complete' with the AI response.
    - All error paths return status='manual_review' with a safe fallback
      message — the lead is never discarded.
    """
    start = time.time()
    graph = get_graph()

    # Thread config — session_id is the LangGraph thread_id so every
    # conversation has its own isolated checkpoint stream.
    config = {"configurable": {"thread_id": request.session_id}}

    initial_state: Dict[str, Any] = {
        "session_id": request.session_id,
        "user_message": request.message,
        "critic_revision_count": 0,
        "is_manual_review": False,
        "lead_persisted": False,
        "email_captured": False,
    }
    if request.lead_email:
        initial_state["lead_email"] = request.lead_email
    if request.lead_name:
        initial_state["lead_name"] = request.lead_name

    try:
        # ainvoke returns the final state after graph completes or interrupts
        final_state = await graph.ainvoke(initial_state, config)
    except Exception as exc:
        logger.error("graph_invoke | unhandled error session=%s: %s", request.session_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Graph execution failed.")

    elapsed = (time.time() - start) * 1000

    # --- Detect interrupt (HITL pending) ------------------------------------
    # LangGraph signals an interrupt by having the graph stop at hitl_node.
    # We detect this by checking the current_node in state.
    current_node = final_state.get("current_node", "")
    score = final_state.get("qualification_score")
    is_interrupted = (
        current_node == "input_node"   # graph stopped before hitl runs
        or (score is not None and score >= 90 and not final_state.get("final_response"))
    )

    # Cleaner: check if graph stopped before reaching deliver/manual_review
    reached_terminal = current_node in ("deliver_node", "manual_review_node")
    if not reached_terminal and score is not None and score >= 90:
        is_interrupted = True

    if is_interrupted:
        logger.info(
            "graph_invoke | INTERRUPTED at hitl session=%s score=%s",
            request.session_id, score,
        )
        return GraphInvokeResponse(
            session_id=request.session_id,
            response=(
                "Your query has been escalated to our team for a personalised response. "
                "We'll follow up with you shortly."
            ),
            status="pending_approval",
            qualification_score=score,
            qualification_tier=final_state.get("qualification_tier"),
            lead_captured=bool(final_state.get("lead_email")),
            requires_human_approval=True,
            elapsed_ms=round(elapsed, 1),
        )

    # --- Normal completion --------------------------------------------------
    final_response = final_state.get("final_response") or ""
    is_manual = final_state.get("is_manual_review", False)

    logger.info(
        "graph_invoke | session=%s node=%s score=%s manual=%s elapsed=%.0fms",
        request.session_id, current_node, score, is_manual, elapsed,
    )

    return GraphInvokeResponse(
        session_id=request.session_id,
        response=final_response,
        status="manual_review" if is_manual else "complete",
        conversation_state=final_state.get("legacy_stage"),
        qualification_score=score,
        qualification_tier=final_state.get("qualification_tier"),
        lead_captured=final_state.get("lead_persisted", False),
        requires_human_approval=False,
        is_manual_review=is_manual,
        elapsed_ms=round(elapsed, 1),
    )


# ---------------------------------------------------------------------------
# GET /api/graph/state/{session_id}  (protected)
# ---------------------------------------------------------------------------

@router.get("/graph/state/{session_id}")
async def get_graph_state(
    session_id: str,
    _: dict = Depends(get_current_user),
):
    """
    Return the current checkpointed GraphState for a session.
    Useful for the dashboard to display live qualification scores,
    enrichment data, and HITL status.
    """
    graph = get_graph()
    config = {"configurable": {"thread_id": session_id}}

    try:
        snapshot = await graph.aget_state(config)
    except Exception as exc:
        logger.error("get_graph_state | session=%s error: %s", session_id, exc)
        raise HTTPException(status_code=404, detail="No state found for this session.")

    if not snapshot or not snapshot.values:
        raise HTTPException(status_code=404, detail="No state found for this session.")

    state = snapshot.values
    return {
        "session_id": session_id,
        "current_node": state.get("current_node"),
        "legacy_stage": state.get("legacy_stage"),
        "lead_email": state.get("lead_email"),
        "lead_name": state.get("lead_name"),
        "qualification_score": state.get("qualification_score"),
        "qualification_tier": state.get("qualification_tier"),
        "qualification_reasoning": state.get("qualification_reasoning"),
        "intent_signals": state.get("intent_signals"),
        "enrichment": {
            "company_name": state.get("company_name"),
            "company_size": state.get("company_size"),
            "company_industry": state.get("company_industry"),
            "lead_role": state.get("lead_role"),
            "source": state.get("enrichment_source"),
        },
        "critic_approved": state.get("critic_approved"),
        "critic_revision_count": state.get("critic_revision_count", 0),
        "requires_human_approval": state.get("requires_human_approval", False),
        "human_approved": state.get("human_approved"),
        "is_manual_review": state.get("is_manual_review", False),
        "error": state.get("error"),
    }


# ---------------------------------------------------------------------------
# POST /api/graph/approve/{session_id}  (protected — dashboard only)
# ---------------------------------------------------------------------------

@router.post("/graph/approve/{session_id}", response_model=ApprovalResponse)
async def approve_lead(
    session_id: str,
    request: ApprovalRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    HITL approval endpoint.

    1. Injects the human decision into the checkpointed graph state.
    2. Resumes the graph from hitl_node.
    3. Updates the lead DB record with the reviewer's decision.
    4. Returns the final AI response (for display in the dashboard).
    """
    graph = get_graph()
    config = {"configurable": {"thread_id": session_id}}
    reviewer = current_user.get("sub", "unknown")

    logger.info(
        "approve_lead | session=%s approved=%s reviewer=%s notes='%s'",
        session_id, request.approved, reviewer, request.notes or "",
    )

    # Step 1: Inject human decision into checkpointed state
    try:
        await graph.aupdate_state(
            config,
            {
                "human_approved": request.approved,
                "human_reviewer": reviewer,
                "human_notes": request.notes,
                # Clear the interrupt route so the graph can continue
                "route_to": "deliver" if request.approved else "manual_review",
            },
        )
    except Exception as exc:
        logger.error("approve_lead | state update failed session=%s: %s", session_id, exc)
        raise HTTPException(status_code=500, detail="Failed to update graph state.")

    # Step 2: Resume graph execution (pass None as input — uses checkpointed state)
    try:
        final_state = await graph.ainvoke(None, config)
    except Exception as exc:
        logger.error("approve_lead | graph resume failed session=%s: %s", session_id, exc)
        raise HTTPException(status_code=500, detail="Failed to resume graph execution.")

    # Step 3: Update lead DB record with reviewer decision
    conv_id = final_state.get("conversation_id")
    if conv_id:
        try:
            update_lead_approval(
                conversation_id=conv_id,
                human_approved=request.approved,
                human_reviewer=reviewer,
                human_notes=request.notes,
            )
        except Exception as exc:
            logger.warning("approve_lead | DB update failed (non-fatal): %s", exc)

    # Step 4: Return result
    is_manual = final_state.get("is_manual_review", False)
    final_response = final_state.get("final_response", "")
    status = "manual_review" if (is_manual or not request.approved) else "resumed"

    return ApprovalResponse(
        session_id=session_id,
        approved=request.approved,
        status=status,
        final_response=final_response,
    )
