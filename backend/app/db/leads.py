import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.db.sqlite_db import get_db_connection, from_json, to_json

logger = logging.getLogger(__name__)

_COLS = "id, conversation_id, email, name, intent_trigger, quality, captured_via, metadata, captured_at"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_dict(row) -> Dict:
    return {
        "id": row["id"],
        "conversation_id": row["conversation_id"],
        "business_id": None,
        "email": row["email"],
        "name": row["name"],
        "intent": row["intent_trigger"],
        "quality": row["quality"],
        "captured_via": row["captured_via"],
        "metadata": from_json(row["metadata"]),
        "captured_at": row["captured_at"],
    }


def upsert_lead(
    *,
    conversation_id: str,
    email: str,
    name: Optional[str] = None,
    intent_trigger: Optional[str] = None,
    qualification_score: Optional[int] = None,
    qualification_tier: Optional[str] = None,
    intent_signals: Optional[List[str]] = None,
    recommended_action: Optional[str] = None,
    company_name: Optional[str] = None,
    company_size: Optional[str] = None,
    company_industry: Optional[str] = None,
    lead_role: Optional[str] = None,
    enrichment_source: Optional[str] = None,
    requires_human_approval: bool = False,
    human_approved: Optional[bool] = None,
    human_reviewer: Optional[str] = None,
    human_notes: Optional[str] = None,
    is_manual_review: bool = False,
    quality: str = "MEDIUM",
    metadata: Optional[Dict] = None,
    business_id: Optional[str] = None,
) -> str:
    if qualification_score is not None:
        quality = "HIGH" if qualification_score >= 80 else "MEDIUM" if qualification_score >= 50 else "LOW"

    meta = dict(metadata or {})
    meta.update({
        "qualification_score": qualification_score,
        "qualification_tier": qualification_tier,
        "intent_signals": intent_signals or [],
        "recommended_action": recommended_action,
        "company_name": company_name,
        "company_size": company_size,
        "company_industry": company_industry,
        "lead_role": lead_role,
        "enrichment_source": enrichment_source,
        "requires_human_approval": requires_human_approval,
        "human_approved": human_approved,
        "human_reviewer": human_reviewer,
        "human_notes": human_notes,
        "is_manual_review": is_manual_review,
    })

    now = _utcnow()
    with get_db_connection() as conn:
        existing = conn.execute(
            "SELECT id, metadata FROM leads WHERE conversation_id=?", (conversation_id,)
        ).fetchone()

        if existing:
            # Merge metadata
            old_meta = from_json(existing["metadata"])
            old_meta.update(meta)
            conn.execute(
                """UPDATE leads SET email=?, name=COALESCE(?, name),
                   intent_trigger=COALESCE(?, intent_trigger),
                   quality=?, metadata=?, captured_via=?
                   WHERE conversation_id=?""",
                (email, name, intent_trigger or "other", quality, to_json(old_meta), "graph", conversation_id),
            )
            conn.commit()
            return existing["id"]
        else:
            lead_id = str(uuid.uuid4())
            conn.execute(
                f"INSERT INTO leads ({_COLS}) VALUES (?,?,?,?,?,?,?,?,?)",
                (lead_id, conversation_id, email, name, intent_trigger or "other",
                 quality, "graph", to_json(meta), now),
            )
            conn.commit()
            logger.info("upsert_lead | conversation=%s lead_id=%s", conversation_id, lead_id)
            return lead_id


def update_lead_approval(
    *, conversation_id: str, human_approved: bool,
    human_reviewer: Optional[str] = None, human_notes: Optional[str] = None,
) -> bool:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT id, metadata FROM leads WHERE conversation_id=?", (conversation_id,)
        ).fetchone()
        if not row:
            return False
        meta = from_json(row["metadata"])
        meta.update({"human_approved": human_approved, "human_reviewer": human_reviewer, "human_notes": human_notes})
        conn.execute(
            "UPDATE leads SET metadata=? WHERE conversation_id=?",
            (to_json(meta), conversation_id),
        )
        conn.commit()
        return True


def create_lead(conversation_id: str, email: str, name: str = None,
                intent: str = None, budget: str = None, metadata: Dict = None) -> str:
    return upsert_lead(conversation_id=conversation_id, email=email, name=name,
                       intent_trigger=intent, metadata=metadata or {})


def get_lead_by_id(lead_id: str) -> Optional[Dict]:
    with get_db_connection() as conn:
        row = conn.execute(f"SELECT {_COLS} FROM leads WHERE id=?", (lead_id,)).fetchone()
    return _row_to_dict(row) if row else None


def get_lead_by_conversation(conversation_id: str) -> Optional[Dict]:
    with get_db_connection() as conn:
        row = conn.execute(
            f"SELECT {_COLS} FROM leads WHERE conversation_id=?", (conversation_id,)
        ).fetchone()
    return _row_to_dict(row) if row else None


def lead_exists(conversation_id: str) -> bool:
    return get_lead_by_conversation(conversation_id) is not None


def get_all_leads() -> List[Dict]:
    with get_db_connection() as conn:
        rows = conn.execute(f"SELECT {_COLS} FROM leads ORDER BY captured_at DESC").fetchall()
    return [_row_to_dict(r) for r in rows]


def get_leads_pending_approval() -> List[Dict]:
    leads = get_all_leads()
    return [
        l for l in leads
        if l["metadata"].get("requires_human_approval") and l["metadata"].get("human_approved") is None
    ]
