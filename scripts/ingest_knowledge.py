"""
Script to ingest business knowledge into the database.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.embeddings import embedding_service
from app.db.knowledge_base import count_documents
from app.db.pg_direct import insert_vectors_direct
from app.utils.text_processing import chunk_text, clean_text
from typing import List, Dict


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
    """Process and ingest knowledge into database"""
    
    print("🔄 Processing business knowledge...")
    
    documents_to_insert = []
    
    for item in data:
        content = clean_text(item['content'])
        
        if len(content.split()) > 300:
            chunks = chunk_text(content, chunk_size=200, overlap=30)
        else:
            chunks = [content]
        
        for chunk in chunks:
            embedding = embedding_service.embed_text(chunk)
            
            if isinstance(embedding, list):
                embedding_list = embedding
            else:
                embedding_list = embedding.tolist()
            
            documents_to_insert.append({
                'content': chunk,
                'embedding': embedding_list,
                'metadata': {
                    'source': item.get('source', 'Unknown'),
                    'category': item.get('category', 'general')
                },
                'source': item.get('source', 'Unknown')
            })
    
    print(f"📝 Inserting {len(documents_to_insert)} documents...")
    
    insert_vectors_direct(documents_to_insert)
    
    print(f"✅ Successfully ingested {len(documents_to_insert)} documents!")
    
    total = count_documents()
    print(f"📊 Total documents in knowledge base: {total}")


def main():
    """Main ingestion function"""
    print("🚀 Starting knowledge ingestion...")
    
    data = load_sample_knowledge()
    ingest_knowledge(data)
    
    print("✅ Knowledge ingestion complete!")


if __name__ == "__main__":
    main()
