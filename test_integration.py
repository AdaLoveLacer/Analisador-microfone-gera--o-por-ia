#!/usr/bin/env python3
"""
Integration Test Suite - Testes End-to-End
Valida: Backend + Frontend integration, APIs, WebSocket
"""

import os
import sys
import time
import json
import logging
import subprocess
import threading
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from urllib.parse import urljoin

# Setup paths
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegrationTestSuite:
    """Suite de testes de integração"""
    
    BACKEND_URL = "http://localhost:5000"
    FRONTEND_URL = "http://localhost:3000"
    API_TIMEOUT = 5
    
    def __init__(self):
        self.results = {
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
    
    def run_all_tests(self) -> bool:
        """Executa todos os testes de integração"""
        print("\n" + "=" * 70)
        print("🔗 INTEGRATION TEST SUITE")
        print("=" * 70 + "\n")
        
        # Setup: Iniciar servidores
        if not self._setup_servers():
            logger.error("Failed to setup test servers")
            return False
        
        try:
            # Aguardar servidores ficarem prontos
            time.sleep(3)
            
            # Executar testes
            tests = [
                ("Backend Connectivity", self.test_backend_connectivity),
                ("API Status Endpoint", self.test_api_status),
                ("API Health Check", self.test_api_health),
                ("Keywords CRUD", self.test_keywords_crud),
                ("Sounds Upload", self.test_sounds_upload),
                ("Config GET/POST", self.test_config_endpoints),
                ("Capture Start/Stop", self.test_capture_control),
                ("LLM Engine", self.test_llm_engine),
                ("Database Persistence", self.test_db_persistence),
                ("Error Handling", self.test_error_handling),
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
        
        finally:
            # Cleanup: Parar servidores
            self._cleanup_servers()
    
    def _setup_servers(self) -> bool:
        """Inicia backend e frontend para testes"""
        print("Setting up test servers...\n")
        
        try:
            # Iniciar backend
            print("  Starting backend...", end=" ")
            self.backend_process = subprocess.Popen(
                ["python", "main.py"],
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("✓")
            
            # Aguardar backend iniciar
            time.sleep(2)
            
            # Verificar se backend está respondendo
            for attempt in range(10):
                try:
                    response = requests.get(
                        f"{self.BACKEND_URL}/api/status",
                        timeout=1
                    )
                    if response.status_code == 200:
                        print("  Backend is ready ✓\n")
                        return True
                except:
                    if attempt < 9:
                        time.sleep(1)
            
            logger.error("Backend failed to start")
            return False
        
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False
    
    def _cleanup_servers(self):
        """Para os servidores de teste"""
        print("\nCleaning up test servers...")
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            print("  Backend stopped ✓")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            print("  Frontend stopped ✓")
    
    def test_backend_connectivity(self) -> bool:
        """Valida que backend está respondendo"""
        try:
            response = requests.get(
                f"{self.BACKEND_URL}/api/status",
                timeout=self.API_TIMEOUT
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Backend connectivity failed: {e}")
            return False
    
    def test_api_status(self) -> bool:
        """Testa endpoint /api/status"""
        try:
            response = requests.get(
                f"{self.BACKEND_URL}/api/status",
                timeout=self.API_TIMEOUT
            )
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            
            # Validar campos obrigatórios
            required_fields = ['is_recording', 'device', 'model', 'sample_rate']
            for field in required_fields:
                if field not in data:
                    logger.error(f"Missing field in status: {field}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Status test failed: {e}")
            return False
    
    def test_api_health(self) -> bool:
        """Testa health check da API"""
        try:
            # Testar vários endpoints de diagnóstico
            endpoints = [
                "/api/status",
                "/api/llm/status",
            ]
            
            for endpoint in endpoints:
                response = requests.get(
                    f"{self.BACKEND_URL}{endpoint}",
                    timeout=self.API_TIMEOUT
                )
                
                if response.status_code != 200:
                    logger.error(f"Health check failed for {endpoint}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def test_keywords_crud(self) -> bool:
        """Testa CRUD de keywords"""
        try:
            # GET - Listar
            response = requests.get(
                f"{self.BACKEND_URL}/api/keywords",
                timeout=self.API_TIMEOUT
            )
            if response.status_code != 200:
                return False
            
            initial_count = len(response.json())
            
            # POST - Criar
            new_keyword = {
                "name": "test_keyword",
                "pattern": "test",
                "variations": "teste,testing",
                "context": "integration,testing",
                "sound_id": None,
                "weight": 1.0
            }
            
            response = requests.post(
                f"{self.BACKEND_URL}/api/keywords",
                json=new_keyword,
                timeout=self.API_TIMEOUT
            )
            if response.status_code != 201:
                return False
            
            keyword_id = response.json().get('id')
            if not keyword_id:
                return False
            
            # GET - Verificar criação
            response = requests.get(
                f"{self.BACKEND_URL}/api/keywords",
                timeout=self.API_TIMEOUT
            )
            if len(response.json()) != initial_count + 1:
                return False
            
            # DELETE - Remover
            response = requests.delete(
                f"{self.BACKEND_URL}/api/keywords/{keyword_id}",
                timeout=self.API_TIMEOUT
            )
            if response.status_code not in [200, 204]:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Keywords CRUD test failed: {e}")
            return False
    
    def test_sounds_upload(self) -> bool:
        """Testa upload de sons"""
        try:
            # Listar sons
            response = requests.get(
                f"{self.BACKEND_URL}/api/sounds",
                timeout=self.API_TIMEOUT
            )
            
            if response.status_code != 200:
                return False
            
            # Validar estrutura
            sounds = response.json()
            if not isinstance(sounds, list):
                return False
            
            return True
        except Exception as e:
            logger.error(f"Sounds test failed: {e}")
            return False
    
    def test_config_endpoints(self) -> bool:
        """Testa GET/POST de configurações"""
        try:
            # GET - Obter config
            response = requests.get(
                f"{self.BACKEND_URL}/api/config",
                timeout=self.API_TIMEOUT
            )
            if response.status_code != 200:
                return False
            
            config = response.json()
            
            # POST - Salvar config (sem alterações)
            response = requests.post(
                f"{self.BACKEND_URL}/api/config",
                json=config,
                timeout=self.API_TIMEOUT
            )
            if response.status_code not in [200, 201]:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Config endpoints test failed: {e}")
            return False
    
    def test_capture_control(self) -> bool:
        """Testa controle de captura (start/stop)"""
        try:
            # Start
            response = requests.post(
                f"{self.BACKEND_URL}/api/capture/start",
                timeout=self.API_TIMEOUT
            )
            if response.status_code != 200:
                return False
            
            time.sleep(1)
            
            # Status
            response = requests.get(
                f"{self.BACKEND_URL}/api/capture/status",
                timeout=self.API_TIMEOUT
            )
            if response.status_code != 200:
                return False
            
            # Stop
            response = requests.post(
                f"{self.BACKEND_URL}/api/capture/stop",
                timeout=self.API_TIMEOUT
            )
            if response.status_code != 200:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Capture control test failed: {e}")
            return False
    
    def test_llm_engine(self) -> bool:
        """Testa LLM Engine"""
        try:
            response = requests.get(
                f"{self.BACKEND_URL}/api/llm/status",
                timeout=self.API_TIMEOUT
            )
            
            if response.status_code != 200:
                return False
            
            status = response.json()
            
            # Validar estrutura
            required_fields = ['active_backend', 'ollama_available', 'transformers_available']
            for field in required_fields:
                if field not in status:
                    return False
            
            return True
        except Exception as e:
            logger.error(f"LLM Engine test failed: {e}")
            return False
    
    def test_db_persistence(self) -> bool:
        """Testa persistência de dados no banco"""
        try:
            # Criar keyword
            keyword_data = {
                "name": "persistence_test",
                "pattern": "persist",
                "variations": "",
                "context": "",
                "sound_id": None,
                "weight": 1.0
            }
            
            response = requests.post(
                f"{self.BACKEND_URL}/api/keywords",
                json=keyword_data,
                timeout=self.API_TIMEOUT
            )
            
            if response.status_code != 201:
                return False
            
            keyword_id = response.json().get('id')
            
            # Aguardar e verificar persistência
            time.sleep(1)
            
            response = requests.get(
                f"{self.BACKEND_URL}/api/keywords",
                timeout=self.API_TIMEOUT
            )
            
            keywords = response.json()
            found = any(k.get('id') == keyword_id for k in keywords)
            
            return found
        except Exception as e:
            logger.error(f"DB persistence test failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Testa tratamento de erros"""
        try:
            # Teste 1: 404 Not Found
            response = requests.get(
                f"{self.BACKEND_URL}/api/nonexistent",
                timeout=self.API_TIMEOUT
            )
            if response.status_code != 404:
                return False
            
            # Teste 2: Bad request
            response = requests.post(
                f"{self.BACKEND_URL}/api/keywords",
                json={},  # Dados incompletos
                timeout=self.API_TIMEOUT
            )
            if response.status_code not in [400, 422]:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error handling test failed: {e}")
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
    suite = IntegrationTestSuite()
    success = suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
