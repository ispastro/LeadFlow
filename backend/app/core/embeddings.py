"""
Lightweight embedding service using FastEmbed
- No torch dependency
- Fast startup (~1s vs 10s)
- Small model size
- Same quality as sentence-transformers
"""

from fastembed import TextEmbedding
from typing import List
import logging

logger = logging.getLogger(__name__)


class FastEmbeddingService:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.info("Loading FastEmbed model (all-MiniLM-L6-v2)...")
            cls._model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
            logger.info("Model loaded!")
        return cls._instance
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embeddings = list(self._model.embed([text]))
        return embeddings[0].tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = list(self._model.embed(texts))
        return [emb.tolist() for emb in embeddings]
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        return 384  # all-MiniLM-L6-v2 dimension


# Singleton instance
embedding_service = FastEmbeddingService()
