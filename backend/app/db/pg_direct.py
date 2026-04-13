"""
Direct PostgreSQL connection for vector operations
"""

import psycopg2
from psycopg2.extras import execute_values
from config import settings
from typing import List, Dict


def get_pg_connection():
    """Get direct PostgreSQL connection"""
    return psycopg2.connect(settings.supabase_db_url)


def insert_vectors_direct(documents: List[Dict]):
    """Insert documents with vectors using raw SQL"""
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        for doc in documents:
            embedding_list = doc['embedding']
            
            cur.execute("""
                INSERT INTO knowledge_base (content, embedding, metadata, source)
                VALUES (%s, %s::vector, %s, %s)
            """, (
                doc['content'],
                embedding_list,
                psycopg2.extras.Json(doc.get('metadata', {})),
                doc.get('source', 'Unknown')
            ))
        
        conn.commit()
        print(f"✅ Inserted {len(documents)} documents")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def test_vector_search_direct(query_embedding: List[float], top_k: int = 3):
    """Search for similar documents using vector similarity"""
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        cur.execute("""
            SELECT 
                id,
                content,
                metadata,
                1 - (embedding <=> %s::vector) AS similarity
            FROM knowledge_base
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (embedding_str, embedding_str, top_k))
        
        results = cur.fetchall()
        
        docs = []
        for row in results:
            docs.append({
                'id': str(row[0]),
                'content': row[1],
                'metadata': row[2],
                'similarity': float(row[3])
            })
        
        return docs
        
    finally:
        cur.close()
        conn.close()
