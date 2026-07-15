"""
Postgres-backed LangGraph checkpointer.

LangGraph's AsyncPostgresSaver persists the full graph state after every node,
giving us crash-resilience and the ability to resume interrupted graphs
(critical for HITL approval flows).

The checkpointer creates its own tables on first use:
  - checkpoints
  - checkpoint_blobs
  - checkpoint_writes

We expose a single async context manager `get_checkpointer()` that the
graph builder uses at startup, and a sync `get_sync_checkpointer()` used
in tests or scripts.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from config import settings

logger = logging.getLogger(__name__)

# Module-level singleton — initialised once during app lifespan
_checkpointer: AsyncPostgresSaver | None = None


async def init_checkpointer() -> AsyncPostgresSaver:
    """
    Create and set up the AsyncPostgresSaver.
    Called once from main.py lifespan startup.
    """
    global _checkpointer
    if _checkpointer is not None:
        return _checkpointer

    logger.info("Initialising Postgres checkpointer...")
    cp = AsyncPostgresSaver.from_conn_string(settings.database_url)
    # Creates checkpoints / checkpoint_blobs / checkpoint_writes tables
    await cp.setup()
    _checkpointer = cp
    logger.info("Postgres checkpointer ready")
    return _checkpointer


def get_checkpointer() -> AsyncPostgresSaver:
    """
    Return the already-initialised checkpointer.
    Raises RuntimeError if called before init_checkpointer().
    """
    if _checkpointer is None:
        raise RuntimeError(
            "Checkpointer not initialised. "
            "Ensure init_checkpointer() was awaited during app startup."
        )
    return _checkpointer
