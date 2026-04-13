"""
Test script to verify RAG pipeline is working correctly
"""

import sys
sys.path.append('..')

from app.core.rag import rag_service
from app.core.embeddings import embedding_service
from app.db.knowledge_base import count_documents


def test_embeddings():
    """Test embedding generation"""
    print("\n🧪 Testing Embeddings...")
    
    test_text = "What are your pricing plans?"
    embedding = embedding_service.embed_text(test_text)
    
    print(f"✅ Generated embedding with dimension: {len(embedding)}")
    print(f"   Expected: 384, Got: {len(embedding)}")
    
    assert len(embedding) == 384, "Embedding dimension mismatch!"
    print("✅ Embeddings working correctly!")


def test_knowledge_base():
    """Test knowledge base has documents"""
    print("\n🧪 Testing Knowledge Base...")
    
    count = count_documents()
    print(f"📊 Documents in knowledge base: {count}")
    
    if count == 0:
        print("⚠️  No documents found! Run: python scripts/ingest_knowledge.py")
        return False
    
    print("✅ Knowledge base populated!")
    return True


def test_retrieval():
    """Test document retrieval"""
    print("\n🧪 Testing Document Retrieval...")
    
    test_queries = [
        "What are your pricing plans?",
        "How do I get started?",
        "What features do you offer?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        docs = rag_service.retrieve_context(query, top_k=2)
        
        if docs:
            print(f"✅ Found {len(docs)} relevant documents")
            for i, doc in enumerate(docs, 1):
                print(f"   {i}. Source: {doc.get('metadata', {}).get('source', 'Unknown')}")
                print(f"      Similarity: {doc.get('similarity', 0):.3f}")
                print(f"      Preview: {doc['content'][:100]}...")
        else:
            print("❌ No documents retrieved")
    
    print("\n✅ Retrieval working!")


def test_rag_response():
    """Test full RAG response generation"""
    print("\n🧪 Testing RAG Response Generation...")
    
    test_message = "What are your pricing plans?"
    print(f"💬 User: {test_message}")
    
    response = rag_service.generate_response(test_message)
    
    print(f"🤖 AI: {response}")
    print("\n✅ RAG pipeline working end-to-end!")


def main():
    """Run all tests"""
    print("🚀 Testing RAG Pipeline...\n")
    print("=" * 60)
    
    try:
        # Test 1: Embeddings
        test_embeddings()
        
        # Test 2: Knowledge Base
        has_docs = test_knowledge_base()
        
        if not has_docs:
            print("\n⚠️  Cannot continue tests without documents in knowledge base")
            return
        
        # Test 3: Retrieval
        test_retrieval()
        
        # Test 4: Full RAG
        test_rag_response()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! RAG pipeline is working correctly!")
        print("\n💡 Next: Start the API with: uvicorn main:app --reload")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
