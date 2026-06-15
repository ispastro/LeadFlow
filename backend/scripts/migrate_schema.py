import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from config import settings
import psycopg2

def migrate():
    """Apply schema migrations"""
    
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    print("🚀 Starting migration...\n")
    
    # Step 1: Create businesses table
    print("1️⃣ Creating businesses table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
          id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          name            TEXT NOT NULL,
          domain          TEXT NOT NULL,
          api_key         TEXT NOT NULL UNIQUE,
          widget_settings JSONB DEFAULT '{}'::jsonb,
          active          BOOLEAN NOT NULL DEFAULT TRUE,
          created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
          updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_businesses_api_key ON businesses(api_key);")
    conn.commit()
    print("   ✅ Businesses table created\n")
    
    # Step 2: Insert default business
    print("2️⃣ Creating default business...")
    cursor.execute("""
        INSERT INTO businesses (name, domain, api_key)
        VALUES ('Default Business', 'leadflow.ai', 'default_api_key_123')
        ON CONFLICT (api_key) DO NOTHING
        RETURNING id;
    """)
    result = cursor.fetchone()
    default_business_id = result[0] if result else None
    
    if not default_business_id:
        cursor.execute("SELECT id FROM businesses WHERE api_key = 'default_api_key_123';")
        default_business_id = cursor.fetchone()[0]
    
    conn.commit()
    print(f"   ✅ Default business ID: {default_business_id}\n")
    
    # Step 3: Add columns to conversations
    print("3️⃣ Updating conversations table...")
    
    cursor.execute("""
        ALTER TABLE conversations 
        ADD COLUMN IF NOT EXISTS business_id UUID REFERENCES businesses(id) ON DELETE CASCADE;
    """)
    
    cursor.execute("""
        ALTER TABLE conversations 
        ADD COLUMN IF NOT EXISTS session_id TEXT;
    """)
    
    cursor.execute("""
        ALTER TABLE conversations 
        ADD COLUMN IF NOT EXISTS stage TEXT DEFAULT 'NEW';
    """)
    
    cursor.execute("""
        ALTER TABLE conversations 
        ADD COLUMN IF NOT EXISTS email_captured BOOLEAN DEFAULT FALSE;
    """)
    
    cursor.execute("""
        ALTER TABLE conversations 
        ADD COLUMN IF NOT EXISTS email_ask_count INT DEFAULT 0;
    """)
    
    conn.commit()
    
    # Set default business_id for existing rows
    cursor.execute(f"""
        UPDATE conversations 
        SET business_id = '{default_business_id}'
        WHERE business_id IS NULL;
    """)
    
    # Generate session_id for existing rows (use id as fallback)
    cursor.execute("""
        UPDATE conversations 
        SET session_id = CONCAT('legacy_', id::text)
        WHERE session_id IS NULL;
    """)
    
    conn.commit()
    
    # Make business_id NOT NULL after populating
    cursor.execute("ALTER TABLE conversations ALTER COLUMN business_id SET NOT NULL;")
    cursor.execute("ALTER TABLE conversations ALTER COLUMN session_id SET NOT NULL;")
    
    conn.commit()
    
    # Add indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_business_id ON conversations(business_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_business_created ON conversations(business_id, created_at DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);")
    
    conn.commit()
    print("   ✅ Conversations table updated\n")
    
    # Step 4: Add columns to messages
    print("4️⃣ Updating messages table...")
    
    cursor.execute("""
        ALTER TABLE messages 
        ADD COLUMN IF NOT EXISTS business_id UUID REFERENCES businesses(id) ON DELETE CASCADE;
    """)
    
    conn.commit()
    
    # Populate business_id from conversations
    cursor.execute("""
        UPDATE messages m
        SET business_id = c.business_id
        FROM conversations c
        WHERE m.conversation_id = c.id AND m.business_id IS NULL;
    """)
    
    conn.commit()
    
    cursor.execute("ALTER TABLE messages ALTER COLUMN business_id SET NOT NULL;")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id, created_at ASC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_business_id ON messages(business_id, created_at DESC);")
    
    conn.commit()
    print("   ✅ Messages table updated\n")
    
    # Step 5: Update leads table
    print("5️⃣ Updating leads table...")
    
    cursor.execute("""
        ALTER TABLE leads 
        ADD COLUMN IF NOT EXISTS business_id UUID REFERENCES businesses(id) ON DELETE CASCADE;
    """)
    
    cursor.execute("""
        ALTER TABLE leads 
        ADD COLUMN IF NOT EXISTS intent_trigger TEXT DEFAULT 'other';
    """)
    
    cursor.execute("""
        ALTER TABLE leads 
        ADD COLUMN IF NOT EXISTS quality TEXT DEFAULT 'MEDIUM';
    """)
    
    cursor.execute("""
        ALTER TABLE leads 
        ADD COLUMN IF NOT EXISTS captured_via TEXT DEFAULT 'asked';
    """)
    
    cursor.execute("""
        ALTER TABLE leads 
        ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
    """)
    
    conn.commit()
    
    # Populate business_id from conversations
    cursor.execute("""
        UPDATE leads l
        SET business_id = c.business_id
        FROM conversations c
        WHERE l.conversation_id = c.id AND l.business_id IS NULL;
    """)
    
    conn.commit()
    
    cursor.execute("ALTER TABLE leads ALTER COLUMN business_id SET NOT NULL;")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_business_id ON leads(business_id, captured_at DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_metadata ON leads USING gin(metadata);")
    
    conn.commit()
    print("   ✅ Leads table updated\n")
    
    # Step 6: Create outbox_jobs table
    print("6️⃣ Creating outbox_jobs table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outbox_jobs (
          id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          job_type        TEXT NOT NULL,
          payload         JSONB NOT NULL,
          status          TEXT NOT NULL DEFAULT 'pending',
          attempts        INT NOT NULL DEFAULT 0,
          last_error      TEXT,
          created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
          updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_outbox_pending 
        ON outbox_jobs(status, created_at ASC) WHERE status = 'pending';
    """)
    
    conn.commit()
    print("   ✅ Outbox jobs table created\n")
    
    cursor.close()
    conn.close()
    
    print("✅ Migration completed successfully!")
    print(f"\n📊 Default Business ID: {default_business_id}")
    print("   Use this ID in your application configuration.\n")

if __name__ == "__main__":
    migrate()
