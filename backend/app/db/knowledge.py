from typing import List, Dict, Optional
from app.db.pg_direct import get_db_connection
from datetime import datetime
import psycopg2.extras

def get_all_knowledge(business_id: str) -> List[Dict]:
    """Get all knowledge documents for a business"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT id, business_id, title, content, category, source, metadata, created_at, updated_at
                FROM knowledge_documents
                WHERE business_id = %s
                ORDER BY created_at DESC
            """, (business_id,))
            
            rows = cur.fetchall()
            
            documents = []
            for row in rows:
                documents.append({
                    'id': str(row[0]),
                    'business_id': str(row[1]),
                    'title': row[2],
                    'content': row[3],
                    'category': row[4],
                    'source': row[5],
                    'metadata': row[6],
                    'created_at': row[7].isoformat() if row[7] else None,
                    'updated_at': row[8].isoformat() if row[8] else None
                })
            
            return documents
        finally:
            cur.close()


def get_knowledge_by_id(knowledge_id: str) -> Optional[Dict]:
    """Get single knowledge document"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT id, business_id, title, content, category, source, metadata, created_at, updated_at
                FROM knowledge_documents
                WHERE id = %s
            """, (knowledge_id,))
            
            row = cur.fetchone()
            if not row:
                return None
            
            return {
                'id': str(row[0]),
                'business_id': str(row[1]),
                'title': row[2],
                'content': row[3],
                'category': row[4],
                'source': row[5],
                'metadata': row[6],
                'created_at': row[7].isoformat() if row[7] else None,
                'updated_at': row[8].isoformat() if row[8] else None
            }
        finally:
            cur.close()


def create_knowledge(
    business_id: str,
    title: str,
    content: str,
    category: str,
    source: str = "manual",
    metadata: Dict = None
) -> str:
    """Create new knowledge document"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO knowledge_documents (business_id, title, content, category, source, metadata, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                business_id,
                title,
                content,
                category,
                source,
                psycopg2.extras.Json(metadata or {}),
                datetime.utcnow(),
                datetime.utcnow()
            ))
            
            knowledge_id = str(cur.fetchone()[0])
            conn.commit()
            
            return knowledge_id
        finally:
            cur.close()


def update_knowledge(
    knowledge_id: str,
    title: str = None,
    content: str = None,
    category: str = None,
    source: str = None,
    metadata: Dict = None
) -> bool:
    """Update knowledge document"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            # Build dynamic update query
            updates = []
            values = []
            
            if title is not None:
                updates.append("title = %s")
                values.append(title)
            
            if content is not None:
                updates.append("content = %s")
                values.append(content)
            
            if category is not None:
                updates.append("category = %s")
                values.append(category)
            
            if source is not None:
                updates.append("source = %s")
                values.append(source)
            
            if metadata is not None:
                updates.append("metadata = %s")
                values.append(psycopg2.extras.Json(metadata))
            
            updates.append("updated_at = %s")
            values.append(datetime.utcnow())
            
            values.append(knowledge_id)
            
            query = f"UPDATE knowledge_documents SET {', '.join(updates)} WHERE id = %s"
            cur.execute(query, values)
            conn.commit()
            
            return cur.rowcount > 0
        finally:
            cur.close()


def delete_knowledge(knowledge_id: str) -> bool:
    """Delete knowledge document"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("DELETE FROM knowledge_documents WHERE id = %s", (knowledge_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            cur.close()


def count_knowledge(business_id: str) -> int:
    """Count knowledge documents for a business"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("SELECT COUNT(*) FROM knowledge_documents WHERE business_id = %s", (business_id,))
            return cur.fetchone()[0]
        finally:
            cur.close()
