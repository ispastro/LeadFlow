"""
Test script to debug RAG retrieval
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.embeddings import embedding_service
from app.db.pg_direct import test_vector_search_direct, get_pg_connection


def test_database_contents():
    """Check what's in the database"""
    print("\n📊 Testing Database Contents...")
    
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT COUNT(*) FROM knowledge_base")
        count = cur.fetchone()[0]
        print(f"✅ Total documents in database: {count}")
        
        if count == 0:
            print("❌ ERROR: No documents in database!")
            return False
        
        cur.execute("SELECT content, source, embedding FROM knowledge_base LIMIT 3")
        docs = cur.fetchall()
        
        print(f"\n📄 Sample documents:")
        for i, doc in enumerate(docs, 1):
            content, source, embedding = doc
            print(f"\n  Doc {i}:")
            print(f"    Content: {content[:100]}...")
            print(f"    Source: {source}")
            print(f"    Has embedding: {embedding is not None}")
        
        return True
        
    finally:
        cur.close()
        conn.close()


def test_vector_search():
    """Test vector similarity search"""
    print("\n\n🔍 Testing Vector Search...")
    
    query = "What are your pricing plans?"
    print(f"Query: '{query}'")
    
    query_embedding = embedding_service.embed_text(query)
    print(f"✅ Generated embedding (dimension: {len(query_embedding)})")
    
    print("\n🔎 Searching with direct PostgreSQL...")
    docs = test_vector_search_direct(query_embedding, top_k=5)
    
    print(f"✅ PostgreSQL returned {len(docs)} documents")
    
    if docs:
        print("\n📄 Retrieved documents:")
        for i, doc in enumerate(docs, 1):
            print(f"\n  Doc {i}:")
            print(f"    Content: {doc['content'][:100]}...")
            print(f"    Similarity: {doc.get('similarity', 0):.4f}")
    else:
        print("❌ ERROR: No documents returned!")
    
    return len(docs) > 0


def main():
    print("🚀 RAG Debugging Script\n")
    print("=" * 60)
    
    db_ok = test_database_contents()
    
    if not db_ok:
        print("\n❌ Database is empty. Run: python scripts/ingest_knowledge.py")
        return
    
    search_ok = test_vector_search()
    
    print("\n" + "=" * 60)
    if search_ok:
        print("✅ RAG system is working!")
    else:
        print("❌ RAG system has issues.")


if __name__ == "__main__":
    main()
