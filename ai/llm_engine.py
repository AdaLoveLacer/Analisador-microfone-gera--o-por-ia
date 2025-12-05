"""LLM Engine for local AI processing with Phi-2 model.

Supports multiple backends:
- Ollama (http://localhost:11434)
- Transformers (local model loading)
- Fallback to sentence-transformers for embeddings
"""

import logging
import requests
import threading
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repetition_penalty: float = 1.2


class OllamaBackend:
    """Backend for Ollama LLM service."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "phi"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.is_available = False
        self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=2
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "").split(":")[0] for m in models]
                self.is_available = self.model in model_names
                if self.is_available:
                    logger.info(f"✓ Ollama backend available with model: {self.model}")
                else:
                    logger.warning(f"✗ Ollama available but model '{self.model}' not found")
                    logger.info(f"  Available models: {model_names}")
                return True
            return False
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            return False
    
    def generate(self, prompt: str, config: GenerationConfig) -> Optional[str]:
        """Generate text using Ollama."""
        if not self.is_available:
            return None
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": config.temperature,
                    "top_p": config.top_p,
                    "top_k": config.top_k,
                    "num_predict": config.max_tokens,
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                logger.debug(f"Ollama generated: {generated_text[:100]}...")
                return generated_text
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logger.debug(f"Ollama request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return None


class TransformersBackend:
    """Backend for local Transformers model (Phi-2)."""
    
    def __init__(self, model_name: str = "microsoft/phi-2"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = None
        self.is_available = False
        self._load_model_lazy = True  # Load on first use
    
    def _load_model(self) -> bool:
        """Load model lazily on first use - FORÇA CPU para economizar VRAM para o Whisper."""
        if self.model is not None:
            return True
        
        if not self._load_model_lazy:
            return False
        
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # IMPORTANTE: Forçar CPU para o modelo Transformers
            # O Whisper large precisa de toda VRAM disponível
            self.device = "cpu"
            logger.info(f"Loading Phi-2 model on CPU (GPU reserved for Whisper)")
            
            # Load tokenizer
            logger.info(f"Loading tokenizer: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
            )
            
            # Load model on CPU
            logger.info(f"Loading model: {self.model_name} on CPU")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,  # CPU usa float32
                device_map={"": "cpu"},  # Forçar CPU
                trust_remote_code=True,
                low_cpu_mem_usage=True,  # Economizar RAM
            )
            
            self.is_available = True
            logger.info("✓ Transformers backend ready (Phi-2 on CPU)")
            return True
        
        except ImportError:
            logger.warning("Transformers not available - install with: pip install transformers torch")
            self._load_model_lazy = False
            return False
        except Exception as e:
            logger.error(f"Failed to load Transformers model: {e}")
            self._load_model_lazy = False
            return False
    
    def generate(self, prompt: str, config: GenerationConfig) -> Optional[str]:
        """Generate text using local Transformers model."""
        if not self._load_model():
            return None
        
        try:
            import torch
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=config.max_tokens,
                    temperature=config.temperature,
                    top_p=config.top_p,
                    top_k=config.top_k,
                    repetition_penalty=config.repetition_penalty,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            
            # Decode
            generated_text = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )
            
            # Extract only new tokens (remove prompt)
            response = generated_text[len(prompt):].strip()
            logger.debug(f"Transformers generated: {response[:100]}...")
            
            return response
        
        except Exception as e:
            logger.error(f"Transformers generation error: {e}")
            return None


class LLMEngine:
    """Main LLM Engine coordinating multiple backends."""
    
    def __init__(
        self,
        ollama_model: str = "phi",
        transformers_model: str = "microsoft/phi-2",
        ollama_url: str = "http://localhost:11434",
    ):
        """
        Initialize LLM Engine.
        
        Args:
            ollama_model: Model name in Ollama
            transformers_model: HuggingFace model identifier
            ollama_url: Ollama service URL
        """
        self.generation_config = GenerationConfig()
        
        # Initialize backends
        self.ollama = OllamaBackend(base_url=ollama_url, model=ollama_model)
        self.transformers = TransformersBackend(model_name=transformers_model)
        
        # Determine active backend
        self.active_backend = None
        if self.ollama.is_available:
            self.active_backend = "ollama"
            logger.info("LLM Engine using Ollama backend")
        elif self.transformers._load_model():
            self.active_backend = "transformers"
            logger.info("LLM Engine using Transformers backend")
        else:
            logger.warning("No LLM backend available - using sentence-transformers fallback")
            self.active_backend = "fallback"
        
        # Cache for responses
        self._response_cache: Dict[str, str] = {}
        self._cache_lock = threading.Lock()
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7,
        use_cache: bool = True,
    ) -> Optional[str]:
        """
        Generate text from prompt.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature (0.0-2.0)
            use_cache: Use response cache
        
        Returns:
            Generated text or None if failed
        """
        if not prompt or not isinstance(prompt, str):
            return None
        
        # Check cache
        if use_cache:
            cache_key = f"{prompt}_{max_tokens}_{temperature}"
            with self._cache_lock:
                if cache_key in self._response_cache:
                    logger.debug("Cache hit")
                    return self._response_cache[cache_key]
        
        # Update config
        self.generation_config.max_tokens = max_tokens
        self.generation_config.temperature = temperature
        
        # Generate with active backend
        response = None
        
        if self.active_backend == "ollama":
            response = self.ollama.generate(prompt, self.generation_config)
        elif self.active_backend == "transformers":
            response = self.transformers.generate(prompt, self.generation_config)
        else:
            logger.warning("No active LLM backend")
            return None
        
        # Cache result
        if response and use_cache:
            cache_key = f"{prompt}_{max_tokens}_{temperature}"
            with self._cache_lock:
                self._response_cache[cache_key] = response
        
        return response
    
    def analyze_context(
        self,
        text: str,
        context_keywords: List[str],
        threshold: float = 0.6,
    ) -> Dict[str, Any]:
        """
        Analyze context relevance using LLM.
        
        Args:
            text: Text to analyze
            context_keywords: Keywords providing context
            threshold: Confidence threshold (0.0-1.0)
        
        Returns:
            Dict with analysis results
        """
        if not text or not context_keywords:
            return {
                "relevant": False,
                "confidence": 0.0,
                "explanation": "Missing text or context keywords"
            }
        
        # Build prompt for context analysis
        keywords_str = ", ".join(context_keywords)
        prompt = f"""Analyze if this text is related to these context keywords.
