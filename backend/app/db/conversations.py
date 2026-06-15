from typing import Dict, Optional
from app.db.pg_direct import get_db_connection
from datetime import datetime
import uuid


def create_conversation(session_id: str, business_id: str = None) -> Dict:
    """Create a new conversation"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Get default business if not provided
        if not business_id:
            cur.execute("SELECT id FROM businesses WHERE api_key = 'default_api_key_123' LIMIT 1;")
            result = cur.fetchone()
            business_id = str(result[0]) if result else None
        
        try:
            cur.execute("""
                INSERT INTO conversations (session_id, business_id, stage, email_captured, created_at, updated_at)
                VALUES (%s, %s, 'NEW', FALSE, %s, %s)
                RETURNING id, session_id, business_id, stage, email_captured, created_at, updated_at
            """, (session_id, business_id, datetime.utcnow(), datetime.utcnow()))
            
            row = cur.fetchone()
            conn.commit()
            
            return {
                'id': str(row[0]),
                'session_id': row[1],
                'business_id': str(row[2]),
                'stage': row[3],
                'email_captured': row[4],
                'created_at': row[5].isoformat(),
                'updated_at': row[6].isoformat()
            }
        finally:
            cur.close()


def get_conversation_by_session(session_id: str) -> Optional[Dict]:
    """Get conversation by session ID"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT id, session_id, business_id, stage, email_captured, created_at, updated_at
                FROM conversations
                WHERE session_id = %s
            """, (session_id,))
            
            row = cur.fetchone()
            if not row:
                return None
            
            return {
                'id': str(row[0]),
                'session_id': row[1],
                'business_id': str(row[2]),
                'stage': row[3],
                'email_captured': row[4],
                'created_at': row[5].isoformat(),
                'updated_at': row[6].isoformat()
            }
        finally:
            cur.close()


def get_or_create_conversation(session_id: str, business_id: str = None) -> Dict:
    """Get existing conversation or create new one"""
    conversation = get_conversation_by_session(session_id)
    if conversation:
        return conversation
    return create_conversation(session_id, business_id)


def update_conversation_stage(conversation_id: str, stage: str, email_captured: bool = None):
    """Update conversation stage"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            if email_captured is not None:
                cur.execute("""
                    UPDATE conversations
                    SET stage = %s, email_captured = %s, updated_at = %s
                    WHERE id = %s
                """, (stage, email_captured, datetime.utcnow(), conversation_id))
            else:
                cur.execute("""
                    UPDATE conversations
                    SET stage = %s, updated_at = %s
                    WHERE id = %s
                """, (stage, datetime.utcnow(), conversation_id))
            conn.commit()
        finally:
            cur.close()


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
