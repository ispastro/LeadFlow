from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from app.services.qdrant_service import qdrant_service
from app.core.embeddings import embedding_service
import uuid

router = APIRouter()


class DocumentCreate(BaseModel):
    content: str
    source: str
    category: Optional[str] = "general"


class DocumentUpdate(BaseModel):
    content: str
    source: str
    category: Optional[str] = "general"


@router.get("/knowledge")
async def get_all_documents():
    """Get all knowledge base documents from Qdrant"""
    try:
        documents = qdrant_service.get_all_documents(limit=100)
        count = qdrant_service.count_documents()
        return {
            "total": count,
            "documents": documents
        }
    except Exception as e:
        print(f"❌ Knowledge base error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/{doc_id}")
async def get_document(doc_id: str):
    """Get a specific document by ID"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/knowledge")
async def create_document(doc: DocumentCreate):
    """Create a new knowledge base document"""
    try:
        # Generate embedding
        embedding = embedding_service.embed_text(doc.content)
        
        documents = [{
            'id': str(uuid.uuid4()),
            'content': doc.content,
            'embedding': embedding,
            'source': doc.source,
            'category': doc.category
        }]
        
        qdrant_service.add_documents(documents)
        
        return {
            "message": "Document added successfully",
            "id": documents[0]['id']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/knowledge/{doc_id}")
async def update_document(doc_id: str, doc: DocumentUpdate):
    """Update an existing document"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/knowledge/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/knowledge/stats/count")
async def get_document_count():
    """Get total document count from Qdrant"""
    try:
        count = qdrant_service.count_documents()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
