"""
Clear all documents from knowledge base
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.pg_direct import get_pg_connection


def clear_knowledge_base():
    """Delete all documents"""
    print("🗑️  Clearing knowledge base...")
    
    conn = get_pg_connection()
    cur = conn.cursor()
    
    try:
        # Count before
        cur.execute("SELECT COUNT(*) FROM knowledge_base")
        before = cur.fetchone()[0]
        print(f"📊 Documents before: {before}")
        
        # Delete all
        cur.execute("DELETE FROM knowledge_base")
        conn.commit()
        
        # Count after
        cur.execute("SELECT COUNT(*) FROM knowledge_base")
        after = cur.fetchone()[0]
        print(f"📊 Documents after: {after}")
        
        if after == 0:
            print("✅ Knowledge base cleared successfully!")
        else:
            print(f"⚠️  Still {after} documents remaining")
    
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    clear_knowledge_base()
