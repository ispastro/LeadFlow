"""
Lead persistence layer.

All write operations are idempotent:
  - upsert_lead uses ON CONFLICT (conversation_id) DO UPDATE
    so running it twice with the same conversation_id is safe.
  - create_lead is kept for backwards compatibility with the old chat endpoint.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Optional

import psycopg2.extras

from app.db.pg_direct import get_db_connection

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Column list shared across all SELECT queries — single source of truth
# ---------------------------------------------------------------------------
_SELECT_COLS = """
    id, conversation_id, business_id, email, name,
    intent_trigger, quality, captured_via, metadata, captured_at
"""


def _row_to_dict(row) -> Dict:
    return {
        "id": str(row[0]),
        "conversation_id": str(row[1]),
        "business_id": str(row[2]) if row[2] else None,
        "email": row[3],
        "name": row[4],
        "intent": row[5],
        "quality": row[6],
        "captured_via": row[7],
        "metadata": row[8] or {},
        "captured_at": row[9].isoformat() if row[9] else None,
    }


# ---------------------------------------------------------------------------
# Idempotent upsert (used by the RevOps graph deliver_node)
# ---------------------------------------------------------------------------
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
) -> int:
    """
    Insert or update a lead by conversation_id.
    Safe to call multiple times — idempotent via ON CONFLICT.
    Returns the lead id.
    """
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

    # Determine quality tier from score if not explicitly set
    if qualification_score is not None:
        if qualification_score >= 80:
            quality = "HIGH"
        elif qualification_score >= 50:
            quality = "MEDIUM"
        else:
            quality = "LOW"

    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            # Resolve business_id from conversation if not supplied
            if not business_id:
                cur.execute(
                    "SELECT business_id FROM conversations WHERE id = %s",
                    (conversation_id,),
                )
                result = cur.fetchone()
                business_id = str(result[0]) if result else None

            cur.execute(
                """
                INSERT INTO leads
                    (conversation_id, business_id, email, name, intent_trigger,
                     quality, captured_via, metadata, captured_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (conversation_id) DO UPDATE SET
                    email          = EXCLUDED.email,
                    name           = COALESCE(EXCLUDED.name, leads.name),
                    intent_trigger = COALESCE(EXCLUDED.intent_trigger, leads.intent_trigger),
                    quality        = EXCLUDED.quality,
                    metadata       = leads.metadata || EXCLUDED.metadata,
                    captured_via   = EXCLUDED.captured_via
                RETURNING id
                """,
                (
                    conversation_id,
                    business_id,
                    email,
                    name,
                    intent_trigger or "other",
                    quality,
                    "graph",
                    psycopg2.extras.Json(meta),
                    datetime.utcnow(),
                ),
            )
            lead_id = cur.fetchone()[0]
            conn.commit()
            logger.info("upsert_lead | conversation=%s lead_id=%s", conversation_id, lead_id)
            return lead_id
        except Exception as exc:
            conn.rollback()
            logger.error("upsert_lead failed | conversation=%s: %s", conversation_id, exc)
            raise
        finally:
            cur.close()


def update_lead_approval(
    *,
    conversation_id: str,
    human_approved: bool,
    human_reviewer: Optional[str] = None,
    human_notes: Optional[str] = None,
) -> bool:
    """Update HITL approval fields on an existing lead. Returns True on success."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE leads
                SET metadata = metadata || %s::jsonb
                WHERE conversation_id = %s
                """,
                (
                    psycopg2.extras.Json({
                        "human_approved": human_approved,
                        "human_reviewer": human_reviewer,
                        "human_notes": human_notes,
                    }),
                    conversation_id,
                ),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            cur.close()


# ---------------------------------------------------------------------------
# Legacy create (kept for old chat endpoint backwards compatibility)
# ---------------------------------------------------------------------------
def create_lead(
    conversation_id: str,
    email: str,
    name: str = None,
    intent: str = None,
    budget: str = None,
    metadata: Dict = None,
) -> int:
    return upsert_lead(
        conversation_id=conversation_id,
        email=email,
        name=name,
        intent_trigger=intent,
        metadata=metadata or {},
    )


# ---------------------------------------------------------------------------
# Read helpers
# ---------------------------------------------------------------------------
_FULL_SELECT = """
    id, conversation_id, business_id, email, name,
    intent_trigger, quality, captured_via, metadata, captured_at
"""


def get_lead_by_id(lead_id: str) -> Optional[Dict]:
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute(f"SELECT {_FULL_SELECT} FROM leads WHERE id = %s", (lead_id,))
            row = cur.fetchone()
            return _row_to_dict(row) if row else None
        finally:
            cur.close()


def get_lead_by_conversation(conversation_id: str) -> Optional[Dict]:
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                f"SELECT {_FULL_SELECT} FROM leads WHERE conversation_id = %s",
                (conversation_id,),
            )
            row = cur.fetchone()
            return _row_to_dict(row) if row else None
        finally:
            cur.close()


def lead_exists(conversation_id: str) -> bool:
    return get_lead_by_conversation(conversation_id) is not None


def get_all_leads() -> List[Dict]:
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute(f"SELECT {_FULL_SELECT} FROM leads ORDER BY captured_at DESC")
            return [_row_to_dict(row) for row in cur.fetchall()]
        finally:
            cur.close()


def get_leads_pending_approval() -> List[Dict]:
    """Return leads that require human approval and haven't been decided yet."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                f"""
                SELECT {_FULL_SELECT} FROM leads
                WHERE (metadata->>'requires_human_approval')::boolean = true
                  AND metadata->>'human_approved' IS NULL
                ORDER BY captured_at DESC
                """,
            )
            return [_row_to_dict(row) for row in cur.fetchall()]
        finally:
            cur.close()
