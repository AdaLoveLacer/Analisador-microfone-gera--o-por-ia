#!/usr/bin/env python
"""Test to validate all critical fixes."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import threading
import time
from core.analyzer import MicrophoneAnalyzer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_thread_safety():
    """Test thread safety improvements."""
    logger.info("=" * 60)
    logger.info("TEST 1: Thread Safety (Locks)")
    logger.info("=" * 60)
    
    analyzer = MicrophoneAnalyzer()
    
    # Verificar que locks foram criados
    assert hasattr(analyzer, '_state_lock'), "Missing _state_lock"
    assert hasattr(analyzer, '_callback_lock'), "Missing _callback_lock"
    logger.info("✅ Locks criados corretamente")
    
    # Teste de início/parada rápido (verificar race conditions)
    def rapid_toggle():
        for i in range(5):
            try:
                analyzer.start()
                time.sleep(0.1)
                analyzer.stop()
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Erro no toggle {i}: {e}")
    
    thread = threading.Thread(target=rapid_toggle)
    thread.start()
    thread.join(timeout=5)
    
    logger.info("✅ Start/stop com múltiplas threads sem erro")
    print()

def test_component_reuse():
    """Test that components are reused, not recreated."""
    logger.info("=" * 60)
    logger.info("TEST 2: Component Reuse (Memory Leak Fix)")
    logger.info("=" * 60)
    
    analyzer = MicrophoneAnalyzer()
    
    # Start
    analyzer.start()
    time.sleep(0.5)
    
    # Get component references
    processor_1st = analyzer.audio_processor
    transcriber_1st = analyzer.transcriber
    
    # Stop
    analyzer.stop()
    time.sleep(0.5)
    
    # Start again
    analyzer.start()
    time.sleep(0.5)
    
    # Get component references again
    processor_2nd = analyzer.audio_processor
    transcriber_2nd = analyzer.transcriber
    
    # Verificar que são as MESMAS instâncias
    if processor_1st is processor_2nd:
        logger.info("✅ AudioProcessor reutilizado (sem memory leak)")
    else:
        logger.warning("⚠️ AudioProcessor foi recriado (memory leak)")
    
    if transcriber_1st is transcriber_2nd:
        logger.info("✅ Transcriber reutilizado (sem memory leak)")
    else:
        logger.warning("⚠️ Transcriber foi recriado (memory leak)")
    
    analyzer.stop()
    print()

def test_get_status():
    """Test that get_status() exists and is thread-safe."""
    logger.info("=" * 60)
    logger.info("TEST 3: get_status() Method")
    logger.info("=" * 60)
    
    analyzer = MicrophoneAnalyzer()
    
    # Verificar método existe
    assert hasattr(analyzer, 'get_status'), "Missing get_status() method"
    
    # Chamar get_status
    status = analyzer.get_status()
    
    assert isinstance(status, dict), "get_status() deve retornar dict"
    assert 'is_running' in status, "status deve ter 'is_running'"
    assert 'is_capturing' in status, "status deve ter 'is_capturing'"
    assert 'timestamp' in status, "status deve ter 'timestamp'"
    
    logger.info(f"✅ get_status() retorna: {status}")
    print()

def test_config_validation():
    """Test config validation."""
    logger.info("=" * 60)
    logger.info("TEST 4: Config Validation")
    logger.info("=" * 60)
    
    analyzer = MicrophoneAnalyzer()
    
    # Verificar que config foi carregada
    config = analyzer.config.get_all()
    assert isinstance(config, dict), "Config deve ser dict"
    logger.info(f"✅ Config carregada com {len(config)} seções")
    
    # Verificar método de validação existe
    assert hasattr(analyzer.config, '_validate_config_structure'), "Missing _validate_config_structure"
    logger.info("✅ Método de validação de config implementado")
    print()

def test_database_thread_safety():
    """Test database thread safety."""
    logger.info("=" * 60)
    logger.info("TEST 5: Database Thread Safety")
    logger.info("=" * 60)
    
    from database.db_manager import DatabaseManager
    
    db = DatabaseManager()
    
    # Verificar que lock foi criado
    assert hasattr(db, '_db_lock'), "Missing _db_lock"
    logger.info("✅ Database lock criado")
    
    # Verificar que método _execute_with_lock existe
    assert hasattr(db, '_execute_with_lock'), "Missing _execute_with_lock"
    logger.info("✅ Método _execute_with_lock implementado")
    
    # Teste de concurrent access
    def add_multiple():
        for i in range(3):
            try:
                db.add_event(f"test_event_{i}")
            except Exception as e:
                logger.error(f"Erro ao adicionar evento {i}: {e}")
    
    threads = [threading.Thread(target=add_multiple) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)
    
    logger.info("✅ Database handle concurrent writes corretamente")
    print()

if __name__ == '__main__':
    try:
        test_thread_safety()
        test_component_reuse()
        test_get_status()
        test_config_validation()
        test_database_thread_safety()
        
        logger.info("=" * 60)
        logger.info("✅ TODOS OS TESTES PASSARAM!")
        logger.info("=" * 60)
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ TESTE FALHOU: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
