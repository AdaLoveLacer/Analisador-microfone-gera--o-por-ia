#!/bin/bash
# Setup e execução - Analisador de Microfone com IA (Linux/Mac)

set -e

# Detectar modo verbose
VERBOSE=false
if [ "$1" = "vv" ] || [ "$2" = "vv" ] || [ "$3" = "vv" ]; then
    VERBOSE=true
    set -x
    echo "🔍 Modo VERBOSE ativado"
    echo ""
fi

# Função para logar em verbose
vlog() {
    if [ "$VERBOSE" = true ]; then
        echo "  └─ $1" >&2
    fi
}

# ============ COMANDO WATCHDOG ============
if [ "$1" = "watchdog" ]; then
    shift  # Remove 'watchdog' dos argumentos
    bash "$(dirname "$0")/watchdog.sh" "${@:-status}"
    exit $?
fi

# ============ COMANDO STOP ============
if [ "$1" = "stop" ] || [ "$2" = "stop" ]; then
    echo "🛑 Matando processos da aplicação..."
    echo ""
    
    KILLED=0
    
    # Parar watchdog primeiro
    echo "🔍 Procurando Watchdog..."
    if [ -f "/tmp/watchdog.pid" ]; then
        WATCHDOG_PID=$(cat /tmp/watchdog.pid)
        if kill -0 "$WATCHDOG_PID" 2>/dev/null; then
            echo "   Encontrado! Parando Watchdog..."
            kill "$WATCHDOG_PID" 2>/dev/null || true
            sleep 1
            kill -9 "$WATCHDOG_PID" 2>/dev/null || true
            rm -f /tmp/watchdog.pid
            echo "✓ Watchdog parado"
            KILLED=$((KILLED+1))
        else
            rm -f /tmp/watchdog.pid
            echo "   ℹ️  Watchdog não estava rodando"
        fi
    else
        echo "   ℹ️  Watchdog não estava rodando"
    fi
    
    # Matar processos Python (main.py)
    echo "🔍 Procurando processos Python..."
    if pgrep -f "python.*main" > /dev/null 2>&1 || pgrep -f "main.py" > /dev/null 2>&1; then
        echo "   Encontrados! Parando Backend..."
        pkill -9 -f "python.*main" 2>/dev/null || true
        pkill -9 -f "main.py" 2>/dev/null || true
        sleep 1
        echo "✓ Backend parado"
        KILLED=$((KILLED+1))
    else
        echo "   ℹ️  Nenhum processo Python encontrado"
    fi
    
    # Matar processos npm/node (APENAS da nossa aplicação)
    echo "🔍 Procurando processos Node.js (Vite)..."
    # Procura específica por npm/vite/node do projeto
    if pgrep -f "npm run dev" > /dev/null 2>&1 || pgrep -f "vite" > /dev/null 2>&1 || pgrep -f "web-control" > /dev/null 2>&1; then
        echo "   Encontrados! Parando Frontend..."
        pkill -9 -f "npm run dev" 2>/dev/null || true
        pkill -9 -f "npm.*dev" 2>/dev/null || true
        pkill -9 -f "node.*vite" 2>/dev/null || true
        pkill -9 -f "vite" 2>/dev/null || true
        pkill -9 -f "web-control" 2>/dev/null || true
        sleep 1
        echo "✓ Frontend parado"
        KILLED=$((KILLED+1))
    else
        echo "   ℹ️  Nenhum processo Node.js encontrado"
    fi
    
    echo ""
    if [ $KILLED -eq 0 ]; then
        echo "✅ Nenhum processo da aplicação estava rodando"
    else
        echo "✅ $KILLED processo(s) parado(s)"
    fi
    
    # Verificação final
    echo ""
    echo "Verificação final:"
    if pgrep -f "python.*main" > /dev/null 2>&1 || pgrep -f "main.py" > /dev/null 2>&1; then
        echo "⚠️  Ainda existem processos Python rodando:"
        pgrep -a -f "python.*main" || pgrep -a -f "main.py"
    else
        echo "✓ Nenhum processo Python rodando"
    fi
    
    if pgrep -f "npm run dev" > /dev/null 2>&1 || pgrep -f "vite" > /dev/null 2>&1 || pgrep -f "web-control" > /dev/null 2>&1; then
        echo "⚠️  Ainda existem processos Node.js rodando (Frontend):"
        pgrep -a -f "npm run dev" 2>/dev/null || pgrep -a -f "vite" 2>/dev/null || pgrep -a -f "web-control" 2>/dev/null || true
    else
        echo "✓ Nenhum processo Node.js rodando"
    fi
    
    exit 0
fi

