import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from app.db.sqlite_db import get_db_connection, from_json

logger = logging.getLogger(__name__)


def _since(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


class AnalyticsService:

    def get_overview_metrics(self, days: int = 30) -> Dict:
        since = _since(days)
        with get_db_connection() as conn:
            total_conversations = conn.execute(
                "SELECT COUNT(*) FROM conversations WHERE created_at >= ?", (since,)
            ).fetchone()[0]

            total_leads = conn.execute(
                "SELECT COUNT(*) FROM leads WHERE captured_at >= ?", (since,)
            ).fetchone()[0]

            conversion_rate = (
                round(total_leads / total_conversations * 100, 2)
                if total_conversations > 0 else 0
            )

            avg_row = conn.execute(
                """
                SELECT AVG(cnt) FROM (
                    SELECT COUNT(*) as cnt FROM messages
                    WHERE created_at >= ?
                    GROUP BY conversation_id
                )
                """,
                (since,),
            ).fetchone()
            avg_messages = round(float(avg_row[0] or 0), 2)

        return {
            "total_conversations": total_conversations,
            "total_leads": total_leads,
            "conversion_rate": conversion_rate,
            "avg_messages_per_conversation": avg_messages,
        }

    def get_lead_quality_breakdown(self, days: int = 30) -> List[Dict]:
        since = _since(days)
        leads = self._get_leads_since(since)
        counts: Dict[str, int] = {}
        for lead in leads:
            q = (lead.get("metadata") or {}).get("qualification_tier") or "unknown"
            counts[q] = counts.get(q, 0) + 1
        return [{"quality": k.upper(), "count": v} for k, v in counts.items()]

    def get_intent_breakdown(self, days: int = 30) -> List[Dict]:
        since = _since(days)
        with get_db_connection() as conn:
            rows = conn.execute(
                "SELECT intent_trigger, COUNT(*) as cnt FROM leads WHERE captured_at >= ? AND intent_trigger IS NOT NULL GROUP BY intent_trigger",
                (since,),
            ).fetchall()
        return [{"intent": r["intent_trigger"], "count": r["cnt"]} for r in rows]

    def get_time_series_data(self, days: int = 30) -> Dict:
        since = _since(days)
        with get_db_connection() as conn:
            conv_rows = conn.execute(
                "SELECT DATE(created_at) as d, COUNT(*) as cnt FROM conversations WHERE created_at >= ? GROUP BY d ORDER BY d",
                (since,),
            ).fetchall()
            lead_rows = conn.execute(
                "SELECT DATE(captured_at) as d, COUNT(*) as cnt FROM leads WHERE captured_at >= ? GROUP BY d ORDER BY d",
                (since,),
            ).fetchall()
        return {
            "conversations": [{"date": r["d"], "count": r["cnt"]} for r in conv_rows],
            "leads":         [{"date": r["d"], "count": r["cnt"]} for r in lead_rows],
        }

    def _get_leads_since(self, since: str) -> List[Dict]:
        with get_db_connection() as conn:
            rows = conn.execute(
                "SELECT metadata FROM leads WHERE captured_at >= ?", (since,)
            ).fetchall()
        return [{"metadata": from_json(r["metadata"])} for r in rows]


analytics_service = AnalyticsService()
