import logging
from fastapi import APIRouter, HTTPException, Depends
from app.db import messages as msg_db
from app.db.sqlite_db import get_db_connection
from app.api.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, _: dict = Depends(get_current_user)):
    try:
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT id, session_id, created_at, updated_at FROM conversations WHERE id=?",
                (conversation_id,),
            ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Conversation not found")

        conversation = dict(row)
        messages = msg_db.get_conversation_history(conversation_id, limit=100)
        return {"conversation": conversation, "messages": messages}

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to fetch conversation %s: %s", conversation_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/conversations")
async def get_all_conversations(_: dict = Depends(get_current_user)):
    try:
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT c.id, c.session_id, c.created_at, c.updated_at,
                       COUNT(m.id) as message_count,
                       l.email, l.name
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                LEFT JOIN leads l ON c.id = l.conversation_id
                GROUP BY c.id, c.session_id, c.created_at, c.updated_at, l.email, l.name
                ORDER BY c.updated_at DESC
                """
            ).fetchall()

        conversations = [dict(r) for r in rows]
        return {"conversations": conversations, "total": len(conversations)}

    except Exception as exc:
        logger.error("Failed to fetch conversations: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