# ============ COMANDO PURGE ============
if [ "$1" = "purge" ] || [ "$2" = "purge" ]; then
    echo "🔴 PURGE - Limpeza completa"
    echo "=============================="
    echo ""
    
    bash "$0" stop 2>/dev/null || true
    sleep 1
    
    echo "Removendo venv..."
    rm -rf venv 2>/dev/null || true
    
    echo "Limpando cache Python..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    echo "Removendo logs..."
    rm -rf logs/*.log 2>/dev/null || true
    
    echo ""
    echo "✅ Purge concluído!"
    echo "Agora execute: bash run.sh"
    echo ""
    
    exit 0
fi

# ============ SETUP PRINCIPAL ============

echo "🎙️ Analisador de Microfone com IA"
echo "===================================="
echo ""

# ============ FASE 1: BACKEND ============

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║ FASE 1: BACKEND - Verificando Dependências                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Definir versão do Python a usar (3.11 é mais estável/compatível)
PYTHON_CMD="python3.11"
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "⚠️  Python 3.11 não encontrado, tentando python3..."
    PYTHON_CMD="python3"
fi

# 1. Verificar Python
echo "[1/3] Verificando Python..."
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ Python não encontrado"
    exit 1
fi
PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION (usando $PYTHON_CMD)"
echo ""

# 2. Criar venv
echo "[2/3] Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    echo "   ✓ venv criado com $PYTHON_CMD"
elif [ -f "venv/bin/python" ]; then
    # Verificar se o venv usa a versão correta
    VENV_PY_VERSION=$(venv/bin/python --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2)
    TARGET_PY_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$VENV_PY_VERSION" != "$TARGET_PY_VERSION" ]; then
        echo "   ⚠️  venv usa Python $VENV_PY_VERSION, recriando com Python $TARGET_PY_VERSION..."
        rm -rf venv
        $PYTHON_CMD -m venv venv
        echo "   ✓ venv recriado com $PYTHON_CMD"
    fi
fi
source venv/bin/activate
echo "✓ venv ativado"
echo ""

# 3. Atualizar pip
echo "[3/3] Atualizando pip..."
pip install --upgrade pip -q 2>&1 | tail -2 || true
echo "✓ pip atualizado"
echo ""

# ============ DEPENDÊNCIAS DO SISTEMA (BACKEND) ============

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║ Verificando Dependências do Sistema                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Detectar OS
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
            esac
            ;;
        apt)
            echo "$pkg"
            ;;
        dnf|yum)
            case "$pkg" in
                portaudio19-dev) echo "portaudio-devel" ;;
                build-essential) echo "gcc gcc-c++ make" ;;
                *) echo "$pkg" ;;
            esac
            ;;
        zypper)
            case "$pkg" in
                portaudio19-dev) echo "portaudio-devel" ;;
                build-essential) echo "gcc gcc-c++ make" ;;
                *) echo "$pkg" ;;
            esac
            ;;
        brew)
            case "$pkg" in
                portaudio19-dev) echo "portaudio" ;;
                *) echo "$pkg" ;;
            esac
            ;;
        *)
            echo "$pkg"
            ;;
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

# Verificar dependências do sistema
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
        pacman)
            echo "Executando: sudo pacman -Sy $MISSING_PACKAGES"
            sudo pacman -Sy $MISSING_PACKAGES || exit 1
            ;;
        apt)
            echo "Executando: sudo apt-get update && sudo apt-get install -y $MISSING_PACKAGES"
            sudo apt-get update && sudo apt-get install -y $MISSING_PACKAGES || exit 1
            ;;
        dnf)
            echo "Executando: sudo dnf install -y $MISSING_PACKAGES"
            sudo dnf install -y $MISSING_PACKAGES || exit 1
            ;;
        yum)
            echo "Executando: sudo yum install -y $MISSING_PACKAGES"
            sudo yum install -y $MISSING_PACKAGES || exit 1
            ;;
        zypper)
            echo "Executando: sudo zypper install -y $MISSING_PACKAGES"
            sudo zypper install -y $MISSING_PACKAGES || exit 1
            ;;
        brew)
            echo "Executando: brew install $MISSING_PACKAGES"
            brew install $MISSING_PACKAGES || exit 1
            ;;
        *)
            echo "❌ Gerenciador não detectado!"
            exit 1
            ;;
    esac
    
    echo ""
fi

echo "✓ Dependências do sistema OK"
echo ""

# ============ INSTALAR PYTHON ============

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║ Instalando Dependências Python (Backend)                      ║"
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

# ============ FASE 2: FRONTEND ============

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║ FASE 2: FRONTEND - Verificando Dependências                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar Node.js
echo "[1/2] Verificando Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado!"
    echo ""
    echo "Instale em: https://nodejs.org/"
    echo "Ou via seu gerenciador:"
    echo "  Arch: pacman -S nodejs npm"
    echo "  Debian: apt-get install -y nodejs npm"
    echo "  Fedora: dnf install -y nodejs npm"
    exit 1
fi

NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
echo "✓ Node.js $NODE_VERSION"
echo "✓ npm $NPM_VERSION"
echo ""

# Instalar dependências npm
echo "[2/2] Instalando dependências do Frontend..."
if [ ! -d "web-control/node_modules" ]; then
    echo ""
    echo "Executando: npm install --legacy-peer-deps (web-control/)"
    echo ""
    echo "📦 Instalando dependências Node.js (isso pode levar alguns minutos)..."
    echo "ℹ️  Flag --legacy-peer-deps está ativada para melhor compatibilidade"
    echo ""
    
    cd web-control
    npm install --legacy-peer-deps
    RESULT=$?
    cd ..
    
    if [ $RESULT -ne 0 ]; then
        echo ""
        echo "❌ Erro ao instalar dependências Frontend!"
        exit 1
    fi
    echo ""
    echo "✓ Dependências Frontend instaladas"
else
    echo "✓ Dependências Frontend já instaladas"
fi

echo ""

# ============ CRIAR DIRETÓRIOS ============

echo "Preparando estrutura de diretórios..."
mkdir -p logs data sounds models
echo "✓ Estrutura pronta"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETO!"
echo "════════════════════════════════════════════════════════════════"
echo ""

# ============ INICIAR SERVIDORES ============

echo "🚀 Iniciando Backend (Python FastAPI)..."
# Ativar venv e rodar backend
if [ -f "venv/bin/python" ]; then
    venv/bin/python main.py > /tmp/backend.log 2>&1 &
else
    python3 main.py > /tmp/backend.log 2>&1 &
fi
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
echo "🎨 Iniciando Frontend (Vite + React)..."

cd web-control
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "⏳ Aguardando Frontend..."
FRONTEND_READY=0
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend pronto em http://localhost:3000"
        FRONTEND_READY=1
        break
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend parou!"
        echo "Verifique logs:"
        tail -20 /tmp/frontend.log
        exit 1
    fi
    
    echo -n "."
    sleep 1
done

if [ $FRONTEND_READY -eq 0 ]; then
    echo ""
    echo "⚠️  Frontend não respondeu após 60s"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ APLICAÇÃO PRONTA!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Backend (FastAPI):  http://localhost:5000"
echo "  - API:            http://localhost:5000/api"
echo "  - Docs:           http://localhost:5000/docs"
echo "  - ReDoc:          http://localhost:5000/redoc"
echo ""
echo "Frontend (Vite):    http://localhost:3000"
echo ""
echo "PIDs: Backend=$BACKEND_PID, Frontend=$FRONTEND_PID"
echo ""

# Abrir navegador
if command -v xdg-open > /dev/null 2>&1; then
    xdg-open http://localhost:3000 > /dev/null 2>&1 &
elif command -v open > /dev/null 2>&1; then
    open http://localhost:3000 > /dev/null 2>&1 &
fi

echo ""
echo "💡 Dicas:"
echo "  - Para parar: pressione Ctrl+C"
echo "  - API Docs: http://localhost:5000/docs"
echo "  - Watchdog: bash run.sh watchdog start"
echo ""

# ============ MODO FOREGROUND vs BACKGROUND ============

# Se rodando em background (CI/CD), apenas aguarde
if [ "$1" = "foreground" ] || [ "$2" = "foreground" ] || [ -z "$1" ]; then
    # Modo interativo - permite Ctrl+C para parar
    cleanup() {
        echo ""
        echo ""
        echo "🛑 Parando aplicação..."
        kill $BACKEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        sleep 1
        echo "✅ Aplicação parada"
        exit 0
    }
    
    trap cleanup SIGINT SIGTERM
    
    echo ""
    echo "🎯 Executando em FOREGROUND (pressione Ctrl+C para parar)"
    echo ""
    
    while true; do
        # Verificar se os processos ainda estão vivos
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            echo "⚠️  Backend morreu!"
            tail -20 /tmp/backend.log
            break
        fi
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "⚠️  Frontend morreu!"
            tail -20 /tmp/frontend.log
            break
        fi
        sleep 2
    done
else
    # Modo background - inicia watchdog e exibe PIDs
    echo ""
    echo "🎯 Executando em BACKGROUND"
    echo ""
    
    # Iniciar watchdog automaticamente em background
    if [ "$1" != "no-watchdog" ] && [ "$2" != "no-watchdog" ]; then
        echo "🐕 Iniciando Watchdog para monitorar o backend..."
        bash "$(dirname "$0")/watchdog.sh" start 2>/dev/null || true
        echo ""
    fi
    
    echo "Para parar: bash run.sh stop"
    echo "Para logs:  tail -f /tmp/backend.log  ou  tail -f /tmp/frontend.log"
    echo "Watchdog:   bash run.sh watchdog status"
    echo ""
    exit 0
fi
