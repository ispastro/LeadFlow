from typing import List, Dict
from app.services.supabase_client import supabase
from datetime import datetime


def create_message(conversation_id: str, role: str, content: str) -> Dict:
    """Create a new message"""
    data = {
        'conversation_id': conversation_id,
        'role': role,
        'content': content,
        'created_at': datetime.utcnow().isoformat()
    }
    
    result = supabase.table('messages').insert(data).execute()
    return result.data[0] if result.data else None


def get_conversation_messages(conversation_id: str) -> List[Dict]:
    """Get all messages for a conversation"""
    result = supabase.table('messages').select('*').eq('conversation_id', conversation_id).order('created_at').execute()
    return result.data if result.data else []


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
    result = supabase.table('messages').select('id', count='exact').eq('conversation_id', conversation_id).eq('role', 'user').execute()
    return result.count if hasattr(result, 'count') else 0
