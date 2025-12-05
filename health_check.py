#!/usr/bin/env python3
"""
Quick Health Check - Verificação Rápida de Saúde do Projeto
Executa em < 1 segundo
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

def check_health():
    """Realiza check rápido do projeto"""
    print("\n⚡ QUICK HEALTH CHECK\n")
    
    checks = {
        "Core Files": [
            ("main.py", BASE_DIR / "main.py"),
            ("requirements.txt", BASE_DIR / "requirements.txt"),
            ("run.sh", BASE_DIR / "run.sh"),
            ("run.bat", BASE_DIR / "run.bat"),
        ],
        "Core Modules": [
            ("core/analyzer.py", BASE_DIR / "core" / "analyzer.py"),
            ("ai/llm_engine.py", BASE_DIR / "ai" / "llm_engine.py"),
            ("web/app.py", BASE_DIR / "web" / "app.py"),
            ("database/db_manager.py", BASE_DIR / "database" / "db_manager.py"),
        ],
        "Frontend": [
            ("web-control/package.json", BASE_DIR / "web-control" / "package.json"),
            ("web-control/lib/api.ts", BASE_DIR / "web-control" / "lib" / "api.ts"),
            ("web-control/components/dashboard.tsx", BASE_DIR / "web-control" / "components" / "dashboard.tsx"),
        ],
        "Test Scripts": [
            ("test_runner.py", BASE_DIR / "test_runner.py"),
            ("test_backend.py", BASE_DIR / "test_backend.py"),
            ("test_frontend.sh", BASE_DIR / "test_frontend.sh"),
            ("test_integration.py", BASE_DIR / "test_integration.py"),
            ("run_all_tests.sh", BASE_DIR / "run_all_tests.sh"),
            ("run_all_tests.bat", BASE_DIR / "run_all_tests.bat"),
        ],
        "Documentation": [
            ("README.md", BASE_DIR / "README.md"),
            ("TESTING_GUIDE.md", BASE_DIR / "TESTING_GUIDE.md"),
            ("README_TESTES.md", BASE_DIR / "README_TESTES.md"),
            ("SUMARIO_TESTES.md", BASE_DIR / "SUMARIO_TESTES.md"),
        ],
    }
    
    total = 0
    passed = 0
    
    for category, files in checks.items():
        print(f"📁 {category}")
        
        for name, path in files:
            total += 1
            if path.exists():
                print(f"  ✅ {name}")
                passed += 1
            else:
                print(f"  ❌ {name} (NOT FOUND)")
        print()
    
    # Verificar imports críticos
    print("🐍 Python Imports")
    
    critical_imports = [
        "flask",
        "flask_socketio",
        "sqlalchemy",
        "whisper",
        "transformers",
        "pygame",
    ]
    
    for module in critical_imports:
        try:
            __import__(module)
            print(f"  ✅ {module}")
            passed += 1
            total += 1
        except ImportError:
            print(f"  ❌ {module} (NOT INSTALLED)")
            total += 1
    
    print()
    
    # Resultado
    percentage = (passed / total * 100) if total > 0 else 0
    
    print("=" * 50)
    print(f"Total Checks: {total}")
    print(f"Passed: {passed} ({percentage:.0f}%)")
    print("=" * 50)
    print()
    
    if passed == total:
        print("✅ PROJECT HEALTH: EXCELLENT")
        return True
    elif percentage >= 80:
        print("⚠️  PROJECT HEALTH: GOOD (some warnings)")
        return True
    else:
        print("❌ PROJECT HEALTH: POOR (fix issues above)")
        return False


if __name__ == "__main__":
    success = check_health()
    sys.exit(0 if success else 1)
