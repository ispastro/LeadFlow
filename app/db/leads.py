from typing import List, Dict, Optional
from app.services.supabase_client import supabase
from datetime import datetime


def create_lead(
    conversation_id: str,
    email: str,
    name: str = None,
    intent: str = None,
    budget: str = None,
    metadata: Dict = None
) -> Dict:
    """Create a new lead"""
    data = {
        'conversation_id': conversation_id,
        'email': email,
        'name': name,
        'intent': intent,
        'budget': budget,
        'metadata': metadata or {},
        'captured_at': datetime.utcnow().isoformat()
    }
    
    result = supabase.table('leads').insert(data).execute()
    return result.data[0] if result.data else None


def get_lead_by_conversation(conversation_id: str) -> Optional[Dict]:
    """Get lead by conversation ID"""
    result = supabase.table('leads').select('*').eq('conversation_id', conversation_id).execute()
    return result.data[0] if result.data else None


def get_all_leads() -> List[Dict]:
    """Get all leads"""
    result = supabase.table('leads').select('*').order('captured_at', desc=True).execute()
    return result.data if result.data else []


def update_lead(lead_id: str, data: Dict) -> Dict:
    """Update lead information"""
    result = supabase.table('leads').update(data).eq('id', lead_id).execute()
    return result.data[0] if result.data else None


def lead_exists(conversation_id: str) -> bool:
    """Check if lead already exists for conversation"""
    lead = get_lead_by_conversation(conversation_id)
    return lead is not None
