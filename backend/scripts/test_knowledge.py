"""
Test knowledge base endpoint directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import knowledge_base as kb_db

print("Testing knowledge base database access...\n")

try:
    print("Attempting to get all documents...")
    documents = kb_db.get_all_documents()
    print(f"✅ Success! Found {len(documents)} documents")
    
    if documents:
        print("\nFirst document:")
        doc = documents[0]
        print(f"  ID: {doc['id']}")
        print(f"  Source: {doc['source']}")
        print(f"  Content: {doc['content'][:100]}...")
    else:
        print("\n⚠️  No documents in knowledge base")
        print("Run: python scripts/ingest_knowledge.py")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
