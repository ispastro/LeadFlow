from typing import Dict, Optional
from app.db.pg_direct import get_db_connection
from datetime import datetime
import uuid


def create_conversation(session_id: str) -> Dict:
    """Create a new conversation"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO conversations (session_id, created_at, updated_at)
                VALUES (%s, %s, %s)
                RETURNING id, session_id, created_at, updated_at
            """, (session_id, datetime.utcnow(), datetime.utcnow()))
            
            row = cur.fetchone()
            conn.commit()
            
            return {
                'id': str(row[0]),
                'session_id': row[1],
                'created_at': row[2].isoformat(),
                'updated_at': row[3].isoformat()
            }
        finally:
            cur.close()


def get_conversation_by_session(session_id: str) -> Optional[Dict]:
    """Get conversation by session ID"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT id, session_id, created_at, updated_at
                FROM conversations
                WHERE session_id = %s
            """, (session_id,))
            
            row = cur.fetchone()
            if not row:
                return None
            
            return {
                'id': str(row[0]),
                'session_id': row[1],
                'created_at': row[2].isoformat(),
                'updated_at': row[3].isoformat()
            }
        finally:
            cur.close()


def get_or_create_conversation(session_id: str) -> Dict:
    """Get existing conversation or create new one"""
    conversation = get_conversation_by_session(session_id)
    if conversation:
        return conversation
    return create_conversation(session_id)


def update_conversation_timestamp(conversation_id: str):
    """Update conversation's updated_at timestamp"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("""
                UPDATE conversations
                SET updated_at = %s
                WHERE id = %s
            """, (datetime.utcnow(), conversation_id))
            conn.commit()
        finally:
            cur.close()
