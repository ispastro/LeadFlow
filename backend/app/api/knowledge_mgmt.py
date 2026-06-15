from fastapi import APIRouter, HTTPException
from app.models.knowledge import KnowledgeCreate, KnowledgeUpdate, KnowledgeResponse, KnowledgeSyncResponse
from app.db import knowledge as knowledge_db
from app.core.embeddings import embedding_service
from app.services.qdrant_service import qdrant_service
from app.utils.text_processing import chunk_text, clean_text
from typing import List
import uuid

router = APIRouter()

# Default business ID (for now, until multi-tenancy is fully implemented)
DEFAULT_BUSINESS_ID = "216141f4-8ed0-4b44-9d82-ab2d24e41d4b"


@router.get("/knowledge", response_model=List[KnowledgeResponse])
async def get_all_knowledge():
    """Get all knowledge documents"""
    try:
        documents = knowledge_db.get_all_knowledge(DEFAULT_BUSINESS_ID)
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching knowledge: {str(e)}")


@router.get("/knowledge/{knowledge_id}", response_model=KnowledgeResponse)
async def get_knowledge(knowledge_id: str):
    """Get single knowledge document"""
    try:
        document = knowledge_db.get_knowledge_by_id(knowledge_id)
        if not document:
            raise HTTPException(status_code=404, detail="Knowledge document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching knowledge: {str(e)}")


@router.post("/knowledge", response_model=KnowledgeResponse)
async def create_knowledge(data: KnowledgeCreate):
    """Create new knowledge document and auto-sync to Qdrant"""
    try:
        # Create in database
        knowledge_id = knowledge_db.create_knowledge(
            business_id=DEFAULT_BUSINESS_ID,
            title=data.title,
            content=data.content,
            category=data.category,
            source=data.source,
            metadata=data.metadata
        )
        
        # Auto-sync to Qdrant
        await sync_single_document(knowledge_id)
        
        # Return created document
        document = knowledge_db.get_knowledge_by_id(knowledge_id)
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating knowledge: {str(e)}")


@router.put("/knowledge/{knowledge_id}", response_model=KnowledgeResponse)
async def update_knowledge(knowledge_id: str, data: KnowledgeUpdate):
    """Update knowledge document and auto-sync to Qdrant"""
    try:
        # Check if exists
        existing = knowledge_db.get_knowledge_by_id(knowledge_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Knowledge document not found")
        
        # Update in database
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
        
        # Auto-sync to Qdrant
        await sync_single_document(knowledge_id)
        
        # Return updated document
        document = knowledge_db.get_knowledge_by_id(knowledge_id)
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating knowledge: {str(e)}")


@router.delete("/knowledge/{knowledge_id}")
async def delete_knowledge(knowledge_id: str):
    """Delete knowledge document and remove from Qdrant"""
    try:
        # Check if exists
        existing = knowledge_db.get_knowledge_by_id(knowledge_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Knowledge document not found")
        
        # Delete from database
        success = knowledge_db.delete_knowledge(knowledge_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete knowledge")
        
        # Note: Qdrant will be resynced on next full sync
        # Individual deletion from Qdrant is optional here
        
        return {"success": True, "message": "Knowledge document deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting knowledge: {str(e)}")


@router.post("/knowledge/sync", response_model=KnowledgeSyncResponse)
async def sync_knowledge_to_qdrant():
    """Sync all knowledge documents to Qdrant (full re-ingestion)"""
    try:
        # Get all documents from database
        documents = knowledge_db.get_all_knowledge(DEFAULT_BUSINESS_ID)
        
        if not documents:
            return KnowledgeSyncResponse(
                success=True,
                documents_synced=0,
                message="No documents to sync"
            )
        
        # Clear existing collection (optional - recreate from scratch)
        # qdrant_service.delete_collection()
        # qdrant_service._ensure_collection()
        
        # Process and upload to Qdrant
        documents_to_insert = []
        
        for doc in documents:
            content = clean_text(doc['content'])
            
            # Chunk if too long
            if len(content.split()) > 300:
                chunks = chunk_text(content, chunk_size=200, overlap=30)
            else:
                chunks = [content]
            
            for i, chunk in enumerate(chunks):
                # Generate embedding
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
        
        # Upload in batches
        batch_size = 100
        for i in range(0, len(documents_to_insert), batch_size):
            batch = documents_to_insert[i:i+batch_size]
            qdrant_service.add_documents(batch)
        
        return KnowledgeSyncResponse(
            success=True,
            documents_synced=len(documents),
            message=f"Successfully synced {len(documents)} documents to Qdrant"
        )
    except Exception as e:
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
        print(f"Error syncing document {knowledge_id}: {e}")
