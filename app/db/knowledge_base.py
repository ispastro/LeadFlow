from typing import List, Dict, Optional
from app.services.supabase_client import supabase


def insert_document(content: str, embedding: List[float], metadata: Dict = None, source: str = None) -> Dict:
    """Insert a document into knowledge base"""
    data = {
        'content': content,
        'embedding': embedding,
        'metadata': metadata or {},
        'source': source
    }
    
    result = supabase.table('knowledge_base').insert(data).execute()
    return result.data[0] if result.data else None


def insert_documents_batch(documents: List[Dict]) -> List[Dict]:
    """Insert multiple documents at once"""
    result = supabase.table('knowledge_base').insert(documents).execute()
    return result.data if result.data else []


def get_all_documents() -> List[Dict]:
    """Get all documents from knowledge base"""
    result = supabase.table('knowledge_base').select('*').execute()
    return result.data if result.data else []


def delete_all_documents():
    """Delete all documents (use with caution)"""
    result = supabase.table('knowledge_base').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    return result


def count_documents() -> int:
    """Count total documents in knowledge base"""
    result = supabase.table('knowledge_base').select('id', count='exact').execute()
    return result.count if hasattr(result, 'count') else 0
