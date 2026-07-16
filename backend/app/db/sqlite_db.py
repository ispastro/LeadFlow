import json
import logging
import sqlite3
import threading
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger(__name__)

_DB_PATH = "leadflow.db"
_local = threading.local()


def set_db_path(path: str) -> None:
    global _DB_PATH
    _DB_PATH = path


def get_db_path() -> str:
    return _DB_PATH


@contextmanager
def get_db_connection():
    """
    Thread-safe SQLite connection context manager.
    Each thread gets its own connection (SQLite requirement).
    Connections are cached per-thread and reused across calls.
    """
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(
            _DB_PATH,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")
        _local.conn.execute("PRAGMA foreign_keys=ON")

    conn = _local.conn
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise


def close_connections() -> None:
    """Called on app shutdown."""
    if hasattr(_local, "conn") and _local.conn:
        _local.conn.close()
        _local.conn = None


# ---------------------------------------------------------------------------
# JSON helpers — replaces psycopg2.extras.Json
# ---------------------------------------------------------------------------

def to_json(value: Any) -> str:
    if value is None:
        return "{}"
    if isinstance(value, str):
        return value
    return json.dumps(value)


def from_json(value: Any) -> Any:
    if value is None:
        return {}
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return {}
