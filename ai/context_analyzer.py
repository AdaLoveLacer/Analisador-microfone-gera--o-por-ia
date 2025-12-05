"""Context analyzer for semantic similarity and contextual understanding."""

import numpy as np
import logging
from typing import List, Dict, Optional, Tuple
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """Simple cache for embeddings to avoid recomputing."""

    def __init__(self, max_size: int = 1000):
        """
        Initialize cache.

        Args:
            max_size: Maximum cache size
        """
        self.cache = {}
        self.max_size = max_size

    def get(self, text: str) -> Optional[np.ndarray]:
        """Get cached embedding."""
        return self.cache.get(text)

    def set(self, text: str, embedding: np.ndarray) -> None:
        """Set cached embedding."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simple FIFO)
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        self.cache[text] = embedding

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()


class ContextAnalyzer:
    """Analyzes context using semantic similarity."""

    def __init__(self, embedding_model_name: str = "distiluse-base-multilingual-cased-v2"):
        """
        Initialize ContextAnalyzer.

        Args:
            embedding_model_name: Name of sentence transformer model to use
        """
        self.embedding_model_name = embedding_model_name
        self.model = None  # Lazy load
        self.device = None
        self.embedding_cache = EmbeddingCache(max_size=1000)
        logger.info(f"ContextAnalyzer initialized (lazy loading)")

    def _load_model(self):
        """Load model lazily on first use - SEMPRE NA CPU para economizar VRAM."""
        if self.model is not None:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            import torch

            # IMPORTANTE: Forçar CPU para SentenceTransformer
            # O Whisper large-v3 precisa de ~3GB de VRAM
            # Deixar a GPU livre para o Whisper que é mais pesado
            self.device = "cpu"
            logger.info(f"Loading embedding model on CPU (GPU reserved for Whisper)")

            self.model = SentenceTransformer(self.embedding_model_name, device=self.device)
            logger.info(f"Embedding model loaded: {self.embedding_model_name} on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def analyze(
        self,
        text: str,
        context_keywords: Optional[List[str]] = None,
        min_confidence: float = 0.6,
    ) -> float:
        """
        Analyze context relevance.

        Args:
            text: Text to analyze
            context_keywords: Keywords that provide context
            min_confidence: Minimum confidence threshold

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not text or not context_keywords:
            return 0.0

        try:
            # Get embeddings
            text_embedding = self._get_embedding(text)
            if text_embedding is None:
                return 0.0

            # Calculate similarity with context keywords
            similarities = []
            for keyword in context_keywords:
                keyword_embedding = self._get_embedding(keyword)
                if keyword_embedding is None:
                    continue

                # Cosine similarity
                similarity = cosine_similarity(
                    [text_embedding], [keyword_embedding]
                )[0][0]
                similarities.append(similarity)

            if not similarities:
                return 0.0

            # Return average similarity
            avg_similarity = np.mean(similarities)
            return float(np.clip(avg_similarity, 0.0, 1.0))

        except Exception as e:
            logger.error(f"Error analyzing context: {e}")
            return 0.0

    def analyze_batch(
        self,
        texts: List[str],
        context_keywords: Optional[List[str]] = None,
        min_confidence: float = 0.6,
    ) -> List[float]:
        """
        Analyze context for multiple texts.

        Args:
            texts: List of texts to analyze
            context_keywords: Keywords that provide context
            min_confidence: Minimum confidence threshold

        Returns:
            List of confidence scores
        """
        return [
            self.analyze(text, context_keywords, min_confidence)
            for text in texts
        ]

    def semantic_similarity(
        self, text1: str, text2: str
    ) -> float:
        """
        Calculate semantic similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0.0 to 1.0)
        """
        try:
            embedding1 = self._get_embedding(text1)
            embedding2 = self._get_embedding(text2)

            if embedding1 is None or embedding2 is None:
                return 0.0

            similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            return float(np.clip(similarity, 0.0, 1.0))

        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def find_similar_texts(
        self, text: str, texts: List[str], top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find most similar texts.

        Args:
            text: Reference text
            texts: List of texts to compare with
            top_k: Number of top results to return

        Returns:
            List of tuples (text, similarity_score)
        """
        try:
            ref_embedding = self._get_embedding(text)
            if ref_embedding is None:
                return []

            similarities = []
            for other_text in texts:
                other_embedding = self._get_embedding(other_text)
                if other_embedding is None:
                    continue

                similarity = cosine_similarity([ref_embedding], [other_embedding])[0][0]
                similarities.append((other_text, float(similarity)))

            # Sort by similarity descending
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]

        except Exception as e:
            logger.error(f"Error finding similar texts: {e}")
            return []

    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Get embedding for text with caching.

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None if error
        """
        try:
            # Load model if not loaded
            self._load_model()
            
            # Check cache
            cached = self.embedding_cache.get(text)
            if cached is not None:
                return cached

            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)

            # Cache it
            self.embedding_cache.set(text, embedding)

            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def clear_cache(self) -> None:
        """Clear embedding cache."""
        self.embedding_cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "cached_embeddings": len(self.embedding_cache.cache),
            "max_size": self.embedding_cache.max_size,
        }
