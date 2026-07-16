import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.db.sqlite_db import get_db_connection, from_json, to_json

logger = logging.getLogger(__name__)

DEFAULT_BUSINESS_ID = "default"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_all_knowledge(business_id: str = DEFAULT_BUSINESS_ID) -> List[Dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, content, category, source, metadata, created_at, updated_at FROM knowledge_documents ORDER BY created_at DESC"
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_knowledge_by_id(knowledge_id: str) -> Optional[Dict]:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT id, title, content, category, source, metadata, created_at, updated_at FROM knowledge_documents WHERE id=?",
            (knowledge_id,),
        ).fetchone()
    return _row_to_dict(row) if row else None


def create_knowledge(business_id: str, title: str, content: str, category: str,
                     source: str = "manual", metadata: Dict = None) -> str:
    kid = str(uuid.uuid4())
    now = _utcnow()
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO knowledge_documents (id, title, content, category, source, metadata, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
            (kid, title, content, category, source, to_json(metadata or {}), now, now),
        )
        conn.commit()
    return kid


def update_knowledge(knowledge_id: str, title: str = None, content: str = None,
                     category: str = None, source: str = None, metadata: Dict = None) -> bool:
    sets, vals = [], []
    for col, val in [("title", title), ("content", content), ("category", category), ("source", source)]:
        if val is not None:
            sets.append(f"{col}=?")
            vals.append(val)
    if metadata is not None:
        sets.append("metadata=?")
        vals.append(to_json(metadata))
    sets.append("updated_at=?")
    vals.append(_utcnow())
    vals.append(knowledge_id)
    with get_db_connection() as conn:
        cur = conn.execute(f"UPDATE knowledge_documents SET {', '.join(sets)} WHERE id=?", vals)
        conn.commit()
        return cur.rowcount > 0


def delete_knowledge(knowledge_id: str) -> bool:
    with get_db_connection() as conn:
        cur = conn.execute("DELETE FROM knowledge_documents WHERE id=?", (knowledge_id,))
        conn.commit()
        return cur.rowcount > 0


def count_knowledge(business_id: str = DEFAULT_BUSINESS_ID) -> int:
    with get_db_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM knowledge_documents").fetchone()[0]


def _row_to_dict(row) -> Dict:
    return {
        "id": row["id"],
        "business_id": DEFAULT_BUSINESS_ID,
        "title": row["title"],
        "content": row["content"],
        "category": row["category"],
        "source": row["source"],
        "metadata": from_json(row["metadata"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }
