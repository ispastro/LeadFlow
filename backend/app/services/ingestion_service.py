import hashlib
import logging
import uuid
from typing import Optional

from app.core.embeddings import embedding_service
from app.services.qdrant_service import qdrant_service
from app.utils.text_processing import chunk_text, clean_text

logger = logging.getLogger(__name__)

# Chunk config
CHUNK_SIZE = 200   # words
CHUNK_OVERLAP = 30  # words


def _content_hash(content: str, filename: Optional[str] = None) -> str:
    """
    Produce a deterministic UUID v5 from the document content.
    UUID v5 is a name-based UUID — same input always produces the same UUID,
    giving us idempotent upserts in Qdrant.
    """
    blob = clean_text(content)
    if filename:
        blob = f"{filename}::{blob}"
    # UUID5 with DNS namespace gives a valid UUID from any string
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, blob))


def ingest_document(
    content: str,
    title: str,
    category: str = "general",
    source: str = "upload",
    filename: Optional[str] = None,
    extra_metadata: Optional[dict] = None,
) -> dict:
    """
    Core ingestion function — idempotent, chunk-aware, upsert-based.

    1. Compute a deterministic document_id from content hash.
    2. Clean and chunk the text.
    3. Embed each chunk.
    4. Upsert every chunk to Qdrant using a stable chunk-scoped ID
       (`{document_id}-{chunk_index}`). Because Qdrant upsert overwrites
       on ID collision, re-ingesting the same document is safe.

    Returns a summary dict suitable for the API response.
    """
    document_id = _content_hash(content, filename)
    cleaned = clean_text(content)

    chunks = (
        chunk_text(cleaned, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        if len(cleaned.split()) > CHUNK_SIZE
        else [cleaned]
    )

    points = []
    for i, chunk in enumerate(chunks):
        # Stable per-chunk ID: deterministic UUID from document_id + chunk index
        chunk_id = (
            str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{document_id}-{i}"))
            if len(chunks) > 1
            else document_id
        )

        embedding = embedding_service.embed_text(chunk)

        points.append({
            "id": chunk_id,
            "content": chunk,
            "embedding": embedding,
            "source": title,
            "category": category,
            "metadata": {
                "document_id": document_id,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "filename": filename or "",
                "source_type": source,
                **(extra_metadata or {}),
            },
        })

    qdrant_service.add_documents(points)   # add_documents uses upsert internally

    logger.info(
        "Ingested document | id=%s title='%s' chunks=%d",
        document_id, title, len(chunks),
    )

    return {
        "document_id": document_id,
        "title": title,
        "category": category,
        "chunks_indexed": len(chunks),
        "total_vectors": qdrant_service.count_documents(),
    }
