from typing import Dict, Optional
from app.services.supabase_client import supabase
from datetime import datetime


def create_conversation(session_id: str) -> Dict:
    """Create a new conversation"""
    data = {
        'session_id': session_id,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    result = supabase.table('conversations').insert(data).execute()
    return result.data[0] if result.data else None


def get_conversation_by_session(session_id: str) -> Optional[Dict]:
    """Get conversation by session ID"""
    result = supabase.table('conversations').select('*').eq('session_id', session_id).execute()
    return result.data[0] if result.data else None


def get_or_create_conversation(session_id: str) -> Dict:
    """Get existing conversation or create new one"""
    conversation = get_conversation_by_session(session_id)
    if conversation:
        return conversation
    return create_conversation(session_id)


def update_conversation_timestamp(conversation_id: str):
    """Update conversation's updated_at timestamp"""
    data = {'updated_at': datetime.utcnow().isoformat()}
    result = supabase.table('conversations').update(data).eq('id', conversation_id).execute()
    return result.data[0] if result.data else None


def get_all_conversations():
    """Get all conversations"""
    result = supabase.table('conversations').select('*').order('created_at', desc=True).execute()
    return result.data if result.data else []
