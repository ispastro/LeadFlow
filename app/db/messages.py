from typing import List, Dict
from app.db.pg_direct import get_pg_connection
from datetime import datetime


def create_message(conversation_id: str, role: str, content: str) -> Dict:
    """Create a new message"""
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO messages (conversation_id, role, content, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id, conversation_id, role, content, created_at
        """, (conversation_id, role, content, datetime.utcnow()))
        
        row = cur.fetchone()
        conn.commit()
        
        return {
            'id': str(row[0]),
            'conversation_id': str(row[1]),
            'role': row[2],
            'content': row[3],
            'created_at': row[4].isoformat()
        }
    finally:
        cur.close()
        conn.close()


def get_conversation_messages(conversation_id: str) -> List[Dict]:
    """Get all messages for a conversation"""
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, conversation_id, role, content, created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at
        """, (conversation_id,))
        
        rows = cur.fetchall()
        messages = []
        for row in rows:
            messages.append({
                'id': str(row[0]),
                'conversation_id': str(row[1]),
                'role': row[2],
                'content': row[3],
                'created_at': row[4].isoformat()
            })
        return messages
    finally:
        cur.close()
        conn.close()


def get_conversation_history(conversation_id: str, limit: int = 10) -> List[Dict[str, str]]:
    """Get conversation history formatted for AI (last N messages)"""
    messages = get_conversation_messages(conversation_id)
    
    # Get last N messages
    recent_messages = messages[-limit:] if len(messages) > limit else messages
    
    # Format for AI
    history = []
    for msg in recent_messages:
        history.append({
            'role': msg['role'],
            'content': msg['content']
        })
    
    return history


def count_user_messages(conversation_id: str) -> int:
    """Count user messages in conversation"""
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT COUNT(*)
            FROM messages
            WHERE conversation_id = %s AND role = 'user'
        """, (conversation_id,))
        
        return cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()
