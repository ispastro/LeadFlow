import logging
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

logger = logging.getLogger(__name__)

_checkpointer: AsyncSqliteSaver | None = None


def get_checkpointer() -> AsyncSqliteSaver:
    if _checkpointer is None:
        raise RuntimeError("Checkpointer not initialised.")
    return _checkpointer


def set_checkpointer(cp: AsyncSqliteSaver) -> None:
    global _checkpointer
    _checkpointer = cp
