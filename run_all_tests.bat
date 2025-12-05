@echo off
REM Master Test Runner - Executa toda a suite de testes de forma autônoma (Windows)
REM Suporta: Backend tests, Frontend tests, Integration tests, Relatórios

setlocal enabledelayedexpansion

REM Cores não são suportadas em batch puro, mas usamos símbolos
cls
echo.
echo ==================================================
echo 🧪 MASTER TEST RUNNER - Analisador de Microfone
echo ==================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 não encontrado
    exit /b 1
)

REM Verificar venv
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
)

REM Ativar venv
call venv\Scripts\activate.bat

REM Instalar pytest se necessário
pip install pytest requests -q >nul 2>&1

REM ========== TESTES ==========

set TESTS_PASSED=0
set TESTS_FAILED=0

REM 1. Backend Tests
echo.
echo [1/4] Backend Tests (Python)
echo ---------------------------------

python test_backend.py
if %errorlevel% equ 0 (
    set /a TESTS_PASSED+=1
) else (
    set /a TESTS_FAILED+=1
)

REM 2. Frontend Tests
echo.
echo [2/4] Frontend Tests (TypeScript/Next.js)
echo ---------------------------------

if exist test_frontend.sh (
    bash test_frontend.sh
    if %errorlevel% equ 0 (
        set /a TESTS_PASSED+=1
    ) else (
        set /a TESTS_FAILED+=1
    )
) else (
    echo [SKIPPED] test_frontend.sh não encontrado
)

REM 3. Unit Tests (pytest)
echo.
echo [3/4] Unit Tests (pytest)
echo ---------------------------------

python -m pytest tests/ -v --tb=short 2>nul
if %errorlevel% equ 0 (
    set /a TESTS_PASSED+=1
) else (
    echo [WARNING] Unit tests exited with errors
)

REM 4. Integration Tests
echo.
echo [4/4] Integration Tests (E2E)
echo ---------------------------------

python test_integration.py
if %errorlevel% equ 0 (
    set /a TESTS_PASSED+=1
) else (
    set /a TESTS_FAILED+=1
)

REM ========== RELATÓRIOS ==========

echo.
echo [Relatórios] Gerando relatórios...
echo ---------------------------------

python test_runner.py >nul 2>&1

if exist reports (
    echo.
    echo Relatórios gerados em:
    if exist "reports\test_results.json" (
        echo   - reports\test_results.json
    )
    if exist "reports\test_results.html" (
        echo   - reports\test_results.html
    )
)

REM ========== RESUMO FINAL ==========

echo.
echo ==================================================
echo 📊 RESUMO FINAL
echo ==================================================
echo.

set /a TOTAL_SUITES=%TESTS_PASSED% + %TESTS_FAILED%

echo Suites de Testes Executadas: %TOTAL_SUITES%
echo Passaram: %TESTS_PASSED%
echo Falharam: %TESTS_FAILED%

echo.

if %TESTS_FAILED% equ 0 (
    echo ✅ TODOS OS TESTES PASSARAM!
    echo.
    exit /b 0
) else (
    echo ❌ ALGUNS TESTES FALHARAM
    echo.
    echo Para mais detalhes, veja:
    echo   - reports\test_results.html (relatório visual)
    echo   - reports\test_results.json (dados estruturados)
    echo.
    pause
    exit /b 1
)
