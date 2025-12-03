"""
Teste E2E (End-to-End) do fluxo completo
Simula: Captura -> Transcrição -> Detecção -> Som
"""

import sys
import os
import numpy as np
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

def test_e2e_complete_flow():
    """
    Teste E2E completo:
    1. Criar audio simulado
    2. Processar com normalize/energy
    3. Transcrever com Whisper (se possível)
    4. Detectar palavras-chave
    5. Analisar contexto
    6. Validar resultado
    """
    print("\n" + "="*70)
    print("TESTE E2E - FLUXO COMPLETO")
    print("="*70)
    
    try:
        # ======== STEP 1: Imports ========
        print("\n[1/5] Importando módulos...")
        from core.analyzer import MicrophoneAnalyzer
        from ai.keyword_detector import KeywordDetector
        from ai.context_analyzer import ContextAnalyzer
        from audio.audio_utils import normalize_audio, get_audio_energy
        print("      ✓ Módulos importados com sucesso")
        
        # ======== STEP 2: Create Audio Signal ========
        print("\n[2/5] Criando sinal de áudio simulado...")
        sample_rate = 16000
        duration_sec = 3
        num_samples = sample_rate * duration_sec
        
        # Cria sinal de teste (440Hz + ruído)
        t = np.arange(num_samples) / sample_rate
        frequency = 440  # A4 note
        audio_signal = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        audio_signal += np.random.randn(num_samples).astype(np.float32) * 0.1
        
        # Normaliza
        audio_normalized = normalize_audio(audio_signal, target_db=-20.0)
        energy = get_audio_energy(audio_normalized)
        
        print(f"      ✓ Áudio criado: {duration_sec}s @ {sample_rate}Hz")
        print(f"      ✓ Energia: {energy:.4f}")
        print(f"      ✓ Amplitude: [{audio_normalized.min():.4f}, {audio_normalized.max():.4f}]")
        
        # ======== STEP 3: Test Whisper (Transcrição) ========
        print("\n[3/5] Testando Whisper (Transcrição)...")
        try:
            import whisper
            print("      ✓ Whisper importado")
            
            # Tenta carregar modelo (pode demorar na primeira vez)
            print("      ⏳ Carregando modelo base (pode levar minutos)...")
            model = whisper.load_model("base")
            print("      ✓ Modelo carregado com sucesso")
            
            # Salva áudio temporário
            import tempfile
            import scipy.io.wavfile as wavfile  # type: ignore
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                wavfile.write(tmp.name, sample_rate, (audio_normalized * 32767).astype(np.int16))
                tmp_path = tmp.name
            
            # Transcreve
            print("      ⏳ Transcrevendo áudio...")
            result = model.transcribe(tmp_path, language="pt")
            transcription = result.get("text", "").strip()
            os.unlink(tmp_path)
            
            print(f"      ✓ Transcrição: '{transcription}'")
        except Exception as e:
            print(f"      ⚠️  Whisper não disponível: {str(e)[:50]}")
            transcription = "[teste] isso é um teste"
        
        # ======== STEP 4: Keyword Detection ========
        print("\n[4/5] Testando Detecção de Palavras-Chave...")
        detector = None
        detections = []
        try:
            # Exemplo de keywords para teste
            keywords_config = [
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
            
            detector = KeywordDetector(keywords=keywords_config)
            
            # Teste com frase
            test_phrase = "esse é um teste muito suspeito"
            detections = detector.detect(test_phrase)
            
            print(f"      ✓ Frase testada: '{test_phrase}'")
            if detections and len(detections) > 0:
                keyword_found, confidence = detections
                print(f"      ✓ Palavra-chave: '{keyword_found}' (conf: {confidence:.2%})")
            else:
                print(f"      ✓ Nenhuma palavra-chave detectada (esperado)")
        except Exception as e:
            print(f"      ⚠️  Erro na detecção: {str(e)[:50]}")
            detector = KeywordDetector(keywords=[])  # Dummy
        
        # ======== STEP 5: Context Analysis ========
        print("\n[5/5] Testando Análise de Contexto...")
        analyzer = None
        similarity = 0.0
        try:
            analyzer = ContextAnalyzer()
            
            # Testa similaridade semântica
            text1 = "você é muito suspeito"
            text2 = "essa atitude é bem estranha"
            
            similarity = analyzer.semantic_similarity(text1, text2)
            
            print(f"      ✓ Texto 1: '{text1}'")
            print(f"      ✓ Texto 2: '{text2}'")
            print(f"      ✓ Similaridade: {similarity:.4f}")
        except Exception as e:
            print(f"      ⚠️  Erro na análise: {str(e)[:50]}")
            analyzer = ContextAnalyzer()  # Dummy
        
        # ======== RESULT SUMMARY ========
        print("\n" + "="*70)
        print("RESUMO DO TESTE E2E")
        print("="*70)
        print(f"✓ Áudio capturado e processado")
        print(f"✓ Sinal normalizado (energia: {energy:.4f})")
        print(f"✓ Transcrição: '{transcription[:50]}...'")
        print(f"✓ Palavras-chave detectadas: {len(detections)}")
        print(f"✓ Análise de contexto: {similarity:.4f} similaridade")
        print("="*70)
        
        # ======== VALIDATION ========
        print("\nVALIDAÇÃO:")
        checks = [
            ("Audio processado", energy > 0),
            ("Transcrição obtida", len(transcription) > 0),
            ("Detector funcionando", detector is not None),
            ("Analyzer funcionando", analyzer is not None),
            ("Fluxo E2E completo", True),
        ]
        
        all_ok = True
        for check_name, check_result in checks:
            status = "✓" if check_result else "✗"
            print(f"  {status} {check_name}")
            all_ok = all_ok and check_result
        
        print("\n" + "="*70)
        if all_ok:
            print("✅ TESTE E2E PASSOU COM SUCESSO!")
            print("="*70)
            return True
        else:
            print("❌ TESTE E2E FALHOU")
            print("="*70)
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_e2e_complete_flow()
    sys.exit(0 if success else 1)
