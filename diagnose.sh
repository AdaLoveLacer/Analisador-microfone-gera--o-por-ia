#!/bin/bash
# Script de diagnóstico completo do sistema para o projeto
# Executa em Linux/macOS para identificar problemas

set -e

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# ======== FUNÇÕES ========

check() {
    local name="$1"
    local command="$2"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "🔍 $name ... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSOU${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}✗ FALHOU${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

check_version() {
    local name="$1"
    local command="$2"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "🔍 $name ... "
    
    if VERSION=$($command 2>/dev/null); then
        echo -e "${GREEN}✓ $VERSION${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}✗ NÃO ENCONTRADO${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}▶ $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# ======== DIAGNÓSTICO ========

clear
echo -e "${YELLOW}"
echo "╔═══════════════════════════════════════════════════╗"
echo "║  Analisador de Microfone - Diagnóstico do Sistema  ║"
echo "╚═══════════════════════════════════════════════════╝"
echo -e "${NC}"

section "Sistema Operacional"
check_version "Sistema" "uname -s"
check_version "Kernel" "uname -r"

section "Dependências do Sistema"
check "ffmpeg" "command -v ffmpeg"
check "portaudio (libportaudio)" "ldconfig -p 2>/dev/null | grep -q libportaudio"
check "ALSA (libasound2)" "ldconfig -p 2>/dev/null | grep -q libasound"
check "Git" "command -v git"
check "curl/wget" "command -v curl || command -v wget"

section "Python"
check_version "Python 3" "python3 --version"
check_version "pip" "python3 -m pip --version"

# Verifica se Python é 3.8+
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' 2>/dev/null)
if [ ! -z "$PYTHON_VERSION" ]; then
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [[ $MAJOR -ge 3 && $MINOR -ge 8 ]]; then
        echo -e "${GREEN}✓ Python $PYTHON_VERSION (OK - 3.8+)${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}✗ Python $PYTHON_VERSION (REQUER 3.8+)${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

section "Ambiente Virtual"
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ venv encontrado${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    
    if [ -f "venv/bin/python" ]; then
        echo -e "${GREEN}✓ Python da venv funcional${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    else
        echo -e "${RED}✗ Python da venv não encontrado${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    fi
else
    echo -e "${YELLOW}! venv não encontrado (será criado automaticamente)${NC}"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

section "Pacotes Python Críticos"

if [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
else
    PYTHON="python3"
fi

check "Flask" "$PYTHON -c 'import flask'"
check "Whisper" "$PYTHON -c 'import whisper'"
check "PyTorch" "$PYTHON -c 'import torch'"
check "Transformers" "$PYTHON -c 'import transformers'"
check "Sentence-Transformers" "$PYTHON -c 'import sentence_transformers'"
check "SQLAlchemy" "$PYTHON -c 'import sqlalchemy'"
check "PyAudio" "$PYTHON -c 'import pyaudio'"
check "Flask-SocketIO" "$PYTHON -c 'import flask_socketio'"

section "GPU e CUDA"

if [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    GPU_INFO=$($PYTHON -c "import torch; print('CUDA' if torch.cuda.is_available() else 'CPU')" 2>/dev/null)
    
    if [ "$GPU_INFO" = "CUDA" ]; then
        echo -e "${GREEN}✓ GPU (CUDA) disponível${NC}"
        
        GPU_NAME=$($PYTHON -c "import torch; print(torch.cuda.get_device_name(0))" 2>/dev/null)
        GPU_MEMORY=$($PYTHON -c "import torch; print(f'{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB')" 2>/dev/null)
        
        echo "   GPU: $GPU_NAME"
        echo "   VRAM: $GPU_MEMORY"
        
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    else
        echo -e "${YELLOW}! Usando CPU (GPU não disponível)${NC}"
        echo "   Para acelerar, instale: NVIDIA Driver + CUDA 11.8 toolkit"
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    fi
else
    echo -e "${YELLOW}! PyTorch não encontrado, não posso verificar GPU${NC}"
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

section "Modelos AI"

if [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    # Whisper
    if $PYTHON -c "import whisper; whisper.load_model('base')" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Modelo Whisper 'base' (140 MB)${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${YELLOW}⟳ Modelo Whisper será baixado na primeira execução (140 MB)${NC}"
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    # Phi-2
    TRANSFORMERS_CACHE="${HOME}/.cache/huggingface/hub"
    if [ -d "$TRANSFORMERS_CACHE" ] && ls -1 "$TRANSFORMERS_CACHE" 2>/dev/null | grep -q "phi"; then
        echo -e "${GREEN}✓ Modelo Phi-2 (cache local)${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${YELLOW}⟳ Modelo Phi-2 será baixado na primeira execução (3.8 GB)${NC}"
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

section "Espaço em Disco"

AVAILABLE_SPACE=$(df -h . | awk 'NR==2 {print $4}')
REQUIRED_SPACE="20GB"

echo "📊 Espaço disponível: $AVAILABLE_SPACE"
echo "📌 Espaço mínimo necessário: $REQUIRED_SPACE"

AVAILABLE_GB=$(df . | awk 'NR==2 {print $4}' | awk '{print int($1/1024/1024)}')
if [ $AVAILABLE_GB -gt 20 ]; then
    echo -e "${GREEN}✓ Espaço suficiente${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${RED}✗ Espaço insuficiente${NC}"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

section "Arquivos de Configuração"

check "requirements.txt" "test -f requirements.txt"
check "main.py" "test -f main.py"
check "web/app.py" "test -f web/app.py"

section "Diretórios"

check "Diretório logs" "test -d logs"
check "Diretório database" "test -d database"
check "Diretório audio_library" "test -d audio_library"

section "Portas"

check "Porta 5000 disponível" "! netstat -tuln 2>/dev/null | grep -q ':5000 ' && ! ss -tuln 2>/dev/null | grep -q ':5000 '"
check "Porta 3000 disponível" "! netstat -tuln 2>/dev/null | grep -q ':3000 ' && ! ss -tuln 2>/dev/null | grep -q ':3000 '"

# ======== RESUMO ========

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}▶ RESUMO${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "Total de verificações: $TOTAL_CHECKS"
echo -e "${GREEN}Passou: $PASSED_CHECKS${NC}"

if [ $FAILED_CHECKS -gt 0 ]; then
    echo -e "${RED}Falhou: $FAILED_CHECKS${NC}"
else
    echo -e "${GREEN}Falhou: $FAILED_CHECKS${NC}"
fi

echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ Sistema pronto para usar!          ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════╝${NC}"
    echo ""
    echo "Execute: ./run.sh"
    exit 0
else
    echo -e "${YELLOW}╔═══════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⚠ Alguns problemas encontrados      ║${NC}"
    echo -e "${YELLOW}╚═══════════════════════════════════════╝${NC}"
    echo ""
    echo "Dicas de resolução:"
    
    if ! command -v ffmpeg &> /dev/null; then
        echo "  • Instale ffmpeg: sudo apt install ffmpeg"
    fi
    
    if ! ldconfig -p 2>/dev/null | grep -q libportaudio; then
        echo "  • Instale PortAudio: sudo apt install portaudio19-dev"
    fi
    
    if [ $FAILED_CHECKS -lt 5 ]; then
        echo "  • Execute: ./run.sh"
        echo "    Os demais problemas serão resolvidos automaticamente"
    fi
    
    exit 1
fi
