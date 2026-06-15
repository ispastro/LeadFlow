import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from config import settings
import psycopg2

def create_knowledge_table():
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    print("Creating knowledge_documents table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_documents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            source TEXT NOT NULL,
            metadata JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_knowledge_business 
        ON knowledge_documents(business_id);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_knowledge_category 
        ON knowledge_documents(business_id, category);
    """)
    
    conn.commit()
    
    # Insert default knowledge for default business
    cursor.execute("SELECT id FROM businesses WHERE api_key = 'default_api_key_123' LIMIT 1;")
    result = cursor.fetchone()
    default_business_id = str(result[0]) if result else None
    
    if default_business_id:
        print(f"Inserting default knowledge for business: {default_business_id}")
        
        default_docs = [
            {
                "title": "Features",
                "content": """Key Features:
- AI-powered chat responses using RAG technology
- Automatic lead capture and qualification
- Real-time conversation analytics
- Easy website integration (one script tag)
- Admin dashboard for lead management
- 24/7 automated support""",
                "category": "features",
                "source": "About Us"
            },
            {
                "title": "Getting Started",
                "content": """Getting Started:
1. Sign up for a free trial
2. Add our chat widget to your website (copy-paste one line of code)
3. Customize your AI agent's knowledge base
4. Start capturing leads automatically
Setup takes less than 5 minutes.""",
                "category": "onboarding",
                "source": "Getting Started"
            },
            {
                "title": "Pricing",
                "content": """Pricing Plans:
- Starter: $49/month - Up to 1,000 conversations, basic analytics
- Professional: $149/month - Up to 10,000 conversations, advanced analytics, priority support
- Enterprise: Custom pricing - Unlimited conversations, dedicated support, custom integrations
All plans include 14-day free trial.""",
                "category": "pricing",
                "source": "Pricing"
            },
            {
                "title": "FAQ",
                "content": """FAQ:
Q: How does the AI know about my business?
A: You provide your business information, and our RAG system uses it to answer questions accurately.

Q: Can I customize the AI's responses?
A: Yes, you can train it on your specific content and adjust the tone.

Q: What happens to captured leads?
A: They're stored securely in your dashboard and can be exported or integrated with your CRM.""",
                "category": "faq",
                "source": "FAQ"
            }
        ]
        
        for doc in default_docs:
            cursor.execute("""
                INSERT INTO knowledge_documents (business_id, title, content, category, source)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (default_business_id, doc['title'], doc['content'], doc['category'], doc['source']))
        
        conn.commit()
        print(f"Inserted {len(default_docs)} default knowledge documents")
    
    cursor.close()
    conn.close()
    
    print("Knowledge table created successfully!")

if __name__ == "__main__":
    create_knowledge_table()
