"""
Direct PostgreSQL connection with connection pooling
"""

import psycopg2
from psycopg2 import pool
from psycopg2.extras import execute_values
from config import settings
from typing import List, Dict
from contextlib import contextmanager
import atexit
import logging

logger = logging.getLogger(__name__)

# Global connection pool
_connection_pool = None


def initialize_pool(minconn=2, maxconn=10):
    """Initialize the connection pool (called on app startup)"""
    global _connection_pool
    
    if _connection_pool is None:
        try:
            _connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=minconn,
                maxconn=maxconn,
                dsn=settings.supabase_db_url
            )
            logger.info(f"✅ Database connection pool created ({minconn}-{maxconn} connections)")
        except Exception as e:
            logger.error(f"❌ Failed to create connection pool: {e}")
            raise
    
    return _connection_pool


def close_pool():
    """Close all connections in the pool (called on app shutdown)"""
    global _connection_pool
    
    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None
        logger.info("✅ Database connection pool closed")


# Register cleanup on exit
atexit.register(close_pool)


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Automatically returns connection to pool when done.
    
    Usage:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users")
    """
    # Initialize pool if not exists
    if _connection_pool is None:
        initialize_pool()
    
    conn = _connection_pool.getconn()
    try:
        yield conn
    finally:
        _connection_pool.putconn(conn)


def get_pg_connection():
    """
    Legacy function for backward compatibility.
    Returns a connection from the pool.
    
    WARNING: You must manually close this connection!
    Better to use get_db_connection() context manager.
    """
    if _connection_pool is None:
        initialize_pool()
    
    return _connection_pool.getconn()


def return_connection(conn):
    """Return a connection to the pool"""
    if _connection_pool and conn:
        _connection_pool.putconn(conn)


def insert_vectors_direct(documents: List[Dict]):
    """Insert documents with vectors using raw SQL"""
    with get_db_connection() as conn:
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
            logger.info(f"✅ Inserted {len(documents)} documents")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error inserting: {e}")
            raise
        finally:
            cur.close()


def test_vector_search_direct(query_embedding: List[float], top_k: int = 3):
    """Search for similar documents using vector similarity"""
    with get_db_connection() as conn:
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
