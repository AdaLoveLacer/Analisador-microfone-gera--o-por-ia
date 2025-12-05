"""Context analyzer for semantic similarity and contextual understanding.

IMPORTANTE: Este módulo está DESABILITADO por padrão para economizar memória.
Habilite manualmente via API ou interface quando precisar.
"""

import numpy as np
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """Simple cache for embeddings to avoid recomputing."""

    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size

    def get(self, text: str) -> Optional[np.ndarray]:
        return self.cache.get(text)

    def set(self, text: str, embedding: np.ndarray) -> None:
        if len(self.cache) >= self.max_size:
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        self.cache[text] = embedding

    def clear(self) -> None:
        self.cache.clear()


class ContextAnalyzer:
    """Analyzes context using semantic similarity.
    
    DESABILITADO por padrão - habilite via set_enabled(True)
    """

    def __init__(self, embedding_model_name: str = "distiluse-base-multilingual-cased-v2"):
        self.embedding_model_name = embedding_model_name
        self.model = None
        self.device = "cpu"  # Padrão: CPU
        self.embedding_cache = EmbeddingCache(max_size=1000)
        self._enabled = False  # DESABILITADO por padrão
        self._loaded = False
        logger.info(f"ContextAnalyzer initialized (DISABLED by default)")

    def is_enabled(self) -> bool:
        """Check if analyzer is enabled."""
        return self._enabled

    def is_loaded(self) -> bool:
        """Check if model is loaded in memory."""
        return self._loaded and self.model is not None

    def set_enabled(self, enabled: bool) -> bool:
        """Enable or disable the analyzer.
        
        Args:
            enabled: True to enable, False to disable
            
        Returns:
            True if operation succeeded
        """
        if enabled and not self._enabled:
            self._enabled = True
            logger.info("ContextAnalyzer ENABLED (model will load on first use)")
        elif not enabled and self._enabled:
            self._enabled = False
            self.unload()
            logger.info("ContextAnalyzer DISABLED")
        return True

    def set_device(self, device: str) -> bool:
        """Set device for model (cpu or cuda).
        
        Args:
            device: 'cpu' or 'cuda'
            
        Returns:
            True if device was changed (requires reload)
        """
        device = device.lower()
        if device not in ["cpu", "cuda"]:
            logger.error(f"Invalid device: {device}. Use 'cpu' or 'cuda'")
            return False
        
        if device != self.device:
            old_device = self.device
            self.device = device
            logger.info(f"ContextAnalyzer device changed: {old_device} -> {device}")
            
            # If model is loaded, need to reload on new device
            if self._loaded:
                logger.info("Model was loaded, unloading for device change...")
                self.unload()
            return True
        return False

    def _load_model(self) -> bool:
        """Load model on configured device."""
        if not self._enabled:
            logger.warning("Cannot load model: ContextAnalyzer is DISABLED")
            return False
            
        if self.model is not None:
            return True
        
        try:
            from sentence_transformers import SentenceTransformer
            import torch

            logger.info(f"Loading embedding model on {self.device.upper()}...")
            
            # Check CUDA availability
            if self.device == "cuda" and not torch.cuda.is_available():
                logger.warning("CUDA not available, falling back to CPU")
                self.device = "cpu"

            self.model = SentenceTransformer(self.embedding_model_name, device=self.device)
            self._loaded = True
            
            # Log memory usage
            if self.device == "cuda":
                mem_allocated = torch.cuda.memory_allocated() / 1024**3
                logger.info(f"✓ Embedding model loaded on CUDA (VRAM: {mem_allocated:.2f}GB)")
            else:
                logger.info(f"✓ Embedding model loaded on CPU")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self._loaded = False
            return False

    def unload(self) -> bool:
        """Unload model from memory."""
        if self.model is not None:
            try:
                import torch
                import gc
                
                del self.model
                self.model = None
                self._loaded = False
                self.embedding_cache.clear()
                
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                logger.info("✓ Embedding model unloaded from memory")
                return True
            except Exception as e:
                logger.error(f"Error unloading model: {e}")
                return False
        return True

    def get_status(self) -> Dict:
        """Get analyzer status."""
        status = {
            "enabled": self._enabled,
            "loaded": self._loaded,
            "device": self.device,
            "model_name": self.embedding_model_name,
            "cache_size": len(self.embedding_cache.cache),
        }
        
        if self._loaded and self.device == "cuda":
            try:
                import torch
                status["vram_allocated_gb"] = round(torch.cuda.memory_allocated() / 1024**3, 2)
            except:
                pass
        
        return status

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding for text."""
        if not self._enabled:
            return None
            
        # Check cache
        cached = self.embedding_cache.get(text)
        if cached is not None:
            return cached

        # Load model if needed
        if not self._load_model():
            return None

        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            self.embedding_cache.set(text, embedding)
            return embedding
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return None

    def get_embeddings_batch(self, texts: List[str]) -> Optional[np.ndarray]:
        """Get embeddings for multiple texts."""
        if not self._enabled:
            return None
            
        if not self._load_model():
            return None

        try:
            return self.model.encode(texts, convert_to_numpy=True)
        except Exception as e:
            logger.error(f"Batch embedding error: {e}")
            return None

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        if not self._enabled:
            return 0.0
            
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)

        if emb1 is None or emb2 is None:
            return 0.0

        try:
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity([emb1], [emb2])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Similarity error: {e}")
            return 0.0

    def find_most_similar(
        self, query: str, candidates: List[str], top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """Find most similar texts."""
        if not self._enabled or not candidates:
            return []

        query_emb = self.get_embedding(query)
        if query_emb is None:
            return []

        candidate_embs = self.get_embeddings_batch(candidates)
        if candidate_embs is None:
            return []

        try:
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity([query_emb], candidate_embs)[0]
            
            results = list(zip(candidates, similarities))
            results.sort(key=lambda x: x[1], reverse=True)
            
            return [(text, float(score)) for text, score in results[:top_k]]
        except Exception as e:
            logger.error(f"Find similar error: {e}")
            return []

    def analyze_context(
        self,
        text: str,
        context_keywords: List[str],
        threshold: float = 0.6,
    ) -> Dict:
        """Analyze if text matches context keywords."""
        if not self._enabled:
            return {
                "matches": False,
                "confidence": 0.0,
                "best_match": None,
                "reason": "ContextAnalyzer is DISABLED"
            }

        if not text or not context_keywords:
            return {
                "matches": False,
                "confidence": 0.0,
                "best_match": None,
                "reason": "Missing text or keywords"
            }

        results = self.find_most_similar(text, context_keywords, top_k=1)
        
        if not results:
            return {
                "matches": False,
                "confidence": 0.0,
                "best_match": None,
                "reason": "No similarity found"
            }

        best_keyword, score = results[0]
        matches = score >= threshold

        return {
            "matches": matches,
            "confidence": float(score),
            "best_match": best_keyword if matches else None,
            "all_scores": {kw: float(s) for kw, s in results},
            "threshold": threshold,
        }

    def analyze(self, text: str, context_keywords: List[str]) -> float:
        """Shortcut method for backward compatibility.
        
        Returns confidence score (0.0 if disabled).
        """
        if not self._enabled:
            return 0.0
        
        result = self.analyze_context(text, context_keywords)
        return result.get("confidence", 0.0)


# Global instance (DISABLED by default)
_global_analyzer: Optional[ContextAnalyzer] = None

def get_context_analyzer() -> ContextAnalyzer:
    """Get global ContextAnalyzer instance."""
    global _global_analyzer
    if _global_analyzer is None:
        _global_analyzer = ContextAnalyzer()
    return _global_analyzer
