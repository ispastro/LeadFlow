import asyncio
import sys
import os

# Allow running from the backend/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.pg_direct import get_db_connection, initialize_pool
import logging

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Step 1 — Leads table: add new columns + unique constraint
# ---------------------------------------------------------------------------
LEADS_MIGRATIONS = [
    # Unique constraint on conversation_id (enables ON CONFLICT upsert)
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint
            WHERE conname = 'leads_conversation_id_key'
        ) THEN
            ALTER TABLE leads
                ADD CONSTRAINT leads_conversation_id_key
                UNIQUE (conversation_id);
        END IF;
    END $$;
    """,

    # Add conversations.stage + email_captured if missing (legacy compat)
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='conversations' AND column_name='stage'
        ) THEN
            ALTER TABLE conversations ADD COLUMN stage VARCHAR(50) DEFAULT 'NEW';
        END IF;
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='conversations' AND column_name='email_captured'
        ) THEN
            ALTER TABLE conversations ADD COLUMN email_captured BOOLEAN DEFAULT FALSE;
        END IF;
    END $$;
    """,

    # Ensure leads.metadata is JSONB (not TEXT) — needed for || operator
    """
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'leads'
              AND column_name = 'metadata'
              AND data_type != 'jsonb'
        ) THEN
            ALTER TABLE leads ALTER COLUMN metadata TYPE JSONB
                USING metadata::jsonb;
        END IF;
    END $$;
    """,

    # Default metadata to empty object
    """
    ALTER TABLE leads
        ALTER COLUMN metadata SET DEFAULT '{}';
    """,

    # Update existing NULL metadata rows
    """
    UPDATE leads SET metadata = '{}' WHERE metadata IS NULL;
    """,
]


# ---------------------------------------------------------------------------
# Step 2 — Indexes for HITL dashboard queries
# ---------------------------------------------------------------------------
INDEXES = [
    """
    CREATE INDEX IF NOT EXISTS idx_leads_hitl_pending
        ON leads ((metadata->>'requires_human_approval'))
        WHERE (metadata->>'requires_human_approval')::boolean = true;
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_leads_manual_review
        ON leads ((metadata->>'is_manual_review'))
        WHERE (metadata->>'is_manual_review')::boolean = true;
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_leads_qualification_score
        ON leads ((metadata->>'qualification_score'));
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_conversations_session_id
        ON conversations (session_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_conversations_updated_at
        ON conversations (updated_at DESC);
    """,
]


# ---------------------------------------------------------------------------
# Step 3 — LangGraph checkpointer tables (async)
# ---------------------------------------------------------------------------
async def create_checkpointer_tables():
    """Use AsyncPostgresSaver.setup() to create LangGraph tables."""
    from app.db.checkpointer import init_checkpointer
    logger.info("Creating LangGraph checkpointer tables...")
    await init_checkpointer()
    logger.info("  ✓ Checkpointer tables ready")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def run_sync_migrations():
    initialize_pool(minconn=1, maxconn=3)

    with get_db_connection() as conn:
        cur = conn.cursor()

        logger.info("── Step 1: Leads table migrations ──────────────────────")
        for i, sql in enumerate(LEADS_MIGRATIONS, 1):
            try:
                cur.execute(sql)
                conn.commit()
                logger.info("  ✓ Migration %d applied", i)
            except Exception as exc:
                conn.rollback()
                logger.error("  ✗ Migration %d failed: %s", i, exc)
                raise

        logger.info("── Step 2: Indexes ──────────────────────────────────────")
        for sql in INDEXES:
            # Extract index name for logging
            idx_name = sql.strip().split("idx_")[1].split("\n")[0].strip() \
                if "idx_" in sql else "index"
            try:
                cur.execute(sql)
                conn.commit()
                logger.info("  ✓ %s", idx_name)
            except Exception as exc:
                conn.rollback()
                logger.warning("  ⚠ Index skipped (%s): %s", idx_name, exc)

        cur.close()


async def main():
    logger.info("═" * 56)
    logger.info("LeadFlow RevOps — Database Migration")
    logger.info("═" * 56)

    run_sync_migrations()

    logger.info("── Step 3: LangGraph checkpointer tables ────────────────")
    await create_checkpointer_tables()

    logger.info("═" * 56)
    logger.info("Migration complete ✓")
    logger.info("═" * 56)


if __name__ == "__main__":
    asyncio.run(main())
