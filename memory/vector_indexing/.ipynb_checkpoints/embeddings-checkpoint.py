# memory/vector_indexing/embeddings.py
import numpy as np
from sentence_transformers import SentenceTransformer
from common.config import settings
from common.logger import get_logger

logger = get_logger("embeddings")

class EmbeddingModel:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        model_name = settings.embedding_model or "all-MiniLM-L6-v2"
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding model loaded (dimension={self.dimension})")
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a text string"""
        return self.model.encode(text, convert_to_numpy=True)
    
    def get_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts"""
        return self.model.encode(texts, convert_to_numpy=True)
    
    def get_dimension(self) -> int:
        """Get embedding dimension size"""
        return self.dimension