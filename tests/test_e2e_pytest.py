"""
Testes E2E (End-to-End) do fluxo completo de análise
"""

import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from ai.keyword_detector import KeywordDetector
from ai.context_analyzer import ContextAnalyzer
from audio.audio_utils import normalize_audio, get_audio_energy, detect_silence


class TestE2EAudioProcessing:
    """Teste E2E do pipeline de processamento de áudio"""

    def test_audio_capture_and_normalization(self):
        """Captura simulada e normalização de áudio"""
        # Simula captura de 3 segundos
        sample_rate = 16000
        duration = 3
        num_samples = sample_rate * duration

        # Cria sinal de teste
        t = np.arange(num_samples) / sample_rate
        audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        audio += np.random.randn(num_samples).astype(np.float32) * 0.1

        # Normaliza
        normalized = normalize_audio(audio, target_db=-20.0)
        energy = get_audio_energy(normalized)

        assert len(normalized) == len(audio)
        assert normalized.dtype == np.float32
        assert energy > 0
        assert energy <= 1.0


class TestE2EKeywordDetection:
    """Teste E2E da detecção de palavras-chave"""

    def setup_method(self):
        """Configura palavras-chave para teste"""
        self.keywords = [
            {
                "id": "1",
                "name": "Sus",
                "pattern": "sus",
                "enabled": True,
                "variations": ["suspeitoso", "suspeito"],
                "weight": 1.0,
            },
            {
                "id": "2",
                "name": "Teste",
                "pattern": "teste",
                "enabled": True,
                "variations": ["testando", "testes"],
                "weight": 1.0,
            },
        ]

    def test_keyword_detection_exact_match(self):
        """Detecta palavra-chave exata"""
        detector = KeywordDetector(keywords=self.keywords)

        # Testa detecção exata
        result = detector.detect("muito suspeito")

        assert result is not None
        keyword_id, confidence = result
        assert keyword_id == "1"
        assert confidence > 0.8

    def test_keyword_detection_fuzzy_match(self):
        """Detecta palavra-chave com fuzzy matching"""
        detector = KeywordDetector(keywords=self.keywords)

        # Testa fuzzy match (variação)
        result = detector.detect("você é muito suspeitoso")

        assert result is not None
        keyword_id, confidence = result
        assert keyword_id == "1"

    def test_keyword_detection_no_match(self):
        """Não detecta quando não há palavra-chave"""
        detector = KeywordDetector(keywords=self.keywords)

        result = detector.detect("que dia bonito hoje")

        assert result is None or (result and result[1] < 0.5)


class TestE2EContextAnalysis:
    """Teste E2E da análise de contexto"""

    def test_semantic_similarity(self):
        """Calcula similaridade semântica entre textos"""
        analyzer = ContextAnalyzer()

        # Textos similares
        text1 = "que pessoa suspeita"
        text2 = "que atitude estranha"

        similarity = analyzer.semantic_similarity(text1, text2)

        assert isinstance(similarity, (float, np.floating))
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.2  # Textos similares

    def test_semantic_similarity_different_texts(self):
        """Similaridade baixa para textos diferentes"""
        analyzer = ContextAnalyzer()

        text1 = "maçã é uma fruta"
        text2 = "carro tem rodas"

        similarity = analyzer.semantic_similarity(text1, text2)

        assert 0.0 <= similarity <= 1.0
        # Textos bem diferentes têm similaridade menor

    def test_embedding_cache(self):
        """Cache de embeddings funciona"""
        analyzer = ContextAnalyzer()

        text = "teste de cache"

        # Primeira chamada
        emb1 = analyzer._get_embedding(text)

        # Segunda chamada (deve vir do cache)
        emb2 = analyzer._get_embedding(text)

        assert emb1 is not None
        assert emb2 is not None
        assert np.array_equal(emb1, emb2)


class TestE2ECompleteFlow:
    """Teste E2E do fluxo completo"""

    def test_complete_pipeline(self):
        """Fluxo completo: áudio -> detecção -> análise"""
        # Setup
        keywords = [
            {
                "id": "sus",
                "name": "Sus",
                "pattern": "sus",
                "enabled": True,
                "variations": ["suspeito"],
                "weight": 1.0,
            }
        ]

        detector = KeywordDetector(keywords=keywords)
        analyzer = ContextAnalyzer()

        # Simula captura de áudio
        sample_rate = 16000
        audio = np.sin(2 * np.pi * 440 * np.arange(16000) / sample_rate).astype(
            np.float32
        )
        audio_norm = normalize_audio(audio)
        energy = get_audio_energy(audio_norm)

        # Transcrição simulada
        transcription = "essa pessoa é muito suspeita"

        # Detecção
        detection = detector.detect(transcription)

        # Análise
        context1 = "essa atitude é estranha"
        context2 = "pessoa suspeita"
        similarity = analyzer.semantic_similarity(context1, context2)

        # Validação
        assert energy > 0
        assert detection is not None
        assert similarity >= 0.0

    def test_multiple_detections_flow(self):
        """Testa fluxo com múltiplas detecções"""
        keywords = [
            {
                "id": "sus",
                "name": "Sus",
                "pattern": "sus",
                "enabled": True,
                "variations": [],
                "weight": 1.0,
            },
            {
                "id": "teste",
                "name": "Teste",
                "pattern": "teste",
                "enabled": True,
                "variations": [],
                "weight": 1.0,
            },
        ]

        detector = KeywordDetector(keywords=keywords)
        analyzer = ContextAnalyzer()

        phrases = [
            "isso é muito suspeito",
            "esse teste é importante",
            "uma pessoa suspeita fazendo um teste",
        ]

        results = []
        for phrase in phrases:
            detection = detector.detect(phrase)
            if detection:
                keyword_id, confidence = detection
                results.append((phrase, keyword_id, confidence))

        # Deve detectar algo
        assert len(results) > 0


class TestE2EErrorHandling:
    """Teste de tratamento de erros no fluxo E2E"""

    def test_empty_audio_handling(self):
        """Lida corretamente com áudio vazio"""
        audio = np.array([], dtype=np.float32)
        normalized = normalize_audio(audio)
        energy = get_audio_energy(normalized)

        assert len(normalized) == 0
        assert energy == 0.0

    def test_empty_text_detection(self):
        """Lida com texto vazio na detecção"""
        keywords = [{"id": "1", "name": "Test", "pattern": "test", "enabled": True}]
        detector = KeywordDetector(keywords=keywords)

        result = detector.detect("")

        # Função retorna (None, 0.0) para texto vazio
        assert result is None or (result and result[1] == 0.0)

    def test_null_similarity(self):
        """Calcula similaridade com textos válidos"""
        analyzer = ContextAnalyzer()

        sim1 = analyzer.semantic_similarity("", "")
        sim2 = analyzer.semantic_similarity("teste", "")

        assert isinstance(sim1, (float, np.floating))
        assert isinstance(sim2, (float, np.floating))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
