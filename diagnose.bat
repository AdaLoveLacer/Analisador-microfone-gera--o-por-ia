@echo off
REM Script de diagnóstico completo do sistema para Windows
REM Identifica problemas e oferece soluções

setlocal enabledelayedexpansion

set TOTAL_CHECKS=0
set PASSED_CHECKS=0
set FAILED_CHECKS=0

cls
echo.
echo ╔═══════════════════════════════════════════════════╗
echo ║  Analisador de Microfone - Diagnóstico (Windows)   ║
echo ╚═══════════════════════════════════════════════════╝
echo.

REM ======== FUNÇÕES ========

REM ======== SISTEMA ========

echo ======== SISTEMA ========
echo.

for /f "tokens=*" %%i in ('wmic os get caption ^| findstr /v "Caption"') do set OS=%%i
echo [OK] SO: %OS%
echo.

REM ======== PYTHON ========

echo ======== PYTHON ========
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado no PATH
    echo        Instale de: https://www.python.org/downloads/
    echo        IMPORTANTE: Marque "Add Python to PATH"
    set /a FAILED_CHECKS+=1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [OK] Python %PYTHON_VERSION%
    set /a PASSED_CHECKS+=1
)
set /a TOTAL_CHECKS+=1
echo.

python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] pip nao esta funcionando
    set /a FAILED_CHECKS+=1
) else (
    for /f "tokens=2" %%i in ('python -m pip --version') do set PIP_VERSION=%%i
    echo [OK] pip %PIP_VERSION%
    set /a PASSED_CHECKS+=1
)
set /a TOTAL_CHECKS+=1
echo.

REM ======== AMBIENTE VIRTUAL ========

echo ======== AMBIENTE VIRTUAL ========
echo.

if exist "venv" (
    echo [OK] venv encontrado
    set /a PASSED_CHECKS+=1
    
    if exist "venv\Scripts\python.exe" (
        echo [OK] Python da venv encontrado
        set /a PASSED_CHECKS+=1
        set /a TOTAL_CHECKS+=1
    ) else (
        echo [ERRO] Python da venv nao encontrado
        set /a FAILED_CHECKS+=1
        set /a TOTAL_CHECKS+=1
    )
) else (
    echo [AVISO] venv nao encontrado (sera criado automaticamente)
    set /a FAILED_CHECKS+=1
    set /a TOTAL_CHECKS+=1
)
set /a TOTAL_CHECKS+=1
echo.

REM ======== PACOTES CRITICOS ========

echo ======== PACOTES PYTHON ========
echo.

if exist "venv\Scripts\python.exe" (
    set PYTHON_BIN=venv\Scripts\python.exe
) else (
    set PYTHON_BIN=python
)

for %%P in (flask whisper torch transformers sentence_transformers sqlalchemy pyaudio flask_socketio) do (
    %PYTHON_BIN% -c "import %%P" >nul 2>&1
    if errorlevel 1 (
        echo [AVISO] %%P nao encontrado
        set /a FAILED_CHECKS+=1
    ) else (
        echo [OK] %%P
        set /a PASSED_CHECKS+=1
    )
    set /a TOTAL_CHECKS+=1
)
echo.

REM ======== GPU ========

echo ======== GPU/CUDA ========
echo.

%PYTHON_BIN% -c "import torch; print('OK') if torch.cuda.is_available() else print('CPU')" >nul 2>&1
if errorlevel 1 (
    echo [AVISO] PyTorch nao encontrado
) else (
    for /f %%i in ('%PYTHON_BIN% -c "import torch; print('CUDA' if torch.cuda.is_available() else 'CPU')"') do set GPU_MODE=%%i
    
    if "!GPU_MODE!"=="CUDA" (
        for /f %%i in ('%PYTHON_BIN% -c "import torch; print(torch.cuda.get_device_name(0))"') do set GPU_NAME=%%i
        echo [OK] GPU: !GPU_NAME!
        set /a PASSED_CHECKS+=1
    ) else (
        echo [AVISO] Usando CPU (instale NVIDIA Driver + CUDA 11.8)
    )
)
set /a TOTAL_CHECKS+=1
echo.

REM ======== MODELOS ========

echo ======== MODELOS AI ========
echo.

