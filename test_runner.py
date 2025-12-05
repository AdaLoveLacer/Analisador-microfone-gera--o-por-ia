#!/usr/bin/env python3
"""
Test Runner - Executor Autônomo de Testes
Executa toda a suite de testes e gera relatórios detalhados
"""

import os
import sys
import json
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

# Setup paths
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== CONFIGURAÇÃO ==========

@dataclass
class TestResult:
    """Resultado de um teste individual"""
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP", "ERROR"
    duration: float
    output: str
    error: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class TestSuite:
    """Resultado de uma suite de testes"""
    suite_name: str
    total: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    tests: List[TestResult]
    
    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0
        return (self.passed / self.total) * 100


class TestRunner:
    """Executor de testes com suporte a múltiplas suites"""
    
    def __init__(self, base_dir: Path = BASE_DIR):
        self.base_dir = base_dir
        self.results: List[TestSuite] = []
        self.start_time = None
        self.end_time = None
        
    def run(self) -> bool:
        """Executa toda a suite de testes"""
        self.start_time = time.time()
        
        print("\n" + "=" * 70)
        print("🧪 TEST RUNNER - Analisador de Microfone com IA")
        print("=" * 70 + "\n")
        
        # Executar testes
        self._run_unit_tests()
        self._run_api_tests()
        self._run_integration_tests()
        
        self.end_time = time.time()
        
        # Gerar relatórios
        self._generate_reports()
        
        # Exibir resumo
        return self._print_summary()
    
    def _run_unit_tests(self):
        """Executa testes unitários com pytest"""
        print("\n[1/3] 🔬 Testes Unitários")
        print("-" * 70)
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            suite = self._parse_pytest_output(result.stdout, "Unit Tests")
            self.results.append(suite)
            
            print(f"✅ Unit Tests: {suite.passed}/{suite.total} passed")
            
        except subprocess.TimeoutExpired:
            logger.error("Unit tests timeout")
        except Exception as e:
            logger.error(f"Error running unit tests: {e}")
    
    def _run_api_tests(self):
        """Executa testes de API"""
        print("\n[2/3] 🌐 Testes de API")
        print("-" * 70)
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/test_api.py", "-v", "--tb=short"],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            suite = self._parse_pytest_output(result.stdout, "API Tests")
            self.results.append(suite)
            
            print(f"✅ API Tests: {suite.passed}/{suite.total} passed")
            
        except subprocess.TimeoutExpired:
            logger.error("API tests timeout")
        except Exception as e:
            logger.error(f"Error running API tests: {e}")
    
    def _run_integration_tests(self):
        """Executa testes de integração"""
        print("\n[3/3] 🔗 Testes de Integração")
        print("-" * 70)
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/test_e2e_pytest.py", "-v", "--tb=short"],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            suite = self._parse_pytest_output(result.stdout, "Integration Tests")
            self.results.append(suite)
            
            print(f"✅ Integration Tests: {suite.passed}/{suite.total} passed")
            
        except subprocess.TimeoutExpired:
            logger.error("Integration tests timeout")
        except Exception as e:
            logger.error(f"Error running integration tests: {e}")
    
    def _parse_pytest_output(self, output: str, suite_name: str) -> TestSuite:
        """Parse pytest output e retorna TestSuite"""
        lines = output.split('\n')
        
        passed = 0
        failed = 0
        skipped = 0
        errors = 0
        tests = []
        
        for line in lines:
            if " PASSED" in line:
                passed += 1
                test_name = line.split(" ")[0]
                tests.append(TestResult(
                    test_name=test_name,
                    status="PASS",
                    duration=0,
                    output=line
                ))
            elif " FAILED" in line:
                failed += 1
                test_name = line.split(" ")[0]
                tests.append(TestResult(
                    test_name=test_name,
                    status="FAIL",
                    duration=0,
                    output=line
                ))
            elif " SKIPPED" in line:
                skipped += 1
                test_name = line.split(" ")[0]
                tests.append(TestResult(
                    test_name=test_name,
                    status="SKIP",
                    duration=0,
                    output=line
                ))
            elif " ERROR" in line:
                errors += 1
                test_name = line.split(" ")[0]
                tests.append(TestResult(
                    test_name=test_name,
                    status="ERROR",
                    duration=0,
                    output=line
                ))
        
        total = passed + failed + skipped + errors
        
        return TestSuite(
            suite_name=suite_name,
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            duration=0,
            tests=tests
        )
    
    def _generate_reports(self):
        """Gera relatórios JSON e HTML"""
        self._generate_json_report()
        self._generate_html_report()
    
    def _generate_json_report(self):
        """Gera relatório JSON"""
        report_path = self.base_dir / "reports" / "test_results.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "duration": self.end_time - self.start_time if self.end_time else 0,
            "suites": [
                {
                    "name": suite.suite_name,
                    "total": suite.total,
                    "passed": suite.passed,
                    "failed": suite.failed,
                    "skipped": suite.skipped,
                    "errors": suite.errors,
                    "success_rate": suite.success_rate,
                    "tests": [asdict(t) for t in suite.tests]
                }
                for suite in self.results
            ]
        }
        
        with open(report_path, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"JSON report saved: {report_path}")
    
    def _generate_html_report(self):
        """Gera relatório HTML"""
        report_path = self.base_dir / "reports" / "test_results.html"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        html_content = self._build_html_report()
        
        with open(report_path, "w") as f:
            f.write(html_content)
        
        logger.info(f"HTML report saved: {report_path}")
    
    def _build_html_report(self) -> str:
        """Constrói HTML do relatório"""
        total_tests = sum(s.total for s in self.results)
        total_passed = sum(s.passed for s in self.results)
        total_failed = sum(s.failed for s in self.results)
        total_duration = self.end_time - self.start_time if self.end_time else 0
        
        suites_html = ""
        for suite in self.results:
            color = "green" if suite.failed == 0 else "red"
            suites_html += f"""
            <div class="suite">
                <h3 style="color: {color}">
                    {suite.suite_name}
                    <span class="badge">
                        {suite.passed}/{suite.total} passed ({suite.success_rate:.1f}%)
                    </span>
                </h3>
                <ul>
            """
            
            for test in suite.tests:
                status_color = {
                    "PASS": "green",
                    "FAIL": "red",
                    "SKIP": "orange",
                    "ERROR": "darkred"
                }.get(test.status, "gray")
                
                suites_html += f"""
                    <li style="color: {status_color}">
                        <strong>[{test.status}]</strong> {test.test_name}
                    </li>
                """
            
            suites_html += "</ul></div>"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Test Results - Analisador de Microfone com IA</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 10px;
                }}
                .summary {{
                    background-color: #f9f9f9;
                    padding: 15px;
                    border-radius: 4px;
                    margin: 15px 0;
                }}
                .suite {{
                    background-color: #fafafa;
                    padding: 15px;
                    margin: 15px 0;
                    border-left: 4px solid #007bff;
                    border-radius: 4px;
                }}
                .badge {{
                    background-color: #007bff;
                    color: white;
                    padding: 3px 8px;
                    border-radius: 3px;
                    font-size: 0.9em;
                    margin-left: 10px;
                }}
                ul {{
                    list-style-type: none;
                    padding-left: 0;
                }}
                li {{
                    padding: 5px;
                    margin: 5px 0;
                }}
                .timestamp {{
                    color: #666;
                    font-size: 0.9em;
                    margin-top: 20px;
                    padding-top: 10px;
                    border-top: 1px solid #ddd;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧪 Relatório de Testes</h1>
                <p>Analisador de Microfone com IA</p>
                
                <div class="summary">
                    <h2>Resumo Geral</h2>
                    <p><strong>Total de Testes:</strong> {total_tests}</p>
                    <p><strong>Passaram:</strong> <span style="color: green">{total_passed}</span></p>
                    <p><strong>Falharam:</strong> <span style="color: red">{total_failed}</span></p>
                    <p><strong>Taxa de Sucesso:</strong> {(total_passed/total_tests*100 if total_tests > 0 else 0):.1f}%</p>
                    <p><strong>Duração:</strong> {total_duration:.2f}s</p>
                </div>
                
                <h2>Detalhes das Suites</h2>
                {suites_html}
                
                <div class="timestamp">
                    <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _print_summary(self) -> bool:
        """Exibe resumo dos testes e retorna se todos passaram"""
        print("\n" + "=" * 70)
        print("📊 RESUMO FINAL")
        print("=" * 70 + "\n")
        
        total_tests = sum(s.total for s in self.results)
        total_passed = sum(s.passed for s in self.results)
        total_failed = sum(s.failed for s in self.results)
        total_skipped = sum(s.skipped for s in self.results)
        total_errors = sum(s.errors for s in self.results)
        
        for suite in self.results:
            status = "✅" if suite.failed == 0 and suite.errors == 0 else "❌"
            print(f"{status} {suite.suite_name}")
            print(f"   Passed: {suite.passed}, Failed: {suite.failed}, "
                  f"Skipped: {suite.skipped}, Errors: {suite.errors}")
            print(f"   Taxa de Sucesso: {suite.success_rate:.1f}%")
            print()
        
        print(f"Total de Testes: {total_tests}")
        print(f"✅ Passaram: {total_passed}")
        print(f"❌ Falharam: {total_failed}")
        print(f"⏭️  Pulados: {total_skipped}")
        print(f"⚠️  Erros: {total_errors}")
        print(f"⏱️  Duração Total: {self.end_time - self.start_time:.2f}s")
        
        print("\n" + "=" * 70)
        
        if total_failed == 0 and total_errors == 0:
            print("✅ TODOS OS TESTES PASSARAM!")
            print("=" * 70 + "\n")
            return True
        else:
            print("❌ ALGUNS TESTES FALHARAM")
            print("Veja os relatórios em:")
            print(f"  - JSON: reports/test_results.json")
            print(f"  - HTML: reports/test_results.html")
            print("=" * 70 + "\n")
            return False


def main():
    """Entry point"""
    runner = TestRunner()
    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
