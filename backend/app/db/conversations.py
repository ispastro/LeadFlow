import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from app.db.sqlite_db import get_db_connection

logger = logging.getLogger(__name__)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_conversation(session_id: str) -> Dict:
    conv_id = str(uuid.uuid4())
    now = _utcnow()
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO conversations (id, session_id, stage, email_captured, created_at, updated_at)
            VALUES (?, ?, 'NEW', 0, ?, ?)
            """,
            (conv_id, session_id, now, now),
        )
        conn.commit()
    return {
        "id": conv_id,
        "session_id": session_id,
        "stage": "NEW",
        "email_captured": False,
        "created_at": now,
        "updated_at": now,
    }


def get_conversation_by_session(session_id: str) -> Optional[Dict]:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT id, session_id, stage, email_captured, created_at, updated_at FROM conversations WHERE session_id = ?",
            (session_id,),
        ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "session_id": row["session_id"],
        "stage": row["stage"],
        "email_captured": bool(row["email_captured"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def get_or_create_conversation(session_id: str) -> Dict:
    conv = get_conversation_by_session(session_id)
    return conv if conv else create_conversation(session_id)


def update_conversation_stage(conversation_id: str, stage: str, email_captured: bool = None) -> None:
    now = _utcnow()
    with get_db_connection() as conn:
        if email_captured is not None:
            conn.execute(
                "UPDATE conversations SET stage=?, email_captured=?, updated_at=? WHERE id=?",
                (stage, int(email_captured), now, conversation_id),
            )
        else:
            conn.execute(
                "UPDATE conversations SET stage=?, updated_at=? WHERE id=?",
                (stage, now, conversation_id),
            )
        conn.commit()


def update_conversation_timestamp(conversation_id: str) -> None:
    with get_db_connection() as conn:
        conn.execute(
            "UPDATE conversations SET updated_at=? WHERE id=?",
            (_utcnow(), conversation_id),
        )
        conn.commit()
