from typing import List, Dict, Optional
from app.db.pg_direct import get_pg_connection
import psycopg2.extras
from datetime import datetime


def get_all_documents() -> List[Dict]:
    """Get all documents from knowledge base"""
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, content, metadata, source, created_at
            FROM knowledge_base
            ORDER BY created_at DESC
        """)
        
        rows = cur.fetchall()
        
        documents = []
        for row in rows:
            documents.append({
                'id': str(row[0]),
                'content': row[1],
                'metadata': row[2],
                'source': row[3],
                'created_at': row[4].isoformat() if row[4] else None
            })
        
        return documents
    finally:
        cur.close()
        conn.close()


def get_document_by_id(doc_id: str) -> Optional[Dict]:
    """Get a specific document by ID"""
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, content, metadata, source, created_at
            FROM knowledge_base
            WHERE id = %s
        """, (doc_id,))
        
        row = cur.fetchone()
        if not row:
            return None
        
        return {
            'id': str(row[0]),
            'content': row[1],
            'metadata': row[2],
            'source': row[3],
            'created_at': row[4].isoformat() if row[4] else None
        }
    finally:
        cur.close()
        conn.close()


def insert_document(content: str, embedding: List[float], metadata: Dict = None, source: str = None) -> Dict:
    """Insert a document into knowledge base"""
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO knowledge_base (content, embedding, metadata, source, created_at)
            VALUES (%s, %s::vector, %s, %s, %s)
            RETURNING id, content, metadata, source, created_at
        """, (
            content,
            embedding,
            psycopg2.extras.Json(metadata or {}),
            source,
            datetime.utcnow()
        ))
        
        row = cur.fetchone()
        conn.commit()
        
        return {
            'id': str(row[0]),
            'content': row[1],
            'metadata': row[2],
            'source': row[3],
            'created_at': row[4].isoformat() if row[4] else None
        }
    finally:
        cur.close()
        conn.close()


def update_document(doc_id: str, content: str, embedding: List[float], metadata: Dict = None, source: str = None) -> Dict:
    """Update an existing document"""
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE knowledge_base
            SET content = %s, embedding = %s::vector, metadata = %s, source = %s
            WHERE id = %s
            RETURNING id, content, metadata, source, created_at
        """, (
            content,
            embedding,
            psycopg2.extras.Json(metadata or {}),
            source,
            doc_id
        ))
        
        row = cur.fetchone()
        conn.commit()
        
        if not row:
            return None
        
        return {
            'id': str(row[0]),
            'content': row[1],
            'metadata': row[2],
            'source': row[3],
            'created_at': row[4].isoformat() if row[4] else None
        }
    finally:
        cur.close()
        conn.close()


def delete_document(doc_id: str) -> bool:
    """Delete a document by ID"""
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            DELETE FROM knowledge_base
            WHERE id = %s
        """, (doc_id,))
        
        deleted = cur.rowcount > 0
        conn.commit()
        return deleted
    finally:
        cur.close()
        conn.close()


def delete_all_documents():
    """Delete all documents (use with caution)"""
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM knowledge_base")
        conn.commit()
        return cur.rowcount
    finally:
        cur.close()
        conn.close()


def count_documents() -> int:
    """Count total documents in knowledge base"""
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT COUNT(*) FROM knowledge_base")
        count = cur.fetchone()[0]
        return count
    finally:
        cur.close()
        conn.close()
