#!/bin/bash
# Backend only - Analisador de Microfone com IA

set -e

echo "🎙️ Analisador de Microfone - BACKEND"
echo "======================================"
echo ""

# ============ COMANDO STOP ============
if [ "$1" = "stop" ]; then
    echo "🛑 Parando Backend..."
    pkill -9 -f "python.*main" 2>/dev/null || true
    pkill -9 -f "main.py" 2>/dev/null || true
    sleep 1
    echo "✅ Backend parado"
    exit 0
fi

# ============ COMANDO PURGE ============
if [ "$1" = "purge" ]; then
    echo "🔴 Limpeza do Backend"
    bash "$0" stop 2>/dev/null || true
    rm -rf venv logs/*.log 2>/dev/null || true
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    echo "✅ Purge concluído"
    exit 0
fi

# ============ SETUP ============

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║ BACKEND - Verificando Dependências                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar Python
echo "[1/3] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION"
echo ""

# Criar venv
echo "[2/3] Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
echo "✓ venv ativado"
echo ""

# Atualizar pip
echo "[3/3] Atualizando pip..."
pip install --upgrade pip -q 2>&1 | tail -1 || true
echo "✓ pip atualizado"
echo ""

# ============ DEPENDÊNCIAS DO SISTEMA ============

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║ Verificando Dependências do Sistema                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

detect_package_manager() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v pacman &> /dev/null; then
            PKG_MANAGER="pacman"
            DISTRO="Arch Linux"
        elif command -v apt-get &> /dev/null; then
            PKG_MANAGER="apt"
            DISTRO="Debian/Ubuntu"
        elif command -v dnf &> /dev/null; then
            PKG_MANAGER="dnf"
            DISTRO="Fedora/RHEL"
        elif command -v yum &> /dev/null; then
            PKG_MANAGER="yum"
            DISTRO="CentOS"
        elif command -v zypper &> /dev/null; then
            PKG_MANAGER="zypper"
            DISTRO="openSUSE"
        else
            PKG_MANAGER="unknown"
            DISTRO="Linux (desconhecida)"
        fi
        OS_TYPE="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        PKG_MANAGER="brew"
        DISTRO="macOS"
        OS_TYPE="macos"
    else
        OS_TYPE="unknown"
        PKG_MANAGER="unknown"
        DISTRO="Desconhecida"
    fi
}

get_package_name() {
    local pkg="$1"
    case "$PKG_MANAGER" in
        pacman)
            case "$pkg" in
                portaudio19-dev) echo "portaudio" ;;
                build-essential) echo "base-devel" ;;
                *) echo "$pkg" ;;
            esac ;;
        apt) echo "$pkg" ;;
        dnf|yum)
            case "$pkg" in
                portaudio19-dev) echo "portaudio-devel" ;;
                build-essential) echo "gcc gcc-c++ make" ;;
                *) echo "$pkg" ;;
            esac ;;
        zypper)
            case "$pkg" in
                portaudio19-dev) echo "portaudio-devel" ;;
                build-essential) echo "gcc gcc-c++ make" ;;
                *) echo "$pkg" ;;
            esac ;;
        brew)
            case "$pkg" in
                portaudio19-dev) echo "portaudio" ;;
                *) echo "$pkg" ;;
            esac ;;
        *) echo "$pkg" ;;
    esac
}

is_package_installed() {
    local pkg="$1"
    case "$PKG_MANAGER" in
        pacman) pacman -Q "$pkg" &>/dev/null ;;
        apt) dpkg -l | grep -q "^ii.*${pkg}" ;;
        dnf) dnf list installed | grep -q "^${pkg}" ;;
        yum) yum list installed | grep -q "^${pkg}" ;;
        zypper) zypper se -i "$pkg" &>/dev/null ;;
        brew) brew list "$pkg" &>/dev/null ;;
        *) return 1 ;;
    esac
}

detect_package_manager
echo "Sistema: $DISTRO ($PKG_MANAGER)"
echo ""

if [ ! -f "DEPENDENCIES.txt" ]; then
    echo "❌ DEPENDENCIES.txt não encontrado!"
    exit 1
fi

echo "Verificando dependências do sistema..."
MISSING_PACKAGES=""

while IFS='|' read -r dep_type dep_module dep_package dep_description dep_macos || [ -n "$dep_type" ]; do
    [[ "$dep_type" =~ ^#.*$ ]] && continue
    [[ -z "$dep_type" ]] && continue
    [[ "$dep_type" != "system" ]] && continue
    
    converted=$(get_package_name "$dep_package")
    
    if ! is_package_installed "$converted"; then
        MISSING_PACKAGES="$MISSING_PACKAGES $converted"
        echo "❌ Faltando: $dep_description"
    else
        echo "✓ $dep_description"
    fi
done < DEPENDENCIES.txt

if [ -n "$MISSING_PACKAGES" ]; then
    echo ""
    echo "⚠️  INSTALANDO DEPENDÊNCIAS DO SISTEMA..."
    echo ""
    
    case "$PKG_MANAGER" in
        pacman) sudo pacman -Sy $MISSING_PACKAGES || exit 1 ;;
        apt) sudo apt-get update && sudo apt-get install -y $MISSING_PACKAGES || exit 1 ;;
        dnf) sudo dnf install -y $MISSING_PACKAGES || exit 1 ;;
        yum) sudo yum install -y $MISSING_PACKAGES || exit 1 ;;
        zypper) sudo zypper install -y $MISSING_PACKAGES || exit 1 ;;
        brew) brew install $MISSING_PACKAGES || exit 1 ;;
        *) echo "❌ Gerenciador não detectado!"; exit 1 ;;
    esac
    echo ""
fi

echo "✓ Dependências do sistema OK"
echo ""

# ============ INSTALAR PYTHON ============

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║ Instalando Dependências Python                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "Executando: pip install -r requirements.txt --upgrade"
echo ""
echo "📦 Instalando pacotes Python (isso pode levar alguns minutos)..."
echo ""

pip install -r requirements.txt --upgrade

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Erro ao instalar dependências Python!"
    exit 1
fi

echo ""
echo "✓ Dependências Python instaladas"
echo ""

# ============ CRIAR DIRETÓRIOS ============

echo "Preparando estrutura de diretórios..."
mkdir -p logs data sounds models
echo "✓ Estrutura pronta"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ SETUP BACKEND COMPLETO!"
echo "════════════════════════════════════════════════════════════════"
echo ""

# ============ INICIAR BACKEND ============

echo "🚀 Iniciando Backend (FastAPI)..."
python3 main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

echo "⏳ Aguardando Backend..."
BACKEND_READY=0
for i in {1..30}; do
    if curl -s http://localhost:5000/api/status > /dev/null 2>&1; then
        echo "✅ Backend pronto em http://localhost:5000"
        BACKEND_READY=1
        break
    fi
    
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend parou!"
        echo "Verifique logs:"
        tail -20 /tmp/backend.log
        exit 1
    fi
    
    echo -n "."
    sleep 1
done

if [ $BACKEND_READY -eq 0 ]; then
    echo ""
    echo "⚠️  Backend não respondeu após 30s"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ BACKEND RODANDO!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Backend (FastAPI): http://localhost:5000"
echo "  - API:           http://localhost:5000/api"
echo "  - Docs:          http://localhost:5000/docs"
echo "  - ReDoc:         http://localhost:5000/redoc"
echo ""
echo "PID: $BACKEND_PID"
echo ""
echo "💡 Dicas:"
echo "  - Para parar:    bash run-backend.sh stop"
echo "  - Para logs:     tail -f /tmp/backend.log"
echo "  - Para purge:    bash run-backend.sh purge"
echo ""

# Limpeza ao sair
cleanup() {
    echo ""
    echo ""
    echo "🛑 Parando Backend..."
    kill $BACKEND_PID 2>/dev/null || true
    sleep 1
    echo "✅ Backend parado"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "Executando em FOREGROUND (pressione Ctrl+C para parar)"
echo ""

while true; do
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "⚠️  Backend morreu!"
        tail -20 /tmp/backend.log
        break
    fi
    sleep 2
done
