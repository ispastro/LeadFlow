import logging
import os
from typing import List

# Must be set before fastembed / huggingface_hub is imported.
# Prevents HF Hub from making network calls once the model is cached locally.
os.environ.setdefault("FASTEMBED_CACHE_PATH", ".fastembed_cache")

from fastembed import TextEmbedding

logger = logging.getLogger(__name__)

# Qdrant's recommended default model.
# 384-dim cosine space — compatible with existing Qdrant collections.
_MODEL_NAME = "BAAI/bge-small-en-v1.5"
_DIMENSION  = 384


class EmbeddingService:
    _instance = None
    _model: TextEmbedding = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.info("Loading FastEmbed model: %s", _MODEL_NAME)
            cls._model = TextEmbedding(model_name=_MODEL_NAME)
            logger.info("FastEmbed model ready (dim=%d)", _DIMENSION)
        return cls._instance

    def embed_text(self, text: str) -> List[float]:
        return list(self._model.embed([text]))[0].tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [emb.tolist() for emb in self._model.embed(texts)]

    @property
    def dimension(self) -> int:
        return _DIMENSION


# Singleton
embedding_service = EmbeddingService()
