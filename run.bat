@echo off
REM Setup e execução - Analisador de Microfone com IA (Windows)
setlocal enabledelayedexpansion

REM ======== FUNÇÕES AUXILIARES ========

:log_ok
echo [OK] %~1
goto :eof

:log_warn
echo [AVISO] %~1
goto :eof

:log_error
echo [ERRO] %~1
goto :eof

:log_section
echo.
echo === %~1 ===
goto :eof

REM ======== VALIDAÇÃO DE PYTHON ========

:check_python
call :log_section "Validando Python"

python --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Python 3 não encontrado!"
    echo     Instale Python 3.10+ de: https://www.python.org/downloads/
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
call :log_ok "Python 3 encontrado: !PYVER!"

REM Verifica versão mínima (3.8+)
for /f "tokens=1,2 delims=." %%a in ("!PYVER!") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if !MAJOR! lss 3 (
    call :log_error "Python 3.8+ é necessário (encontrado: !PYVER!)"
    exit /b 1
)

if !MAJOR! equ 3 if !MINOR! lss 8 (
    call :log_error "Python 3.8+ é necessário (encontrado: !PYVER!)"
    exit /b 1
)

set PYTHON_BIN=python
exit /b 0

REM ======== ORDEM CORRETA: 1º check_venv ========

:check_venv
call :log_section "Validando ambiente virtual"

if exist "venv" (
    call :log_ok "venv encontrado"
    if exist "venv\Scripts\python.exe" (
        set VENV_PYTHON=venv\Scripts\python.exe
        call :log_ok "Python da venv encontrado: !VENV_PYTHON!"
        exit /b 0
    ) else (
        call :log_warn "venv encontrado mas Python não está disponível"
        exit /b 1
    )
)

if exist ".venv" (
    call :log_warn ".venv encontrado, renomeando para venv"
    ren .venv venv
    if exist "venv\Scripts\python.exe" (
        set VENV_PYTHON=venv\Scripts\python.exe
        exit /b 0
    )
)

exit /b 1

REM ======== ORDEM CORRETA: 2º create_venv ========

:create_venv
call :log_section "Criando ambiente virtual"

python -m venv venv
if errorlevel 1 (
    call :log_error "Falha ao criar ambiente virtual"
    exit /b 1
)

call :log_ok "Ambiente virtual criado"
set VENV_PYTHON=venv\Scripts\python.exe
exit /b 0

REM ======== ORDEM CORRETA: 3º check_pip ========

:check_pip
call :log_section "Validando pip"

!VENV_PYTHON! -m pip --version >nul 2>&1
if errorlevel 1 (
    call :log_error "pip não está funcionando corretamente"
    exit /b 1
)

for /f "tokens=2" %%i in ('!VENV_PYTHON! -m pip --version 2^>^&1') do set PIPVER=%%i
call :log_ok "pip !PIPVER! encontrado"

call :log_section "Atualizando pip"
!VENV_PYTHON! -m pip install --upgrade pip -q 2>nul
call :log_ok "pip atualizado"
exit /b 0

REM ======== ORDEM CORRETA: 4º check_requirements ========

:check_requirements
call :log_section "Validando dependências Python (requirements.txt)"

if not exist "requirements.txt" (
    call :log_error "requirements.txt não encontrado!"
    exit /b 1
)

REM Lista de pacotes críticos
set "CRITICAL_PACKAGES=flask flask-socketio openai-whisper transformers torch sentence-transformers pyaudio"

for %%P in (!CRITICAL_PACKAGES!) do (
    set PKG=%%P
    set PKG=!PKG:-=_!
    !VENV_PYTHON! -c "import !PKG!" >nul 2>&1
    if errorlevel 1 (
        call :log_warn "Pacote não encontrado: %%P"
        exit /b 1
    )
)

call :log_ok "Todos os pacotes críticos encontrados"
exit /b 0

REM ======== ORDEM CORRETA: 5º install_requirements ========

:install_requirements
call :log_section "Instalando dependências (primeira execução)"
echo     Isso pode levar vários minutos...
echo.

if not exist "pip-cache" mkdir pip-cache

call :log_section "Instalando PyTorch com CUDA 11.8"
!VENV_PYTHON! -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --cache-dir pip-cache -q 2>nul

if errorlevel 1 (
    call :log_warn "Falha ao instalar PyTorch com CUDA, tentando CPU"
    !VENV_PYTHON! -m pip install torch torchvision torchaudio --cache-dir pip-cache -q 2>nul
)

call :log_section "Instalando dependências do requirements.txt"
!VENV_PYTHON! -m pip install -r requirements.txt --cache-dir pip-cache -q 2>nul

if errorlevel 1 (
    call :log_error "Falha ao instalar requirements.txt"
    exit /b 1
)

call :log_ok "Dependências instaladas com sucesso"
exit /b 0

REM ======== CRIAÇÃO DE DIRETÓRIOS ========

:create_directories
call :log_section "Criando diretórios necessários"

