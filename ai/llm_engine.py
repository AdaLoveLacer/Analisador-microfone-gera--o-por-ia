"""LLM Engine for local AI processing.

IMPORTANTE: Este módulo está DESABILITADO por padrão para economizar memória.
Habilite manualmente via API ou interface quando precisar.

Supports multiple backends:
- Ollama (http://localhost:11434)
- Transformers (local model loading)
"""

import logging
import requests
import threading
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import gc

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
        # Don't check on init - only when enabled
    
    def check_availability(self) -> bool:
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
                return self.is_available
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
                return result.get("response", "").strip()
            return None
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return None


class TransformersBackend:
    """Backend for local Transformers model (Phi-2).
    
    DESABILITADO por padrão - consome muita memória!
    """
    
    def __init__(self, model_name: str = "microsoft/phi-2"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = "cpu"  # Padrão: CPU
        self.is_available = False
        self._loaded = False
    
    def set_device(self, device: str) -> bool:
        """Set device for model (cpu or cuda)."""
        device = device.lower()
        if device not in ["cpu", "cuda"]:
            logger.error(f"Invalid device: {device}")
            return False
        
        if device != self.device:
            old_device = self.device
            self.device = device
            logger.info(f"Transformers device changed: {old_device} -> {device}")
            
            if self._loaded:
                self.unload()
            return True
        return False
    
    def load_model(self) -> bool:
        """Load model on configured device."""
        if self.model is not None:
            return True
        
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # Check CUDA availability
            if self.device == "cuda" and not torch.cuda.is_available():
                logger.warning("CUDA not available, falling back to CPU")
                self.device = "cpu"
            
            logger.info(f"Loading Transformers model on {self.device.upper()}...")
            logger.warning("⚠️ This will use significant memory!")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
            )
            
            # Load model
            if self.device == "cuda":
                import torch
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16,
                    device_map="cuda",
                    trust_remote_code=True,
                )
                mem_allocated = torch.cuda.memory_allocated() / 1024**3
                logger.info(f"✓ Model loaded on CUDA (VRAM: {mem_allocated:.2f}GB)")
            else:
                import torch
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32,
                    device_map={"": "cpu"},
                    trust_remote_code=True,
                    low_cpu_mem_usage=True,
                )
                logger.info("✓ Model loaded on CPU")
            
            self.is_available = True
            self._loaded = True
            return True
        
        except ImportError:
            logger.warning("Transformers not available")
            return False
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def unload(self) -> bool:
        """Unload model from memory."""
        if self.model is not None:
            try:
                import torch
                
                del self.model
                del self.tokenizer
                self.model = None
                self.tokenizer = None
                self.is_available = False
                self._loaded = False
                
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                logger.info("✓ Transformers model unloaded from memory")
                return True
            except Exception as e:
                logger.error(f"Error unloading: {e}")
                return False
        return True
    
    def generate(self, prompt: str, config: GenerationConfig) -> Optional[str]:
        """Generate text using local model."""
        if not self._loaded or self.model is None:
            return None
        
        try:
            import torch
            
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
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
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = generated_text[len(prompt):].strip()
            
            return response
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return None


