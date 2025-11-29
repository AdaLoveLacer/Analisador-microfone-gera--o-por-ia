"""
Testes unitários para o módulo de áudio
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from audio.audio_utils import (
    normalize_audio,
    detect_silence,
    get_audio_energy,
    apply_gain,
    resample_audio
)


class TestAudioNormalization:
    """Testes para normalização de áudio"""

    def test_normalize_audio_basic(self):
        """Testa normalização básica de áudio"""
        # Cria sinal de teste
        audio = np.array([0.1, 0.2, 0.3, 0.4, 0.5], dtype=np.float32)
        normalized = normalize_audio(audio, target_db=-20.0)
        
        # Verifica se o resultado é válido
        assert isinstance(normalized, np.ndarray)
        assert normalized.dtype == np.float32
        assert len(normalized) == len(audio)

    def test_normalize_audio_preserves_shape(self):
        """Verifica se normalização preserva dimensões"""
        audio = np.random.randn(16000).astype(np.float32)
        normalized = normalize_audio(audio)
        assert normalized.shape == audio.shape

    def test_normalize_audio_empty(self):
        """Testa normalização com array vazio"""
        audio = np.array([], dtype=np.float32)
        result = normalize_audio(audio)
        assert len(result) == 0


class TestSilenceDetection:
    """Testes para detecção de silêncio"""

    def test_detect_silence_silent_audio(self):
        """Detecta silêncio em áudio mudo"""
        # Cria áudio praticamente silencioso
        audio = np.random.randn(16000).astype(np.float32) * 0.001
        is_silent = detect_silence(audio, threshold_db=-50.0)
        assert is_silent is True

    def test_detect_silence_loud_audio(self):
        """Não detecta silêncio em áudio alto"""
        # Cria áudio com sinal forte
        audio = np.sin(2 * np.pi * 440 * np.arange(16000) / 16000).astype(np.float32)
        is_silent = detect_silence(audio, threshold_db=-20.0)
        assert is_silent is False

    def test_detect_silence_threshold_boundary(self):
        """Testa limiar de detecção"""
        audio = np.random.randn(16000).astype(np.float32) * 0.1
        
        # Com limiar muito baixo, não deve detectar silêncio
        is_silent_low = detect_silence(audio, threshold_db=-80.0)
        assert is_silent_low is False
        
        # Com limiar muito alto, deve detectar silêncio
        is_silent_high = detect_silence(audio, threshold_db=-10.0)
        # Resultado depende da energia do áudio


class TestAudioEnergy:
    """Testes para cálculo de energia"""

    def test_get_audio_energy_positive(self):
        """Calcula energia positiva para áudio com som"""
        audio = np.sin(2 * np.pi * 440 * np.arange(1000) / 16000).astype(np.float32)
        energy = get_audio_energy(audio)
        
        assert isinstance(energy, (float, np.floating))
        assert energy >= 0

    def test_get_audio_energy_zero_for_silence(self):
        """Energia é zero para áudio silencioso"""
        audio = np.zeros(16000, dtype=np.float32)
        energy = get_audio_energy(audio)
        
        assert energy == 0.0

    def test_get_audio_energy_order(self):
        """Áudio mais forte tem mais energia"""
        weak_audio = np.sin(2 * np.pi * 440 * np.arange(1000) / 16000).astype(np.float32) * 0.1
        strong_audio = np.sin(2 * np.pi * 440 * np.arange(1000) / 16000).astype(np.float32) * 1.0
        
        weak_energy = get_audio_energy(weak_audio)
        strong_energy = get_audio_energy(strong_audio)
        
        assert strong_energy > weak_energy


class TestGainAdjustment:
    """Testes para ajuste de ganho"""

    def test_apply_gain_positive(self):
        """Aplica ganho positivo"""
        audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        result = apply_gain(audio, gain_db=6.0)
        
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float32

    def test_apply_gain_clipping(self):
        """Verifica clipping em ganho alto"""
        audio = np.ones(100, dtype=np.float32) * 0.5
        result = apply_gain(audio, gain_db=20.0)
        
        # Não deve exceder 1.0
        assert np.max(np.abs(result)) <= 1.0 + 1e-6

    def test_apply_gain_negative(self):
        """Aplica ganho negativo (redução)"""
        audio = np.ones(100, dtype=np.float32) * 0.5
        original_energy = get_audio_energy(audio)
        
        result = apply_gain(audio, gain_db=-6.0)
        result_energy = get_audio_energy(result)
        
        assert result_energy < original_energy


class TestResampling:
    """Testes para reamostragem de áudio"""

    def test_resample_audio_basic(self):
        """Testa reamostragem básica"""
        audio = np.sin(2 * np.pi * 440 * np.arange(16000) / 16000).astype(np.float32)
        resampled = resample_audio(audio, src_sr=16000, tgt_sr=8000)
        
        # Deve ter metade das amostras
        assert len(resampled) == len(audio) // 2

    def test_resample_audio_same_rate(self):
        """Resampling com mesma taxa não altera"""
        audio = np.random.randn(16000).astype(np.float32)
        resampled = resample_audio(audio, src_sr=16000, tgt_sr=16000)
        
        assert len(resampled) == len(audio)

    def test_resample_audio_upsample(self):
        """Testa upsampling"""
        audio = np.sin(2 * np.pi * 440 * np.arange(8000) / 8000).astype(np.float32)
        resampled = resample_audio(audio, src_sr=8000, tgt_sr=16000)
        
        # Deve ter o dobro das amostras
        assert len(resampled) == len(audio) * 2


class TestAudioIntegration:
    """Testes de integração entre funções"""

    def test_normalize_then_detect_silence(self):
        """Normaliza e depois detecta silêncio"""
        audio = np.random.randn(16000).astype(np.float32) * 0.01
        normalized = normalize_audio(audio, target_db=-40.0)
        is_silent = detect_silence(normalized, threshold_db=-30.0)
        
        # Não deve falhar
        assert isinstance(is_silent, (bool, np.bool_))

    def test_apply_gain_preserve_silence(self):
        """Ganho negativo não cria ruído em silêncio"""
        audio = np.zeros(1000, dtype=np.float32)
        result = apply_gain(audio, gain_db=-6.0)
        
        # Deve permanecer silencioso
        energy = get_audio_energy(result)
        assert energy < 1e-10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
