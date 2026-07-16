import io
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.api.auth import get_current_user
from app.services.ingestion_service import ingest_document

logger = logging.getLogger(__name__)
router = APIRouter()

# ---------------------------------------------------------------------------
# Supported upload MIME types → extraction handled inline
# ---------------------------------------------------------------------------
_TEXT_TYPES = {
    "text/plain",
    "text/markdown",
    "text/csv",
}
_PDF_TYPE  = "application/pdf"
_DOCX_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class IngestResponse(BaseModel):
    document_id: str
    title: str
    category: str
    chunks_indexed: int
    total_vectors: int
    message: str


class IngestTextRequest(BaseModel):
    title: str
    content: str
    category: str = "general"
    source: str = "api"


# ---------------------------------------------------------------------------
# Text extraction helpers
# ---------------------------------------------------------------------------

def _extract_text_from_pdf(data: bytes) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(
            page.extract_text() or "" for page in reader.pages
        ).strip()
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"PDF extraction failed: {exc}")


def _extract_text_from_docx(data: bytes) -> str:
    try:
        import docx
        doc = docx.Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"DOCX extraction failed: {exc}")


def _extract_text(data: bytes, content_type: str, filename: str) -> str:
    ct = content_type.split(";")[0].strip().lower()

    if ct in _TEXT_TYPES or filename.endswith((".txt", ".md", ".csv")):
        return data.decode("utf-8", errors="replace")

    if ct == _PDF_TYPE or filename.endswith(".pdf"):
        return _extract_text_from_pdf(data)

    if ct == _DOCX_TYPE or filename.endswith(".docx"):
        return _extract_text_from_docx(data)

    # Fallback — try to decode as UTF-8 text
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {ct}. Supported: .txt, .md, .pdf, .docx",
        )


# ---------------------------------------------------------------------------
# POST /ingest/file  — multipart upload
# ---------------------------------------------------------------------------

@router.post("/ingest/file", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(default=None),
    category: str = Form(default="general"),
    _: dict = Depends(get_current_user),
):
    """
    Upload a document (TXT, MD, PDF, DOCX) and index it in Qdrant.

    - Content is hashed to produce a stable `document_id`.
    - Re-uploading the same file silently overwrites the existing vectors
      (idempotent upsert — no duplicates).
    - Large documents are automatically chunked before embedding.
    """
    if file.size and file.size > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_UPLOAD_BYTES // (1024*1024)} MB.",
        )

    data = await file.read()

    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large.")

    if not data:
        raise HTTPException(status_code=422, detail="Uploaded file is empty.")

    text = _extract_text(data, file.content_type or "", file.filename or "")

    if not text.strip():
        raise HTTPException(status_code=422, detail="No extractable text found in the uploaded file.")

    doc_title = title or (file.filename or "Untitled").rsplit(".", 1)[0]

    try:
        result = ingest_document(
            content=text,
            title=doc_title,
            category=category,
            source="upload",
            filename=file.filename,
        )
    except Exception as exc:
        logger.error("File ingest failed | file=%s: %s", file.filename, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")

    return IngestResponse(
        **result,
        message=f"Indexed {result['chunks_indexed']} chunk(s) from '{doc_title}'.",
    )


# ---------------------------------------------------------------------------
# POST /ingest/text  — raw JSON body
# ---------------------------------------------------------------------------

@router.post("/ingest/text", response_model=IngestResponse)
async def ingest_text(
    body: IngestTextRequest,
    _: dict = Depends(get_current_user),
):
    """
    Ingest a plain-text document via JSON body.

    Useful for programmatic ingestion (webhooks, CRM sync, etc.).
    Same idempotency guarantee as the file endpoint.
    """
    if not body.content.strip():
        raise HTTPException(status_code=422, detail="Content must not be empty.")

    try:
        result = ingest_document(
            content=body.content,
            title=body.title,
            category=body.category,
            source=body.source,
        )
    except Exception as exc:
        logger.error("Text ingest failed | title=%s: %s", body.title, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")

    return IngestResponse(
        **result,
        message=f"Indexed {result['chunks_indexed']} chunk(s) from '{body.title}'.",
    )


# ---------------------------------------------------------------------------
# GET /ingest/status  — collection health check
# ---------------------------------------------------------------------------

@router.get("/ingest/status")
async def ingest_status(_: dict = Depends(get_current_user)):
    """Return current vector collection stats."""
    from app.services.qdrant_service import qdrant_service
    info = qdrant_service.get_collection_info()
    return {
        "collection": info.get("name"),
        "total_vectors": info.get("points_count", 0),
        "vector_size": info.get("vector_size"),
        "status": info.get("status"),
    }
