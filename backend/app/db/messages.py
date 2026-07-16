import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List

from app.db.sqlite_db import get_db_connection

logger = logging.getLogger(__name__)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_message(conversation_id: str, role: str, content: str, **_) -> Dict:
    msg_id = str(uuid.uuid4())
    now = _utcnow()
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (msg_id, conversation_id, role, content, now),
        )
        conn.commit()
    return {"id": msg_id, "conversation_id": conversation_id, "role": role, "content": content, "created_at": now}


def get_conversation_messages(conversation_id: str) -> List[Dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT id, conversation_id, role, content, created_at FROM messages WHERE conversation_id=? ORDER BY created_at",
            (conversation_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_conversation_history(conversation_id: str, limit: int = 10) -> List[Dict[str, str]]:
    messages = get_conversation_messages(conversation_id)
    recent = messages[-limit:] if len(messages) > limit else messages
    return [{"role": m["role"], "content": m["content"]} for m in recent]


def count_user_messages(conversation_id: str) -> int:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE conversation_id=? AND role='user'",
            (conversation_id,),
        ).fetchone()
    return row[0] if row else 0
