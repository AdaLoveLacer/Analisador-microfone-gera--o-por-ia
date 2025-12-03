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

REM Verifica se Python global existe SOMENTE para criar venv (sem mensagem)
if not exist "venv" if not exist ".venv" (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Python nao encontrado. Por favor, instale Python 3.8+
        echo.
        echo Baixe em: https://www.python.org/downloads/
        echo Marque: "Add Python to PATH"
        pause
        exit /b 1
    )
)
echo.

REM Verifica qual tipo de venv existe
if exist "venv" (
    echo [OK] Ambiente virtual encontrado (venv/)
    REM Se tambem existe .venv, deleta para evitar confusao
    if exist ".venv" (
        echo [*] Deletando .venv duplicado...
        rmdir /s /q ".venv" 2>nul
        echo [OK] .venv deletado
    )
    
    REM Pergunta se quer fazer limpeza completa
    echo.
    echo [?] Opcoes disponiveis:
    echo    1) Continuar com setup atual (padrao)
    echo    2) Limpar tudo e reinstalar do zero
    echo    3) Limpar apenas cache pip
    echo.
    set /p setup_option="    Escolha uma opcao (1-3, padrao=1): "
    if "!setup_option!"=="" set setup_option=1
    
    if "!setup_option!"=="2" (
        echo [*] Limpando ambiente virtual...
        rmdir /s /q "venv" 2>nul
        echo [OK] venv deletado
        echo [*] Limpando cache pip...
        python -m pip cache purge 2>nul
        echo [OK] Cache pip limpo
        echo [*] Criando novo venv...
        python -m venv venv
        if errorlevel 1 (
            echo [ERRO] Falha ao criar ambiente virtual
            echo [DICA] Certifique-se de que Python esta instalado e no PATH
            pause
            exit /b 1
        )
        echo [OK] Novo venv criado
        REM Ativa o novo venv para instalar dependências
        call venv\Scripts\activate.bat
    ) else if "!setup_option!"=="3" (
        echo [*] Limpando cache pip...
        call venv\Scripts\activate.bat
        python -m pip cache purge 2>nul
        echo [OK] Cache pip limpo
    )
) else if exist ".venv" (
    echo [OK] Ambiente virtual encontrado (.venv/)
    REM Renomeia para venv para consistencia
    echo [*] Renomeando .venv para venv...
    move ".venv" "venv" >nul 2>&1
    if errorlevel 1 (
        echo [*] Criando novo venv...
        rmdir /s /q ".venv" 2>nul
        python -m venv venv
        if errorlevel 1 (
            echo [ERRO] Falha ao criar ambiente virtual
            pause
            exit /b 1
        )
    )
    echo [OK] Ambiente virtual pronto
) else (
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

REM Agora SEMPRE usa Python da venv
set PYTHON_BIN=venv\Scripts\python.exe
echo [OK] Ambiente virtual ativado
echo [*] Usando Python da venv: %PYTHON_BIN%
echo.

REM Verifica se as dependências estão instaladas (com Python da venv)
echo [*] Verificando dependências...
%PYTHON_BIN% -c "import whisper, sentence_transformers, sklearn, thefuzz, flask, socketio, pyaudio, pygame, sqlalchemy" >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Algumas dependências estão faltando ou desatualizadas
    echo.
    set /p install_deps="Deseja instalar as dependências agora? (s/n): "
    if /i not "!install_deps!"=="s" (
        echo [ERRO] Dependências necessárias não estão instaladas
        echo Use: run.bat --reinstall
        pause
        exit /b 1
    )
    echo [*] Instalando dependências...
    echo Isso pode levar alguns minutos...
    echo.
    
    REM Cria diretório de cache se não existir
    if not exist "pip-cache" mkdir pip-cache
    
    REM Atualiza pip primeiro
    %PYTHON_BIN% -m pip install --upgrade pip --cache-dir pip-cache
    
    REM Instala PyTorch com CUDA 11.8 PRIMEIRO (sem --quiet para ver erros reais)
    echo [*] Instalando PyTorch com CUDA 11.8...
    echo Isso pode levar alguns minutos...
    %PYTHON_BIN% -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --cache-dir pip-cache
    if errorlevel 1 (
        echo [AVISO] Falha ao instalar PyTorch com CUDA
        echo [*] Tentando CPU fallback...
        %PYTHON_BIN% -m pip install torch torchvision torchaudio --cache-dir pip-cache
    )
    echo.
    
    REM Agora instala demais dependências
    echo [*] Instalando demais dependências...
    %PYTHON_BIN% -m pip install -r requirements.txt --cache-dir pip-cache
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar dependências
        pause
        exit /b 1
    )
    
    echo [OK] Dependencias instaladas
    echo.
) else (
    echo [OK] Todas as dependências estão instaladas
    echo.
    
    REM Verifica se PyTorch com CUDA está instalado
    %PYTHON_BIN% -c "import torch; cuda_status = 'CUDA' if torch.cuda.is_available() else 'CPU'; device_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'; print(f'PyTorch {torch.__version__} - Device: {device_name}')" 2>nul
    
    echo.
)

REM Download do modelo Whisper (com Python da venv)
echo [*] Verificando modelo Whisper...
%PYTHON_BIN% -c "import whisper; model = whisper.load_model('base'); print('Modelo carregado com sucesso')" >nul 2>&1
if errorlevel 1 (
    echo [*] Tentando baixar modelo Whisper - isso pode levar alguns minutos...
    %PYTHON_BIN% -c "import whisper; model = whisper.load_model('base')" >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Modelo Whisper baixado com sucesso
    ) else (
        echo [AVISO] Falha ao baixar Whisper.
        echo [AVISO] Pode usar o programa sem Whisper, mas nao conseguira transcrever audio.
    )
) else (
    echo [OK] Modelo Whisper ja esta pronto
)
echo.

REM Cria diretórios necessários
if not exist "logs" mkdir logs
if not exist "database" mkdir database
if not exist "audio_library\memes" mkdir audio_library\memes 2>nul
if not exist "audio_library\efeitos" mkdir audio_library\efeitos 2>nul
if not exist "audio_library\notificacoes" mkdir audio_library\notificacoes 2>nul

REM Inicia a aplicação usando Python da venv
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

REM IMPORTANTE: Sempre usa Python da venv
%PYTHON_BIN% main.py
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
