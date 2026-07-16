import logging
import os
from typing import Literal

from langgraph.graph import StateGraph, END

from app.schemas.graph_state import GraphState
from app.graph.nodes.input_node import input_node
from app.graph.nodes.enrichment_node import enrichment_node
from app.graph.nodes.qualification_node import qualification_node
from app.graph.nodes.drafting_node import drafting_node
from app.graph.nodes.critic_node import critic_node
from app.graph.nodes.hitl_node import hitl_node
from app.graph.nodes.deliver_node import deliver_node
from app.graph.nodes.manual_review_node import manual_review_node
from config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LangSmith environment setup — must be done before any LangChain import
# ---------------------------------------------------------------------------
def _configure_langsmith() -> None:
    if settings.langsmith_enabled:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
        os.environ["LANGCHAIN_ENDPOINT"] = settings.langchain_endpoint
        logger.info(
            "LangSmith tracing ENABLED → project='%s'", settings.langchain_project
        )
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        logger.info("LangSmith tracing DISABLED (set LANGCHAIN_API_KEY + LANGCHAIN_TRACING_V2=true to enable)")


# ---------------------------------------------------------------------------
# Edge routing functions
# ---------------------------------------------------------------------------

def _route_after_input(
    state: GraphState,
) -> Literal["enrichment_node", "manual_review_node"]:
    """After input: proceed to enrichment, or fail-fast to manual review."""
    if state.get("route_to") == "manual_review":
        return "manual_review_node"
    return "enrichment_node"


def _route_after_qualification(
    state: GraphState,
) -> Literal["hitl_node", "drafting_node", "manual_review_node"]:
    """
    After qualification:
      - Explicit manual_review override (qualification failed)
      - Score >= threshold → HITL gate
      - Otherwise → drafting
    """
    if state.get("route_to") == "manual_review":
        return "manual_review_node"

    score = state.get("qualification_score")
    if score is not None and score >= settings.hitl_score_threshold:
        logger.info(
            "router | score=%d >= threshold=%d → hitl_node",
            score, settings.hitl_score_threshold,
        )
        return "hitl_node"

    return "drafting_node"


def _route_after_hitl(
    state: GraphState,
) -> Literal["drafting_node", "manual_review_node"]:
    """After HITL decision: approved → drafting, rejected → manual_review."""
    route = state.get("route_to")
    if route == "manual_review":
        return "manual_review_node"
    return "drafting_node"


def _route_after_critic(
    state: GraphState,
) -> Literal["deliver_node", "drafting_node", "manual_review_node"]:
    """
    After critic verdict:
      - approved → deliver
      - rejected, route_to=drafting_node → revision loop
      - rejected, route_to=manual_review → give up gracefully
    """
    if state.get("critic_approved"):
        return "deliver_node"

    route = state.get("route_to")
    if route == "manual_review":
        return "manual_review_node"
    if route == "drafting_node":
        return "drafting_node"

    # Default safe fallback
    return "manual_review_node"


# ---------------------------------------------------------------------------
# Graph factory
# ---------------------------------------------------------------------------

def build_graph(checkpointer) -> StateGraph:
    """
    Assemble and compile the RevOps StateGraph.

    Args:
        checkpointer: An initialised AsyncPostgresSaver instance.

    Returns:
        A compiled LangGraph CompiledGraph ready for async invocation.
    """
    _configure_langsmith()

    builder = StateGraph(GraphState)

    # ── Register nodes ────────────────────────────────────────────────────
    builder.add_node("input_node",          input_node)
    builder.add_node("enrichment_node",     enrichment_node)
    builder.add_node("qualification_node",  qualification_node)
    builder.add_node("hitl_node",           hitl_node)
    builder.add_node("drafting_node",       drafting_node)
    builder.add_node("critic_node",         critic_node)
    builder.add_node("deliver_node",        deliver_node)
    builder.add_node("manual_review_node",  manual_review_node)

    # ── Entry point ───────────────────────────────────────────────────────
    builder.set_entry_point("input_node")

    # ── Edges ─────────────────────────────────────────────────────────────

    # input → enrichment or manual_review
    builder.add_conditional_edges(
        "input_node",
        _route_after_input,
        {
            "enrichment_node":    "enrichment_node",
            "manual_review_node": "manual_review_node",
        },
    )

    # enrichment → qualification (always proceeds; enrichment is fail-safe)
    builder.add_edge("enrichment_node", "qualification_node")

    # qualification → hitl | drafting | manual_review
    builder.add_conditional_edges(
        "qualification_node",
        _route_after_qualification,
        {
            "hitl_node":          "hitl_node",
            "drafting_node":      "drafting_node",
            "manual_review_node": "manual_review_node",
        },
    )

    # hitl → drafting | manual_review  (resumes after interrupt())
    builder.add_conditional_edges(
        "hitl_node",
        _route_after_hitl,
        {
            "drafting_node":      "drafting_node",
            "manual_review_node": "manual_review_node",
        },
    )

    # drafting → critic (always)
    builder.add_edge("drafting_node", "critic_node")

    # critic → deliver | drafting (revision) | manual_review
    builder.add_conditional_edges(
        "critic_node",
        _route_after_critic,
        {
            "deliver_node":       "deliver_node",
            "drafting_node":      "drafting_node",
            "manual_review_node": "manual_review_node",
        },
    )

    # Terminal nodes
    builder.add_edge("deliver_node",       END)
    builder.add_edge("manual_review_node", END)

    # ── Compile with Postgres checkpointer ───────────────────────────────
    graph = builder.compile(
        checkpointer=checkpointer,
        # Interrupt BEFORE hitl_node so the state is checkpointed
        # before the node tries to call interrupt() internally.
        interrupt_before=["hitl_node"],
    )

    logger.info("RevOps graph compiled successfully")
    return graph


# ---------------------------------------------------------------------------
# Module-level singleton — populated by main.py lifespan
# ---------------------------------------------------------------------------
_graph = None


def get_graph():
    """Return the compiled graph. Raises if not yet initialised."""
    if _graph is None:
        raise RuntimeError(
            "Graph not initialised. Ensure build_graph() was called during app startup."
        )
    return _graph


def set_graph(graph) -> None:
    global _graph
    _graph = graph
