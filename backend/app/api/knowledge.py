from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from app.db import knowledge_base as kb_db
from app.core.embeddings import embedding_service

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
    """Get all knowledge base documents"""
    try:
        documents = kb_db.get_all_documents()
        return {
            "documents": documents,
            "total": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/{doc_id}")
async def get_document(doc_id: str):
    """Get a specific document by ID"""
    try:
        document = kb_db.get_document_by_id(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge")
async def create_document(doc: DocumentCreate):
    """Create a new knowledge base document"""
    try:
        embedding = embedding_service.embed_text(doc.content)
        
        metadata = {
            "source": doc.source,
            "category": doc.category
        }
        
        result = kb_db.insert_document(
            content=doc.content,
            embedding=embedding,
            metadata=metadata,
            source=doc.source
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/knowledge/{doc_id}")
async def update_document(doc_id: str, doc: DocumentUpdate):
    """Update an existing document"""
    try:
        embedding = embedding_service.embed_text(doc.content)
        
        metadata = {
            "source": doc.source,
            "category": doc.category
        }
        
        result = kb_db.update_document(
            doc_id=doc_id,
            content=doc.content,
            embedding=embedding,
            metadata=metadata,
            source=doc.source
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/knowledge/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document"""
    try:
        deleted = kb_db.delete_document(doc_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/stats/count")
async def get_document_count():
    """Get total document count"""
    try:
        count = kb_db.count_documents()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