if not exist "logs" mkdir logs
if not exist "database" mkdir database
if not exist "audio_library" mkdir audio_library
if not exist "audio_library\memes" mkdir audio_library\memes
if not exist "audio_library\efeitos" mkdir audio_library\efeitos
if not exist "audio_library\notificacoes" mkdir audio_library\notificacoes

call :log_ok "Diretórios criados"
exit /b 0

REM ======== DIAGNÓSTICO COMPLETO ========

:diagnose
call :log_section "=== DIAGNÓSTICO DO SISTEMA ==="

call :check_python
if errorlevel 1 exit /b 1

call :check_venv
if errorlevel 1 (
    call :create_venv
    if errorlevel 1 exit /b 1
)

call venv\Scripts\activate.bat
set VENV_PYTHON=python

call :check_pip
if errorlevel 1 exit /b 1

call :check_requirements
if errorlevel 1 (
    call :log_warn "Algumas dependências faltam"
    call :install_requirements
    if errorlevel 1 exit /b 1
)

echo.
call :log_ok "Sistema está OK!"
exit /b 0

REM ======== FUNÇÕES DE MANUTENÇÃO ========

:clean_cache
echo.
echo [*] Limpando cache do pip...
pip cache purge
echo [OK] Cache limpo
echo.
echo Use: run.bat
echo (para iniciar normalmente)
exit /b 0

:delete_venv
echo [AVISO] Isso vai deletar o ambiente virtual
set /p confirm="Deseja continuar? (s/n): "

if not "!confirm!"=="s" if not "!confirm!"=="S" (
    echo Cancelado
    exit /b 1
)

echo.
echo [*] Deletando venv...
if exist "venv" (
    rmdir /s /q venv
    echo [OK] venv deletado
) else (
    echo [OK] venv não existe
)
exit /b 0

REM ======== PROCESSAMENTO DE ARGUMENTOS ========

:main
if "%~1"=="" goto :normal_mode
if "%~1"=="--help" goto :show_help
if "%~1"=="-h" goto :show_help
if "%~1"=="--clean" goto :do_clean
if "%~1"=="--diagnose" goto :do_diagnose
if "%~1"=="--delete-venv" goto :do_delete_venv
if "%~1"=="--skip-checks" (
    set SKIP_CHECKS=1
    goto :skip_mode
)

echo.
echo [ERRO] Opção desconhecida: %~1
call :show_help
exit /b 1

:show_help
echo.
echo === Analisador de Microfone com IA ===
echo.
echo Opções:
echo   --help, -h     Mostra esta mensagem
echo   --diagnose     Diagnostica problemas no sistema
echo   --clean        Limpa cache do pip
echo   --delete-venv  Deleta apenas o ambiente virtual
echo   --skip-checks  Ignora validacoes e inicia direto
echo.
echo Exemplos:
echo   run.bat              - Inicia com validacoes completas
echo   run.bat --diagnose   - Diagnostica problemas
echo   run.bat --clean      - Limpa cache do pip
echo.
exit /b 0

:do_clean
call :clean_cache
exit /b 0

:do_diagnose
call :diagnose
exit /b 0

:do_delete_venv
call :delete_venv
exit /b 0

:skip_mode
set SKIP_CHECKS=1
goto :start_app

:normal_mode
set SKIP_CHECKS=0

:start_app
REM ======== VALIDAÇÕES ========

echo.
echo === Analisador de Microfone com IA ===
echo Versão 2.0 - Build 2025-12-04
echo.

if not "%SKIP_CHECKS%"=="1" (
    call :check_python
    if errorlevel 1 exit /b 1
    
    call :check_venv
    if errorlevel 1 (
        call :create_venv
        if errorlevel 1 exit /b 1
    )
    
    call venv\Scripts\activate.bat
    set VENV_PYTHON=python
    
    call :check_pip
    if errorlevel 1 exit /b 1
    
    call :check_requirements
    if errorlevel 1 (
        call :log_section "Instalando dependências"
        call :install_requirements
        if errorlevel 1 exit /b 1
    )
    
    call :create_directories
    
    echo.
    call :log_ok "Todas as validações OK! Iniciando aplicação..."
    echo.
) else (
    call :log_warn "Pulando validacoes (--skip-checks)"
    
    if not exist "venv" (
        call :log_error "venv não encontrada e --skip-checks foi usado"
        exit /b 1
    )
    
    call venv\Scripts\activate.bat
)

REM ======== INICIA A APLICAÇÃO ========

echo.
echo ========================================
echo [*] Iniciando aplicação...
echo ========================================
echo.
echo 🌐 Acesse: http://localhost:5000
echo.
echo Abrindo navegador em 3 segundos...
echo Pressione Ctrl+C para parar
echo.

REM Aguarda 3 segundos
timeout /t 3 /nobreak >nul

REM Tenta abrir o navegador
start http://localhost:5000 >nul 2>&1

REM Inicia a aplicação
python main.py
if errorlevel 1 (
    echo.
    call :log_error "Falha ao iniciar aplicação"
    echo     Use: run.bat --diagnose
    echo     para diagnosticar problemas
    exit /b 1
)

exit /b 0

call :main %*
