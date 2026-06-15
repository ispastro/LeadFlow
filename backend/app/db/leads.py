from typing import List, Dict, Optional
from app.db.pg_direct import get_db_connection
from datetime import datetime
import psycopg2.extras


def create_lead(
    conversation_id: str,
    email: str,
    name: str = None,
    intent: str = None,
    budget: str = None,
    metadata: Dict = None
) -> int:
    """Create a new lead and return lead ID"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            # Get business_id from conversation
            cur.execute("SELECT business_id FROM conversations WHERE id = %s", (conversation_id,))
            result = cur.fetchone()
            business_id = str(result[0]) if result else None
            
            cur.execute("""
                INSERT INTO leads (conversation_id, business_id, email, name, intent_trigger, quality, captured_via, metadata, captured_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                conversation_id,
                business_id,
                email,
                name,
                intent or 'other',
                'MEDIUM',
                'asked',
                psycopg2.extras.Json(metadata or {}),
                datetime.utcnow()
            ))
            
            lead_id = cur.fetchone()[0]
            conn.commit()
            
            return lead_id
        finally:
            cur.close()


def get_lead_by_conversation(conversation_id: str) -> Optional[Dict]:
    """Get lead by conversation ID"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT id, conversation_id, business_id, email, name, intent_trigger, quality, captured_via, metadata, captured_at
                FROM leads
                WHERE conversation_id = %s
            """, (conversation_id,))
            
            row = cur.fetchone()
            if not row:
                return None
            
            return {
                'id': str(row[0]),
                'conversation_id': str(row[1]),
                'business_id': str(row[2]),
                'email': row[3],
                'name': row[4],
                'intent': row[5],
                'quality': row[6],
                'captured_via': row[7],
                'metadata': row[8],
                'captured_at': row[9].isoformat()
            }
        finally:
            cur.close()


def lead_exists(conversation_id: str) -> bool:
    """Check if lead already exists for conversation"""
    lead = get_lead_by_conversation(conversation_id)
    return lead is not None


def get_all_leads() -> List[Dict]:
    """Get all leads"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT id, conversation_id, business_id, email, name, intent_trigger, quality, captured_via, metadata, captured_at
                FROM leads
                ORDER BY captured_at DESC
            """)
            
            rows = cur.fetchall()
            
            leads = []
            for row in rows:
                leads.append({
                    'id': str(row[0]),
                    'conversation_id': str(row[1]),
                    'business_id': str(row[2]),
                    'email': row[3],
                    'name': row[4],
                    'intent': row[5],
                    'quality': row[6],
                    'captured_via': row[7],
                    'metadata': row[8],
                    'created_at': row[9].isoformat() if row[9] else None
                })
            
            return leads
        finally:
            cur.close()
