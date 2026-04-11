from sentence_transformers import SentenceTransformer
from typing import List, Union


class EmbeddingService:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Load model once at startup
            print("Loading Sentence Transformer model...")
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Model loaded successfully!")
        return cls._instance
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embedding = self._model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (more efficient)"""
        embeddings = self._model.encode(texts, convert_to_tensor=False)
        return [emb.tolist() for emb in embeddings]
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension (384 for all-MiniLM-L6-v2)"""
        return 384


# Singleton instance
embedding_service = EmbeddingService()
