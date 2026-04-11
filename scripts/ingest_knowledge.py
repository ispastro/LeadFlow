"""
Script to ingest business knowledge into the database.
Run this once to load your business data.
"""

import sys
sys.path.append('..')

from app.core.embeddings import embedding_service
from app.db.knowledge_base import insert_documents_batch, count_documents
from app.utils.text_processing import chunk_text, clean_text
from typing import List, Dict


def load_sample_knowledge():
    """Load sample business knowledge (replace with your actual data)"""
    
    # Sample business data - REPLACE THIS WITH YOUR ACTUAL CONTENT
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
        # Clean text
        content = clean_text(item['content'])
        
        # Chunk if too long (optional, depends on your content)
        if len(content.split()) > 300:
            chunks = chunk_text(content, chunk_size=200, overlap=30)
        else:
            chunks = [content]
        
        # Generate embeddings for each chunk
        for chunk in chunks:
            embedding = embedding_service.embed_text(chunk)
            
            documents_to_insert.append({
                'content': chunk,
                'embedding': embedding,
                'metadata': {
                    'source': item.get('source', 'Unknown'),
                    'category': item.get('category', 'general')
                },
                'source': item.get('source', 'Unknown')
            })
    
    print(f"📝 Inserting {len(documents_to_insert)} documents...")
    
    # Insert in batches
    batch_size = 10
    for i in range(0, len(documents_to_insert), batch_size):
        batch = documents_to_insert[i:i + batch_size]
        insert_documents_batch(batch)
        print(f"✅ Inserted batch {i//batch_size + 1}")
    
    print(f"✅ Successfully ingested {len(documents_to_insert)} documents!")
    
    # Verify
    total = count_documents()
    print(f"📊 Total documents in knowledge base: {total}")


def main():
    """Main ingestion function"""
    print("🚀 Starting knowledge ingestion...")
    
    # Load your business data
    data = load_sample_knowledge()
    
    # Ingest into database
    ingest_knowledge(data)
    
    print("✅ Knowledge ingestion complete!")
    print("\n💡 Next steps:")
    print("1. Run the API: uvicorn main:app --reload")
    print("2. Test the chat endpoint")
    print("3. Replace sample data with your actual business content")


if __name__ == "__main__":
    main()
