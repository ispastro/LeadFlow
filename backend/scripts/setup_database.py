"""
Create database tables for LeadFlow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.pg_direct import get_db_connection

def create_tables():
    """Create all required database tables"""
    
    print("🔧 Creating database tables...\n")
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            # Create conversations table
            print("📝 Creating conversations table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create messages table
            print("📝 Creating messages table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create leads table
            print("📝 Creating leads table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id SERIAL PRIMARY KEY,
                    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
                    email VARCHAR(255) NOT NULL,
                    name VARCHAR(255),
                    intent VARCHAR(100),
                    budget VARCHAR(100),
                    metadata JSONB,
                    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            print("📝 Creating indexes...")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_conversation_id ON leads(conversation_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_captured_at ON leads(captured_at)")
            
            conn.commit()
            print("\n✅ All tables created successfully!")
            
            # Verify tables
            print("\n📊 Verifying tables...")
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = cur.fetchall()
            print(f"Found {len(tables)} tables:")
            for table in tables:
                print(f"  ✅ {table[0]}")
                
        except Exception as e:
            conn.rollback()
            print(f"\n❌ Error: {e}")
            raise
        finally:
            cur.close()


if __name__ == "__main__":
    try:
        create_tables()
        print("\n🎉 Database setup complete!")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
