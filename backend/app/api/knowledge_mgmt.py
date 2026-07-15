from fastapi import APIRouter, HTTPException, Depends
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate, KnowledgeResponse, KnowledgeSyncResponse
from app.db import knowledge as knowledge_db
from app.core.embeddings import embedding_service
from app.services.qdrant_service import qdrant_service
from app.utils.text_processing import chunk_text, clean_text
from app.api.auth import get_current_user
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Default business ID (until multi-tenancy is fully implemented)
DEFAULT_BUSINESS_ID = "216141f4-8ed0-4b44-9d82-ab2d24e41d4b"


@router.get("/knowledge", response_model=List[KnowledgeResponse])
async def get_all_knowledge(_: dict = Depends(get_current_user)):
    """Get all knowledge documents"""
    try:
        documents = knowledge_db.get_all_knowledge(DEFAULT_BUSINESS_ID)
        return documents
    except Exception as e:
        logger.error("Failed to fetch knowledge: %s", e)
        raise HTTPException(status_code=500, detail=f"Error fetching knowledge: {str(e)}")


@router.get("/knowledge/{knowledge_id}", response_model=KnowledgeResponse)
async def get_knowledge(knowledge_id: str, _: dict = Depends(get_current_user)):
    """Get single knowledge document"""
    try:
        document = knowledge_db.get_knowledge_by_id(knowledge_id)
        if not document:
            raise HTTPException(status_code=404, detail="Knowledge document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch knowledge %s: %s", knowledge_id, e)
        raise HTTPException(status_code=500, detail=f"Error fetching knowledge: {str(e)}")


@router.post("/knowledge", response_model=KnowledgeResponse)
async def create_knowledge(data: KnowledgeCreate, _: dict = Depends(get_current_user)):
    """Create new knowledge document and auto-sync to Qdrant"""
    try:
        knowledge_id = knowledge_db.create_knowledge(
            business_id=DEFAULT_BUSINESS_ID,
            title=data.title,
            content=data.content,
            category=data.category,
            source=data.source,
            metadata=data.metadata
        )
        await sync_single_document(knowledge_id)
        document = knowledge_db.get_knowledge_by_id(knowledge_id)
        return document
    except Exception as e:
        logger.error("Failed to create knowledge: %s", e)
        raise HTTPException(status_code=500, detail=f"Error creating knowledge: {str(e)}")


@router.put("/knowledge/{knowledge_id}", response_model=KnowledgeResponse)
async def update_knowledge(knowledge_id: str, data: KnowledgeUpdate, _: dict = Depends(get_current_user)):
    """Update knowledge document and auto-sync to Qdrant"""
    try:
        existing = knowledge_db.get_knowledge_by_id(knowledge_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Knowledge document not found")

        success = knowledge_db.update_knowledge(
            knowledge_id=knowledge_id,
            title=data.title,
            content=data.content,
            category=data.category,
            source=data.source,
            metadata=data.metadata
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update knowledge")

        await sync_single_document(knowledge_id)
        document = knowledge_db.get_knowledge_by_id(knowledge_id)
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update knowledge %s: %s", knowledge_id, e)
        raise HTTPException(status_code=500, detail=f"Error updating knowledge: {str(e)}")


@router.delete("/knowledge/{knowledge_id}")
async def delete_knowledge(knowledge_id: str, _: dict = Depends(get_current_user)):
    """Delete knowledge document and remove from Qdrant"""
    try:
        existing = knowledge_db.get_knowledge_by_id(knowledge_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Knowledge document not found")

        success = knowledge_db.delete_knowledge(knowledge_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete knowledge")

        return {"success": True, "message": "Knowledge document deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete knowledge %s: %s", knowledge_id, e)
        raise HTTPException(status_code=500, detail=f"Error deleting knowledge: {str(e)}")


@router.post("/knowledge/sync", response_model=KnowledgeSyncResponse)
async def sync_knowledge_to_qdrant(_: dict = Depends(get_current_user)):
    """Sync all knowledge documents to Qdrant (full re-ingestion)"""
    try:
        documents = knowledge_db.get_all_knowledge(DEFAULT_BUSINESS_ID)

        if not documents:
            return KnowledgeSyncResponse(
                success=True,
                documents_synced=0,
                message="No documents to sync"
            )

        documents_to_insert = []

        for doc in documents:
            content = clean_text(doc['content'])
            chunks = chunk_text(content, chunk_size=200, overlap=30) if len(content.split()) > 300 else [content]

            for i, chunk in enumerate(chunks):
                embedding = embedding_service.embed_text(chunk)
                qdrant_doc = {
                    'id': f"{doc['id']}-{i}" if len(chunks) > 1 else doc['id'],
                    'content': chunk,
                    'embedding': embedding,
                    'source': doc['title'],
                    'category': doc['category'],
                    'metadata': {
                        'knowledge_id': doc['id'],
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    }
                }
                documents_to_insert.append(qdrant_doc)

        batch_size = 100
        for i in range(0, len(documents_to_insert), batch_size):
            qdrant_service.add_documents(documents_to_insert[i:i + batch_size])

        return KnowledgeSyncResponse(
            success=True,
            documents_synced=len(documents),
            message=f"Successfully synced {len(documents)} documents to Qdrant"
        )
    except Exception as e:
        logger.error("Failed to sync knowledge to Qdrant: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error syncing knowledge: {str(e)}")


async def sync_single_document(knowledge_id: str):
    """Helper function to sync a single document to Qdrant"""
    try:
        doc = knowledge_db.get_knowledge_by_id(knowledge_id)
        if not doc:
            return
        
        content = clean_text(doc['content'])
        
        # Chunk if needed
        if len(content.split()) > 300:
            chunks = chunk_text(content, chunk_size=200, overlap=30)
        else:
            chunks = [content]
        
        documents_to_insert = []
        for i, chunk in enumerate(chunks):
            embedding = embedding_service.embed_text(chunk)
            
            qdrant_doc = {
                'id': f"{doc['id']}-{i}" if len(chunks) > 1 else doc['id'],
                'content': chunk,
                'embedding': embedding,
                'source': doc['title'],
                'category': doc['category'],
                'metadata': {
                    'knowledge_id': doc['id'],
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
            }
            documents_to_insert.append(qdrant_doc)
        
        qdrant_service.add_documents(documents_to_insert)
    except Exception as e:
        logger.error("Error syncing document %s: %s", knowledge_id, e)
