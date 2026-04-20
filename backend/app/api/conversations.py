from fastapi import APIRouter, HTTPException
from app.db import messages as msg_db
from app.db.pg_direct import get_db_connection

router = APIRouter()


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation with full message history"""
    try:
        # Get conversation details
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT id, session_id, created_at, updated_at
                FROM conversations
                WHERE id = %s
            """, (conversation_id,))
            
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            conversation = {
                'id': str(row[0]),
                'session_id': row[1],
                'created_at': row[2].isoformat(),
                'updated_at': row[3].isoformat()
            }
            
            cur.close()
        
        # Get messages
        messages = msg_db.get_conversation_history(conversation_id, limit=100)
        
        return {
            'conversation': conversation,
            'messages': messages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching conversation: {str(e)}")


@router.get("/conversations")
async def get_all_conversations():
    """Get all conversations with basic info"""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    c.id,
                    c.session_id,
                    c.created_at,
                    c.updated_at,
                    COUNT(m.id) as message_count,
                    l.email,
                    l.name
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                LEFT JOIN leads l ON c.id = l.conversation_id
                GROUP BY c.id, c.session_id, c.created_at, c.updated_at, l.email, l.name
                ORDER BY c.updated_at DESC
            """)
            
            rows = cur.fetchall()
            conversations = []
            
            for row in rows:
                conversations.append({
                    'id': str(row[0]),
                    'session_id': row[1],
                    'created_at': row[2].isoformat(),
                    'updated_at': row[3].isoformat(),
                    'message_count': row[4],
                    'email': row[5],
                    'name': row[6]
                })
            
            cur.close()
        
        return {'conversations': conversations, 'total': len(conversations)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching conversations: {str(e)}")