if exist "venv\Scripts\python.exe" (
    %PYTHON_BIN% -c "import whisper; whisper.load_model('base')" >nul 2>&1
    if errorlevel 1 (
        echo [AVISO] Modelo Whisper sera baixado na primeira execucao
    ) else (
        echo [OK] Modelo Whisper (140 MB)
        set /a PASSED_CHECKS+=1
    )
) else (
    echo [AVISO] venv nao ativo, nao posso verificar modelos
)
set /a TOTAL_CHECKS+=1

if exist "%USERPROFILE%\.cache\huggingface\hub" (
    dir "%USERPROFILE%\.cache\huggingface\hub" /B 2>nul | findstr /I "phi" >nul
    if errorlevel 1 (
        echo [AVISO] Modelo Phi-2 sera baixado na primeira execucao (3.8GB)
    ) else (
        echo [OK] Modelo Phi-2 (cache local)
        set /a PASSED_CHECKS+=1
    )
) else (
    echo [AVISO] Modelo Phi-2 sera baixado na primeira execucao (3.8GB)
)
set /a TOTAL_CHECKS+=1
echo.

REM ======== ARQUIVOS ========

echo ======== ARQUIVOS E DIRETORIOS ========
echo.

if exist "requirements.txt" (
    echo [OK] requirements.txt
    set /a PASSED_CHECKS+=1
) else (
    echo [ERRO] requirements.txt nao encontrado
    set /a FAILED_CHECKS+=1
)
set /a TOTAL_CHECKS+=1

if exist "main.py" (
    echo [OK] main.py
    set /a PASSED_CHECKS+=1
) else (
    echo [ERRO] main.py nao encontrado
    set /a FAILED_CHECKS+=1
)
set /a TOTAL_CHECKS+=1

if exist "web\app.py" (
    echo [OK] web/app.py
    set /a PASSED_CHECKS+=1
) else (
    echo [ERRO] web/app.py nao encontrado
    set /a FAILED_CHECKS+=1
)
set /a TOTAL_CHECKS+=1

if exist "logs" (
    echo [OK] Diretorio logs
    set /a PASSED_CHECKS+=1
) else (
    echo [AVISO] Diretorio logs nao encontrado
)
set /a TOTAL_CHECKS+=1

if exist "database" (
    echo [OK] Diretorio database
    set /a PASSED_CHECKS+=1
) else (
    echo [AVISO] Diretorio database nao encontrado
)
set /a TOTAL_CHECKS+=1
echo.

REM ======== PORTAS ========

echo ======== PORTAS ========
echo.

netstat -ano 2>nul | findstr ":5000 " >nul
if errorlevel 1 (
    echo [OK] Porta 5000 disponivel
    set /a PASSED_CHECKS+=1
) else (
    echo [AVISO] Porta 5000 em uso
)
set /a TOTAL_CHECKS+=1

netstat -ano 2>nul | findstr ":3000 " >nul
if errorlevel 1 (
    echo [OK] Porta 3000 disponivel
    set /a PASSED_CHECKS+=1
) else (
    echo [AVISO] Porta 3000 em uso
)
set /a TOTAL_CHECKS+=1
echo.

REM ======== RESUMO ========

echo ======== RESUMO ========
echo.
echo Total verificacoes: %TOTAL_CHECKS%
echo Passou: %PASSED_CHECKS%
echo Falhou: %FAILED_CHECKS%
echo.

if %FAILED_CHECKS% equ 0 (
    echo ╔═══════════════════════════════════════╗
    echo ║  ✓ Sistema pronto para usar!         ║
    echo ╚═══════════════════════════════════════╝
    echo.
    echo Execute: run.bat
    echo.
    pause
    exit /b 0
) else if %FAILED_CHECKS% lss 5 (
    echo ╔═══════════════════════════════════════╗
    echo ║  ⚠ Alguns avisos detectados          ║
    echo ╚═══════════════════════════════════════╝
    echo.
    echo Execute: run.bat
    echo Os problemas serao resolvidos automaticamente.
    echo.
    pause
    exit /b 0
) else (
    echo ╔═══════════════════════════════════════╗
    echo ║  X Problemas graves encontrados      ║
    echo ╚═══════════════════════════════════════╝
    echo.
    echo Corrija os erros acima e tente novamente.
    echo.
    pause
    exit /b 1
)
