#!/usr/bin/env python3
"""
Backend Test Suite - Testes Específicos do Backend
Valida: API routes, analyzer, audio processing, AI modules
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any

# Setup paths
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackendTestSuite:
    """Suite de testes do backend"""
    
    def __init__(self):
        self.results = {
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            },
            "timestamp": ""
        }
    
    def run_all_tests(self) -> bool:
        """Executa todos os testes do backend"""
        print("\n" + "=" * 70)
        print("🔬 BACKEND TEST SUITE")
        print("=" * 70 + "\n")
        
        tests = [
            ("Imports do Backend", self.test_imports),
            ("Core Analyzer", self.test_analyzer),
            ("Transcriber (Whisper)", self.test_transcriber),
            ("Keyword Detector", self.test_keyword_detector),
            ("Context Analyzer", self.test_context_analyzer),
            ("LLM Engine", self.test_llm_engine),
            ("Database Manager", self.test_database_manager),
            ("Audio Utils", self.test_audio_utils),
            ("Sound Player", self.test_sound_player),
            ("Config Manager", self.test_config_manager),
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"Testing: {test_name}...", end=" ")
                result = test_func()
                
                if result:
                    print("✅ PASSED")
                    self._add_result(test_name, "PASS")
                else:
                    print("❌ FAILED")
                    self._add_result(test_name, "FAIL")
            except Exception as e:
                print(f"⚠️  ERROR: {str(e)[:50]}")
                self._add_result(test_name, "ERROR", str(e))
        
        return self._print_summary()
    
    def test_imports(self) -> bool:
        """Valida que todos os imports críticos funcionam"""
        try:
            import core.analyzer
            import core.config_manager
            import core.event_logger
            import audio.transcriber
            import audio.processor
            import audio.audio_utils
            import ai.keyword_detector
            import ai.context_analyzer
            import ai.llm_engine
            import database.db_manager
            import sound.player
            import web.api_routes
            import web.app
            import web.websocket_handler
            import utils.validators
            import utils.exceptions
            return True
        except ImportError as e:
            logger.error(f"Import error: {e}")
            return False
    
    def test_analyzer(self) -> bool:
        """Testa inicialização do MicrophoneAnalyzer"""
        try:
            from core.analyzer import MicrophoneAnalyzer
            
            analyzer = MicrophoneAnalyzer(
                config_dir=str(BASE_DIR),
                database_dir=str(BASE_DIR)
            )
            
            # Validar atributos críticos
            assert hasattr(analyzer, 'config'), "Missing config attribute"
            assert hasattr(analyzer, 'db_manager'), "Missing db_manager attribute"
            assert hasattr(analyzer, 'transcriber'), "Missing transcriber attribute"
            assert hasattr(analyzer, 'keyword_detector'), "Missing keyword_detector"
            assert hasattr(analyzer, 'context_analyzer'), "Missing context_analyzer"
            assert hasattr(analyzer, 'llm_engine'), "Missing llm_engine attribute"
            
            return True
        except Exception as e:
            logger.error(f"Analyzer test failed: {e}")
            return False
    
    def test_transcriber(self) -> bool:
        """Testa Transcriber (Whisper integration)"""
        try:
            from audio.transcriber import Transcriber
            
            transcriber = Transcriber(model_name='base')
            
            # Validar métodos críticos
            assert hasattr(transcriber, 'transcribe'), "Missing transcribe method"
            assert hasattr(transcriber, 'load_model'), "Missing load_model method"
            
            return True
        except Exception as e:
            logger.error(f"Transcriber test failed: {e}")
            return False
    
    def test_keyword_detector(self) -> bool:
        """Testa KeywordDetector"""
        try:
            from ai.keyword_detector import KeywordDetector
            
            detector = KeywordDetector()
            
            # Validar métodos críticos
            assert hasattr(detector, 'detect'), "Missing detect method"
            assert hasattr(detector, 'add_keyword'), "Missing add_keyword method"
            assert hasattr(detector, 'remove_keyword'), "Missing remove_keyword method"
            
            # Teste simples de detecção
            detector.add_keyword("test", "test", threshold=0.8)
            results = detector.detect("this is a test")
            
            assert isinstance(results, list), "Detect should return list"
            
            return True
        except Exception as e:
            logger.error(f"KeywordDetector test failed: {e}")
            return False
    
    def test_context_analyzer(self) -> bool:
        """Testa ContextAnalyzer"""
        try:
            from ai.context_analyzer import ContextAnalyzer
            
            analyzer = ContextAnalyzer()
            
            # Validar métodos críticos
            assert hasattr(analyzer, 'analyze'), "Missing analyze method"
            assert hasattr(analyzer, 'get_embeddings'), "Missing get_embeddings"
            
            # Teste simples
            result = analyzer.analyze("test text", ["keyword"])
            assert isinstance(result, dict), "Analyze should return dict"
            
            return True
        except Exception as e:
            logger.error(f"ContextAnalyzer test failed: {e}")
            return False
    
    def test_llm_engine(self) -> bool:
        """Testa LLMEngine"""
        try:
            from ai.llm_engine import LLMEngine
            
            engine = LLMEngine()
            
            # Validar métodos críticos
            assert hasattr(engine, 'generate'), "Missing generate method"
            assert hasattr(engine, 'analyze_context'), "Missing analyze_context"
            assert hasattr(engine, 'get_status'), "Missing get_status method"
            
            # Teste de status
            status = engine.get_status()
            assert isinstance(status, dict), "get_status should return dict"
            assert 'active_backend' in status, "Status missing active_backend"
            
            return True
        except Exception as e:
            logger.error(f"LLMEngine test failed: {e}")
            return False
    
    def test_database_manager(self) -> bool:
        """Testa DatabaseManager"""
        try:
            from database.db_manager import DatabaseManager
            
            db = DatabaseManager(
                database_path=str(BASE_DIR / "test_db.sqlite")
            )
            
            # Validar métodos críticos
            assert hasattr(db, 'add_detection'), "Missing add_detection method"
            assert hasattr(db, 'get_detections'), "Missing get_detections method"
            assert hasattr(db, 'add_keyword'), "Missing add_keyword method"
            
            return True
        except Exception as e:
            logger.error(f"DatabaseManager test failed: {e}")
            return False
    
    def test_audio_utils(self) -> bool:
        """Testa Audio Utils"""
        try:
            from audio.audio_utils import (
                get_audio_devices,
                calculate_audio_level,
                normalize_audio
            )
            
            # Teste de get_audio_devices
            devices = get_audio_devices()
            assert isinstance(devices, list), "get_audio_devices should return list"
            
            return True
        except Exception as e:
            logger.error(f"AudioUtils test failed: {e}")
            return False
    
    def test_sound_player(self) -> bool:
        """Testa SoundPlayer"""
        try:
            from sound.player import SoundPlayer
            
            player = SoundPlayer()
            
            # Validar métodos críticos
            assert hasattr(player, 'play'), "Missing play method"
            assert hasattr(player, 'stop'), "Missing stop method"
            assert hasattr(player, 'load_sound'), "Missing load_sound method"
            
            return True
        except Exception as e:
            logger.error(f"SoundPlayer test failed: {e}")
            return False
    
    def test_config_manager(self) -> bool:
        """Testa ConfigManager"""
        try:
            from core.config_manager import ConfigManager
            
            config = ConfigManager(config_dir=str(BASE_DIR))
            
            # Validar métodos críticos
            assert hasattr(config, 'get'), "Missing get method"
            assert hasattr(config, 'set'), "Missing set method"
            assert hasattr(config, 'save'), "Missing save method"
            assert hasattr(config, 'load'), "Missing load method"
            
            return True
        except Exception as e:
            logger.error(f"ConfigManager test failed: {e}")
            return False
    
    def _add_result(self, test_name: str, status: str, error: str = ""):
        """Adiciona resultado de teste"""
        self.results["tests"].append({
            "name": test_name,
            "status": status,
            "error": error
        })
        
        self.results["summary"]["total"] += 1
        
        if status == "PASS":
            self.results["summary"]["passed"] += 1
        elif status == "FAIL":
            self.results["summary"]["failed"] += 1
        elif status == "SKIP":
            self.results["summary"]["skipped"] += 1
    
    def _print_summary(self) -> bool:
        """Exibe resumo e retorna sucesso"""
        summary = self.results["summary"]
        
        print("\n" + "-" * 70)
        print(f"Total: {summary['total']} | "
              f"✅ {summary['passed']} | "
              f"❌ {summary['failed']} | "
              f"⏭️  {summary['skipped']}")
        
        success_rate = (summary['passed'] / summary['total'] * 100) if summary['total'] > 0 else 0
        print(f"Taxa de Sucesso: {success_rate:.1f}%")
        print("-" * 70 + "\n")
        
        return summary['failed'] == 0


def main():
    """Entry point"""
    suite = BackendTestSuite()
    success = suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
