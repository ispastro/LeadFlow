from typing import List, Dict, Optional
from app.db.pg_direct import get_pg_connection
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
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO leads (conversation_id, email, name, intent, budget, metadata, captured_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (conversation_id, email, name, intent, budget, psycopg2.extras.Json(metadata or {}), datetime.utcnow()))
        
        lead_id = cur.fetchone()[0]
        conn.commit()
        
        return lead_id
    finally:
        cur.close()
        conn.close()


def get_lead_by_conversation(conversation_id: str) -> Optional[Dict]:
    """Get lead by conversation ID"""
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, conversation_id, email, name, intent, budget, metadata, captured_at
            FROM leads
            WHERE conversation_id = %s
        """, (conversation_id,))
        
        row = cur.fetchone()
        if not row:
            return None
        
        return {
            'id': str(row[0]),
            'conversation_id': str(row[1]),
            'email': row[2],
            'name': row[3],
            'intent': row[4],
            'budget': row[5],
            'metadata': row[6],
            'captured_at': row[7].isoformat()
        }
    finally:
        cur.close()
        conn.close()


def lead_exists(conversation_id: str) -> bool:
    """Check if lead already exists for conversation"""
    lead = get_lead_by_conversation(conversation_id)
    return lead is not None


def get_all_leads() -> List[Dict]:
    """Get all leads"""
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, conversation_id, email, name, intent, budget, metadata, captured_at
            FROM leads
            ORDER BY captured_at DESC
        """)
        
        rows = cur.fetchall()
        
        leads = []
        for row in rows:
            leads.append({
                'id': str(row[0]),
                'conversation_id': str(row[1]),
                'email': row[2],
                'name': row[3],
                'intent': row[4],
                'budget': row[5],
                'metadata': row[6],
                'created_at': row[7].isoformat() if row[7] else None
            })
        
        return leads
    finally:
        cur.close()
        conn.close()
