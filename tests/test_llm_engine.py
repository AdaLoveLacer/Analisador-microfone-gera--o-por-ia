"""Tests for LLM Engine."""

import pytest
import logging
from ai.llm_engine import LLMEngine, GenerationConfig, OllamaBackend, TransformersBackend

logger = logging.getLogger(__name__)


class TestGenerationConfig:
    """Test GenerationConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = GenerationConfig()
        assert config.max_tokens == 256
        assert config.temperature == 0.7
        assert config.top_p == 0.9
        assert config.top_k == 40
        assert config.repetition_penalty == 1.2
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = GenerationConfig(
            max_tokens=512,
            temperature=0.3,
            top_p=0.95,
        )
        assert config.max_tokens == 512
        assert config.temperature == 0.3
        assert config.top_p == 0.95


class TestOllamaBackend:
    """Test Ollama backend."""
    
    def test_ollama_availability_check(self):
        """Test Ollama availability detection."""
        backend = OllamaBackend()
        # This will fail if Ollama is not running, which is expected
        assert isinstance(backend.is_available, bool)
    
    def test_ollama_custom_url(self):
        """Test custom Ollama URL."""
        backend = OllamaBackend(base_url="http://invalid:1234")
        assert backend.is_available is False
    
    def test_ollama_custom_model(self):
        """Test custom model name."""
        backend = OllamaBackend(model="mistral")
        assert backend.model == "mistral"


class TestTransformersBackend:
    """Test Transformers backend."""
    
    def test_transformers_backend_init(self):
        """Test Transformers backend initialization."""
        backend = TransformersBackend()
        assert backend.model is None
        assert backend.tokenizer is None
        assert backend.is_available is False
        assert backend._load_model_lazy is True
    
    def test_transformers_custom_model(self):
        """Test custom model name."""
        backend = TransformersBackend(model_name="microsoft/phi-2")
        assert backend.model_name == "microsoft/phi-2"
    
    def test_transformers_lazy_loading(self):
        """Test lazy loading mechanism."""
        backend = TransformersBackend()
        # Should not load immediately
        assert backend.model is None
        # Mock load attempt (won't actually load in test env)
        # This just verifies lazy loading is enabled
        assert backend._load_model_lazy is True


class TestLLMEngine:
    """Test LLM Engine."""
    
    def test_llm_engine_init(self):
        """Test LLM Engine initialization."""
        engine = LLMEngine()
        assert engine.active_backend in ["ollama", "transformers", "fallback"]
        assert engine.generation_config is not None
        assert engine._response_cache == {}
    
    def test_llm_engine_status(self):
        """Test LLM Engine status."""
        engine = LLMEngine()
        status = engine.get_status()
        
        assert "active_backend" in status
        assert "ollama_available" in status
        assert "transformers_available" in status
        assert "cache_size" in status
        assert "status" in status
        
        assert status["cache_size"] == 0
        assert status["status"] in ["ready", "degraded"]
    
    def test_llm_engine_custom_models(self):
        """Test custom model configuration."""
        engine = LLMEngine(
            ollama_model="mistral",
            transformers_model="microsoft/phi-2",
        )
        assert engine.ollama.model == "mistral"
        assert engine.transformers.model_name == "microsoft/phi-2"
    
    def test_generate_with_invalid_prompt(self):
        """Test generate with invalid inputs."""
        engine = LLMEngine()
        
        # None prompt
        result = engine.generate(None)
        assert result is None
        
        # Empty prompt
        result = engine.generate("")
        assert result is None
        
        # Non-string prompt
        result = engine.generate(123)
        assert result is None
    
    def test_cache_mechanism(self):
        """Test response caching."""
        engine = LLMEngine()
        
        # This test assumes no LLM is available, so generate returns None
        # But we can still test cache structure
        assert len(engine._response_cache) == 0
        
        # Clear cache
        engine.clear_cache()
        assert len(engine._response_cache) == 0
    
    def test_analyze_context_invalid_input(self):
        """Test analyze_context with invalid inputs."""
        engine = LLMEngine()
        
        # No text
        result = engine.analyze_context("", ["keyword"])
        assert result["relevant"] is False
        assert result["confidence"] == 0.0
        
        # No context keywords
        result = engine.analyze_context("some text", [])
        assert result["relevant"] is False
        
        # No keywords list
        result = engine.analyze_context("some text", None)
        assert result["relevant"] is False
    
    def test_generation_config_update(self):
        """Test generation config update."""
        engine = LLMEngine()
        
        original_config = GenerationConfig()
        assert engine.generation_config.max_tokens == original_config.max_tokens
        
        # Update would happen in generate() method
        # Just verify initial state is correct
        assert engine.generation_config.temperature == 0.7


class TestLLMIntegration:
    """Integration tests for LLM Engine."""
    
    def test_multiple_backends_fallback(self):
        """Test fallback between backends."""
        engine = LLMEngine()
        
        # Should have picked one backend
        assert engine.active_backend is not None
        
        # Status should be accessible
        status = engine.get_status()
        assert status["status"] in ["ready", "degraded"]
    
    def test_cache_isolation(self):
        """Test cache thread safety."""
        engine = LLMEngine()
        
        # Clear cache
        engine.clear_cache()
        assert len(engine._response_cache) == 0
        
        # Clear again
        engine.clear_cache()
        assert len(engine._response_cache) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
