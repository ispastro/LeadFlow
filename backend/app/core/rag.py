import logging
from typing import Dict, List

from langchain_core.tools import tool

from app.core.embeddings import embedding_service
from app.services.groq_client import groq_service, get_llm
from app.services.qdrant_service import qdrant_service

logger = logging.getLogger(__name__)

_FALLBACK_CONTEXT = (
    "LeadFlow AI is a SaaS platform that converts website visitors into qualified leads "
    "automatically using AI-powered chat. Key features: 24/7 AI chat, automatic lead "
    "capture and qualification, real-time analytics dashboard, and easy website integration. "
    "Pricing starts at $49/month for the Starter plan with a 14-day free trial."
)


# ---------------------------------------------------------------------------
# LangChain tool (used by drafting_node — traced by LangSmith automatically)
# ---------------------------------------------------------------------------
@tool
def rag_retrieve(query: str) -> str:
    """
    Retrieve relevant knowledge-base documents for a user query.
    Returns a formatted string of context passages ready for inclusion
    in an LLM prompt. Falls back to a default product description if
    the Qdrant collection has no relevant matches.
    """
    try:
        embedding = embedding_service.embed_text(query)
        docs = qdrant_service.search(
            query_vector=embedding,
            top_k=3,
            score_threshold=0.3,
        )
    except Exception as exc:
        logger.warning("RAG retrieve failed (%s) — using fallback", exc)
        docs = []

    if not docs:
        logger.debug("No Qdrant docs for query='%.60s' — fallback", query)
        return _FALLBACK_CONTEXT

    passages = []
    for doc in docs:
        source = doc.get("metadata", {}).get("source", "Knowledge Base")
        passages.append(f"[Source: {source}]\n{doc['content']}")

    logger.debug("RAG retrieved %d docs for query='%.60s'", len(docs), query)
    return "\n\n".join(passages)


# ---------------------------------------------------------------------------
# Legacy class (kept for /api/chat backwards compatibility)
# ---------------------------------------------------------------------------
class RAGService:
    def retrieve_context(self, query: str, top_k: int = 3, similarity_threshold: float = 0.3) -> List[Dict]:
        try:
            embedding = embedding_service.embed_text(query)
            return qdrant_service.search(
                query_vector=embedding,
                top_k=top_k,
                score_threshold=similarity_threshold,
            )
        except Exception as exc:
            logger.warning("RAG retrieve failed: %s", exc)
            return []

    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        additional_instructions: str = "",
    ) -> str:
        context = rag_retrieve.invoke(user_message)  # reuse the tool

        lead_capture_note = ""
        if "MUST ask for their contact information" in additional_instructions:
            lead_capture_note = (
                "\n\nIMPORTANT: After answering, ask for the user's email address naturally."
            )

        system_prompt = (
            f"You are a helpful AI sales agent for LeadFlow AI.{lead_capture_note}\n\n"
            f"=== KNOWLEDGE BASE ===\n{context}\n=== END ===\n\n"
            "Guidelines: be friendly, professional, concise (2-3 sentences)."
        )

        messages: List[Dict] = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        return groq_service.chat_completion(messages, temperature=0.3)


rag_service = RAGService()
