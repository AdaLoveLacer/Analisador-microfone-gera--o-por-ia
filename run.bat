@echo off
REM Script para iniciar o projeto em Windows
REM Com opções para limpeza de cache e reinstalação

setlocal enabledelayedexpansion

cls
echo.
echo ===== Analisador de Microfone com IA =====
echo.

REM Verifica argumentos
if "%1"=="--help" goto show_help
if "%1"=="-h" goto show_help
if "%1"=="--clean" goto clean_cache
if "%1"=="--reinstall" goto reinstall
if "%1"=="--delete-venv" goto delete_venv

REM ======================================
REM MODO NORMAL - Iniciar Aplicacao
REM ======================================

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Por favor, instale Python 3.8+
    echo.
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python encontrado: 
python --version
echo.

REM Verifica/cria ambiente virtual
if not exist "venv" (
    echo [*] Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar ambiente virtual
        pause
        exit /b 1
    )
    echo [OK] Ambiente virtual criado
    echo.
)

REM Ativa ambiente virtual
echo [*] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERRO] Falha ao ativar ambiente virtual
    pause
    exit /b 1
)
echo [OK] Ambiente virtual ativado
echo.

REM Verifica se já instalou as dependências
if not exist "venv\installed.txt" (
    echo [*] Instalando dependências (primeira execucao)...
    echo Isso pode levar alguns minutos...
    echo.
    python -m pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar dependências
        pause
        exit /b 1
    )
    type nul > venv\installed.txt
    echo [OK] Dependencias instaladas
    echo.
)

REM Download do modelo Whisper
echo [*] Verificando modelo Whisper...
python -c "import whisper; whisper.load_model('base')" 2>nul
if errorlevel 1 (
    echo [*] Baixando modelo Whisper (isso pode levar alguns minutos)...
    python -c "import whisper; whisper.load_model('base')"
    if errorlevel 1 (
        echo [AVISO] Falha ao baixar Whisper. Tente mais tarde.
    )
)
echo [OK] Modelo Whisper pronto
echo.

REM Cria diretórios necessários
if not exist "logs" mkdir logs
if not exist "database" mkdir database
if not exist "audio_library\memes" mkdir audio_library\memes 2>nul
if not exist "audio_library\efeitos" mkdir audio_library\efeitos 2>nul
if not exist "audio_library\notificacoes" mkdir audio_library\notificacoes 2>nul

REM Inicia a aplicação
echo.
echo ========================================
echo [*] Iniciando aplicacao...
echo ========================================
echo.
echo Acesse: http://localhost:5000
echo.
echo Abrindo navegador em 5 segundos...
echo Pressione Ctrl+C para parar
echo.

REM Abre a URL no navegador padrão (com delay para o servidor iniciar)
timeout /t 3 /nobreak >nul
start http://localhost:5000

python main.py
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao iniciar aplicacao
    pause
)
exit /b 0

REM ======================================
REM LIMPEZA DE CACHE PIP
REM ======================================
:clean_cache
echo [*] Limpando cache do pip...
pip cache purge
echo [OK] Cache limpo
echo.
echo Use: run.bat
echo (para iniciar normalmente)
exit /b 0

REM ======================================
REM REINSTALAÇÃO COMPLETA
REM ======================================
:reinstall
echo.
echo [AVISO] Isso vai:
echo   1. Deletar ambiente virtual
echo   2. Limpar cache do pip
echo   3. Recriar venv
echo   4. Reinstalar tudo
echo.
set /p confirm="Deseja continuar? (s/n): "
if /i not "%confirm%"=="s" (
    echo Cancelado
    exit /b 0
)

echo.
echo [*] Deletando ambiente virtual...
if exist "venv" (
    rmdir /s /q venv
    echo [OK] venv deletado
) else (
    echo [OK] venv nao existe
)

echo [*] Limpando cache do pip...
pip cache purge
echo [OK] Cache limpo

echo [*] Deletando marcador de instalação...
if exist "venv\installed.txt" del venv\installed.txt

echo.
echo [OK] Pronto para nova instalação!
echo.
echo Use: run.bat
echo (para reinstalar tudo do zero)
exit /b 0

REM ======================================
REM DELETAR VENV
REM ======================================
:delete_venv
echo [AVISO] Isso vai deletar o ambiente virtual
set /p confirm="Deseja continuar? (s/n): "
if /i not "%confirm%"=="s" (
    echo Cancelado
    exit /b 0
)

echo [*] Deletando venv...
if exist "venv" (
    rmdir /s /q venv
    echo [OK] venv deletado
    del venv\installed.txt 2>nul
) else (
    echo [OK] venv nao existe
)
exit /b 0

REM ======================================
REM AJUDA
REM ======================================
:show_help
echo.
echo Analisador de Microfone com IA - Script de Inicializacao
echo.
echo Uso: run.bat [opcao]
echo.
echo Opcoes:
echo   (nenhuma)     Inicia aplicacao normalmente
echo   --clean       Limpa cache do pip
echo   --reinstall   Reinstala tudo do zero (deleta venv + limpa cache)
echo   --delete-venv Deleta apenas o ambiente virtual
echo   --help, -h    Mostra esta mensagem
echo.
echo Exemplos:
echo   run.bat
echo   run.bat --clean
echo   run.bat --reinstall
echo.
pause
exit /b 0
