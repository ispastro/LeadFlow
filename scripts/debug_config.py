"""
Debug script to check config values
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import settings

print("🔍 Current Configuration:")
print(f"SUPABASE_URL: {settings.supabase_url}")
print(f"SUPABASE_KEY: {settings.supabase_key[:20]}...")
print(f"SUPABASE_DB_URL: {settings.supabase_db_url}")
print(f"GROQ_API_KEY: {settings.groq_api_key[:20]}...")
