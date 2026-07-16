"""
migrate_revops.py — SQLite schema setup for LeadFlow RevOps Engine.

Run once before first startup (safe to re-run — all CREATE TABLE/INDEX use IF NOT EXISTS):
    cd backend
    python scripts/migrate_revops.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import sqlite3

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "leadflow.db"

SCHEMA = """
-- Conversations
CREATE TABLE IF NOT EXISTS conversations (
    id           TEXT PRIMARY KEY,
    session_id   TEXT UNIQUE NOT NULL,
    stage        TEXT NOT NULL DEFAULT 'NEW',
    email_captured INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);

-- Messages
CREATE TABLE IF NOT EXISTS messages (
    id              TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role            TEXT NOT NULL,
    content         TEXT NOT NULL,
    created_at      TEXT NOT NULL
);

-- Leads
CREATE TABLE IF NOT EXISTS leads (
    id              TEXT PRIMARY KEY,
    conversation_id TEXT UNIQUE NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    email           TEXT NOT NULL,
    name            TEXT,
    intent_trigger  TEXT,
    quality         TEXT DEFAULT 'MEDIUM',
    captured_via    TEXT DEFAULT 'graph',
    metadata        TEXT DEFAULT '{}',
    captured_at     TEXT NOT NULL
);

-- Knowledge documents
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    content     TEXT NOT NULL,
    category    TEXT NOT NULL DEFAULT 'general',
    source      TEXT DEFAULT 'manual',
    metadata    TEXT DEFAULT '{}',
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at      ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_leads_conversation_id    ON leads(conversation_id);
CREATE INDEX IF NOT EXISTS idx_leads_captured_at        ON leads(captured_at DESC);
CREATE INDEX IF NOT EXISTS idx_knowledge_created_at     ON knowledge_documents(created_at DESC);
"""


def main():
    logger.info("LeadFlow — SQLite schema setup → %s", DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    logger.info("Schema ready.")


if __name__ == "__main__":
    main()
