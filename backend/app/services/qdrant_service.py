import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional
import uuid
import logging

logger = logging.getLogger(__name__)


class QdrantService:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Lazy initialization - actual connection happens on first use"""
        if QdrantService._initialized:
            return
        
        self.collection_name = "leadflow_knowledge"
        self.vector_size = 384
        self._client = None
        self._qdrant_url = None
        self._qdrant_api_key = None
        QdrantService._initialized = True
    
    def configure(self, qdrant_url: str, qdrant_api_key: str):
        """Configure Qdrant with credentials from settings"""
        self._qdrant_url = qdrant_url
        self._qdrant_api_key = qdrant_api_key
    
    def _ensure_connected(self):
        """Ensure client is connected (lazy connection)"""
        if self._client is not None:
            return
        
        if not self._qdrant_url or not self._qdrant_api_key:
            logger.warning("Qdrant credentials not configured")
            return
        
        try:
            self._client = QdrantClient(
                url=self._qdrant_url,
                api_key=self._qdrant_api_key,
                timeout=30
            )
            self._ensure_collection()
            logger.info(f"✅ Connected to Qdrant Cloud: {self._qdrant_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            self._client = None
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        if not self._client:
            return
        
        try:
            collections = self._client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                self._client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring collection: {e}")
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to Qdrant"""
        self._ensure_connected()
        if not self._client:
            raise Exception("Qdrant client not initialized")
        
        points = []
        for doc in documents:
            point = PointStruct(
                id=doc.get('id', str(uuid.uuid4())),
                vector=doc['embedding'],
                payload={
                    'content': doc['content'],
                    'source': doc.get('source', 'unknown'),
                    'category': doc.get('category', 'general'),
                    'metadata': doc.get('metadata', {})
                }
            )
            points.append(point)
        
        self._client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Added {len(points)} documents to Qdrant")
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 3,
        score_threshold: float = 0.5
    ) -> List[Dict]:
        """Search for similar documents"""
        self._ensure_connected()
        if not self._client:
            logger.warning("Qdrant client not initialized, returning empty results")
            return []
        
        try:
            results = self._client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=score_threshold
            )
            
            documents = []
            for result in results:
                documents.append({
                    'id': result.id,
                    'content': result.payload.get('content', ''),
                    'score': result.score,
                    'metadata': {
                        'source': result.payload.get('source', 'unknown'),
                        'category': result.payload.get('category', 'general')
                    }
                })
            
            return documents
        except Exception as e:
            logger.error(f"Qdrant search error: {e}")
            return []
    
    def collection_exists(self) -> bool:
        """Check if collection exists"""
        self._ensure_connected()
        if not self._client:
            return False
        
        try:
            collections = self._client.get_collections().collections
            return any(c.name == self.collection_name for c in collections)
        except Exception as e:
            logger.error(f"Error checking collection: {e}")
            return False
    
    def get_all_documents(self, limit: int = 100) -> List[Dict]:
        """Get all documents using scroll API"""
        self._ensure_connected()
        if not self._client:
            return []
        
        try:
            # Use scroll to get all points
            result = self._client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            documents = []
            for point in result[0]:  # result is (points, next_offset)
                documents.append({
                    'id': str(point.id),
                    'content': point.payload.get('content', ''),
                    'source': point.payload.get('source', 'unknown'),
                    'metadata': {
                        'category': point.payload.get('category', 'general')
                    },
                    'created_at': None  # Qdrant doesn't store timestamps by default
                })
            
            return documents
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            return []
    
    def count_documents(self) -> int:
        """Count total documents in collection"""
        self._ensure_connected()
        if not self._client:
            return 0
        
        try:
            info = self._client.get_collection(self.collection_name)
            return info.points_count
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0
    
    def get_collection_info(self) -> Dict:
        """Get collection information"""
        self._ensure_connected()
        if not self._client:
            return {}
        
        try:
            info = self._client.get_collection(self.collection_name)
            return {
                'name': self.collection_name,
                'points_count': info.points_count,
                'vector_size': self.vector_size,
                'status': info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}
    
    def delete_collection(self):
        """Delete the entire collection (use with caution)"""
        if not self._client:
            return
        
        try:
            self._client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")


# Singleton instance
qdrant_service = QdrantService()