Text: "{text}"
Context keywords: {keywords_str}

Is the text relevant to the context? Answer with ONLY: Yes or No
Confidence (0-100): """
        
        response = self.generate(prompt, max_tokens=50, temperature=0.3)
        
        if not response:
            return {
                "relevant": False,
                "confidence": 0.0,
                "explanation": "Generation failed"
            }
        
        # Parse response
        response_lower = response.lower()
        is_relevant = "yes" in response_lower
        
        # Extract confidence if provided
        confidence = 0.0
        if "confidence" in response_lower or any(str(i) in response for i in range(100)):
            try:
                # Extract numbers
                numbers = [int(s) for s in response.split() if s.isdigit()]
                if numbers:
                    confidence = min(100, max(0, numbers[0])) / 100.0
            except:
                pass
        
        return {
            "relevant": is_relevant,
            "confidence": confidence,
            "explanation": response.strip(),
            "raw_response": response
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get LLM engine status."""
        return {
            "active_backend": self.active_backend,
            "ollama_available": self.ollama.is_available,
            "transformers_available": self.transformers.is_available,
            "cache_size": len(self._response_cache),
            "status": "ready" if self.active_backend != "fallback" else "degraded"
        }
    
    def clear_cache(self) -> None:
        """Clear response cache."""
        with self._cache_lock:
            self._response_cache.clear()
        logger.info("LLM response cache cleared")