class LLMEngine:
    """Main LLM Engine - DESABILITADO por padrão."""
    
    def __init__(
        self,
        ollama_model: str = "phi",
        transformers_model: str = "microsoft/phi-2",
        ollama_url: str = "http://localhost:11434",
    ):
        self.generation_config = GenerationConfig()
        self._enabled = False  # DESABILITADO por padrão
        
        # Initialize backends (but don't load/check)
        self.ollama = OllamaBackend(base_url=ollama_url, model=ollama_model)
        self.transformers = TransformersBackend(model_name=transformers_model)
        
        self.active_backend = None
        self._response_cache: Dict[str, str] = {}
        self._cache_lock = threading.Lock()
        
        logger.info("LLMEngine initialized (DISABLED by default)")

    def is_enabled(self) -> bool:
        """Check if engine is enabled."""
        return self._enabled

    def set_enabled(self, enabled: bool, backend: str = "ollama") -> bool:
        """Enable or disable the LLM engine.
        
        Args:
            enabled: True to enable, False to disable
            backend: 'ollama' or 'transformers'
        """
        if enabled and not self._enabled:
            self._enabled = True
            
            # Try to activate the requested backend
            if backend == "ollama":
                if self.ollama.check_availability():
                    self.active_backend = "ollama"
                    logger.info("LLMEngine ENABLED with Ollama backend")
                    return True
                else:
                    logger.warning("Ollama not available")
                    self._enabled = False
                    return False
            
            elif backend == "transformers":
                if self.transformers.load_model():
                    self.active_backend = "transformers"
                    logger.info("LLMEngine ENABLED with Transformers backend")
                    return True
                else:
                    logger.warning("Transformers failed to load")
                    self._enabled = False
                    return False
            
        elif not enabled and self._enabled:
            self._enabled = False
            self.active_backend = None
            self.transformers.unload()
            self.clear_cache()
            logger.info("LLMEngine DISABLED")
            return True
        
        return True

    def set_device(self, device: str) -> bool:
        """Set device for Transformers backend."""
        return self.transformers.set_device(device)

    def unload(self) -> bool:
        """Unload all models from memory."""
        self._enabled = False
        self.active_backend = None
        result = self.transformers.unload()
        self.clear_cache()
        return result

    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7,
        use_cache: bool = True,
    ) -> Optional[str]:
        """Generate text from prompt."""
        if not self._enabled:
            logger.debug("LLMEngine is DISABLED")
            return None
        
        if not prompt:
            return None
        
        # Check cache
        if use_cache:
            cache_key = f"{prompt}_{max_tokens}_{temperature}"
            with self._cache_lock:
                if cache_key in self._response_cache:
                    return self._response_cache[cache_key]
        
        # Update config
        self.generation_config.max_tokens = max_tokens
        self.generation_config.temperature = temperature
        
        # Generate
        response = None
        if self.active_backend == "ollama":
            response = self.ollama.generate(prompt, self.generation_config)
        elif self.active_backend == "transformers":
            response = self.transformers.generate(prompt, self.generation_config)
        
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
        """Analyze context relevance using LLM."""
        if not self._enabled:
            return {
                "relevant": False,
                "confidence": 0.0,
                "explanation": "LLMEngine is DISABLED"
            }
        
        if not text or not context_keywords:
            return {
                "relevant": False,
                "confidence": 0.0,
                "explanation": "Missing text or keywords"
            }
        
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
        
        response_lower = response.lower()
        is_relevant = "yes" in response_lower
        
        confidence = 0.0
        try:
            numbers = [int(s) for s in response.split() if s.isdigit()]
            if numbers:
                confidence = min(100, max(0, numbers[0])) / 100.0
        except:
            pass
        
        return {
            "relevant": is_relevant,
            "confidence": confidence,
            "explanation": response.strip(),
        }

    def get_status(self) -> Dict[str, Any]:
        """Get LLM engine status."""
        status = {
            "enabled": self._enabled,
            "active_backend": self.active_backend,
            "ollama_available": self.ollama.is_available,
            "transformers_loaded": self.transformers._loaded,
            "transformers_device": self.transformers.device,
            "cache_size": len(self._response_cache),
        }
        
        if self.transformers._loaded and self.transformers.device == "cuda":
            try:
                import torch
                status["vram_allocated_gb"] = round(torch.cuda.memory_allocated() / 1024**3, 2)
            except:
                pass
        
        return status

    def clear_cache(self) -> None:
        """Clear response cache."""
        with self._cache_lock:
            self._response_cache.clear()


# Global instance (DISABLED by default)
_global_engine: Optional[LLMEngine] = None


def get_llm_engine() -> LLMEngine:
    """Get global LLMEngine instance."""
    global _global_engine
    if _global_engine is None:
        _global_engine = LLMEngine()
    return _global_engine
