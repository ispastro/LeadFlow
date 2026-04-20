import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()  # Load .env file

from config import settings
from app.core.embeddings import embedding_service
from app.services.qdrant_service import qdrant_service
from app.utils.text_processing import chunk_text, clean_text
from typing import List, Dict
import uuid


def load_sample_knowledge():
    """Load sample business knowledge"""
    
    business_data = [
        {
            "content": """
            We are a SaaS company offering AI-powered sales automation tools.
            Our platform helps businesses convert website visitors into qualified leads automatically.
            We provide 24/7 AI chat support, lead capture, and intelligent qualification.
            """,
            "source": "About Us",
            "category": "company"
        },
        {
            "content": """
            Pricing Plans:
            - Starter: $49/month - Up to 1,000 conversations, basic analytics
            - Professional: $149/month - Up to 10,000 conversations, advanced analytics, priority support
            - Enterprise: Custom pricing - Unlimited conversations, dedicated support, custom integrations
            All plans include 14-day free trial.
            """,
            "source": "Pricing",
            "category": "pricing"
        },
        {
            "content": """
            Key Features:
            - AI-powered chat responses using RAG technology
            - Automatic lead capture and qualification
            - Real-time conversation analytics
            - Easy website integration (one script tag)
            - Admin dashboard for lead management
            - 24/7 automated support
            """,
            "source": "Features",
            "category": "features"
        },
        {
            "content": """
            Getting Started:
            1. Sign up for a free trial
            2. Add our chat widget to your website (copy-paste one line of code)
            3. Customize your AI agent's knowledge base
            4. Start capturing leads automatically
            Setup takes less than 5 minutes.
            """,
            "source": "Getting Started",
            "category": "onboarding"
        },
        {
            "content": """
            FAQ:
            Q: How does the AI know about my business?
            A: You provide your business information, and our RAG system uses it to answer questions accurately.
            
            Q: Can I customize the AI's responses?
            A: Yes, you can train it on your specific content and adjust the tone.
            
            Q: What happens to captured leads?
            A: They're stored securely in your dashboard and can be exported or integrated with your CRM.
            """,
            "source": "FAQ",
            "category": "faq"
        }
    ]
    
    return business_data


def ingest_knowledge(data: List[Dict]):
    """Process and ingest knowledge to Qdrant"""
    
    print("🔄 Processing business knowledge...")
    
    documents_to_insert = []
    
    for item in data:
        content = clean_text(item['content'])
        
        if len(content.split()) > 300:
            chunks = chunk_text(content, chunk_size=200, overlap=30)
        else:
            chunks = [content]
        
        for chunk in chunks:
            # Generate embedding with FastEmbed
            embedding = embedding_service.embed_text(chunk)
            
            doc = {
                'id': str(uuid.uuid4()),
                'content': chunk,
                'embedding': embedding,
                'source': item.get('source', 'Unknown'),
                'category': item.get('category', 'general')
            }
            documents_to_insert.append(doc)
    
    print(f"📝 Inserting {len(documents_to_insert)} documents to Qdrant...")
    
    # Collection is auto-created by _ensure_collection in qdrant_service
    # Just add documents
    batch_size = 100
    for i in range(0, len(documents_to_insert), batch_size):
        batch = documents_to_insert[i:i+batch_size]
        qdrant_service.add_documents(batch)
        print(f"  ➡️ Inserted {min(i+batch_size, len(documents_to_insert))}/{len(documents_to_insert)}")
    
    total = qdrant_service.count_documents()
    print(f"✅ Successfully ingested {len(documents_to_insert)} documents!")
    print(f"📊 Total documents in Qdrant: {total}")


def main():
    """Main ingestion function"""
    print("🚀 Starting knowledge ingestion...")
    
    # Configure Qdrant with credentials from settings
    if settings.qdrant_url and settings.qdrant_api_key:
        qdrant_service.configure(settings.qdrant_url, settings.qdrant_api_key)
        print(f"✅ Qdrant configured: {settings.qdrant_url}")
    else:
        print("❌ Qdrant credentials not found in .env")
        return
    
    data = load_sample_knowledge()
    ingest_knowledge(data)
    
    print("✅ Knowledge ingestion complete!")


if __name__ == "__main__":
    main()
