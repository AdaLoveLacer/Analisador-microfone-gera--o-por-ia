#!/bin/bash
# Setup e execução - Analisador de Microfone com IA (Linux/Mac)

set -e

# Detectar modo verbose
VERBOSE=false
if [ "$1" = "vv" ] || [ "$2" = "vv" ]; then
    VERBOSE=true
    set -x  # Ativar modo verbose do bash (mostra cada comando)
    echo "🔍 Modo VERBOSE ativado"
    echo ""
fi

# Função para logar em verbose
vlog() {
    if [ "$VERBOSE" = true ]; then
        echo "  └─ $1" >&2
    fi
}

# Verificar se foi passado comando "stop"
if [ "$1" = "stop" ] || [ "$2" = "stop" ]; then
    echo "🛑 Matando processos travados da aplicação..."
    echo ""
    
    KILLED=0
    
    # Matar processos Python especificamente de main.py
    if pgrep -f "python.*main.py" > /dev/null 2>&1; then
        echo "🔍 Encontrados processos Python (main.py)..."
        vlog "Enviando SIGTERM..."
        pkill -f "python.*main.py" 2>/dev/null
        sleep 2
        if ! pgrep -f "python.*main.py" > /dev/null 2>&1; then
            echo "✓ Processos Python (main.py) encerrados"
            KILLED=$((KILLED+1))
        else
            echo "⚠️  Força-kill em processos Python..."
            vlog "Enviando SIGKILL..."
            pkill -9 -f "python.*main.py" 2>/dev/null || true
            sleep 1
            echo "✓ Processos Python (main.py) força-encerrados"
            KILLED=$((KILLED+1))
        fi
    fi
    
    # Matar npm run dev (Next.js) - específico
    if pgrep -f "npm run dev" > /dev/null 2>&1; then
        echo "🔍 Encontrado processo Next.js (npm run dev)..."
        vlog "Enviando SIGTERM..."
        pkill -f "npm run dev" 2>/dev/null
        sleep 1
        if ! pgrep -f "npm run dev" > /dev/null 2>&1; then
            echo "✓ Processo Next.js (npm run dev) encerrado"
            KILLED=$((KILLED+1))
        else
            echo "⚠️  Força-kill em Next.js..."
            vlog "Enviando SIGKILL..."
            pkill -9 -f "npm run dev" 2>/dev/null || true
            sleep 1
            echo "✓ Processo Next.js força-encerrado"
            KILLED=$((KILLED+1))
        fi
    fi
    
    echo ""
    if [ $KILLED -eq 0 ]; then
        echo "✅ Nenhum processo da aplicação estava rodando"
    else
        echo "✅ $KILLED processo(s) encerrado(s) com sucesso"
    fi
    
    exit 0
fi

# Verificar se foi passado comando "purge"
if [ "$1" = "purge" ] || [ "$2" = "purge" ]; then
    echo "🔴 PURGE - Limpeza completa da instalação"
    echo "=========================================="
    echo ""
    
    # Parar processos primeiro
    echo "1️⃣ Parando aplicação..."
    vlog "Executando: bash run.sh stop"
    bash "$0" stop 2>/dev/null || true
    sleep 1
    echo ""
    
    # Remover venv
    echo "2️⃣ Removendo venv..."
    if [ -d "venv" ]; then
        rm -rf venv
        echo "   ✓ venv removido"
    else
        echo "   ℹ️  venv não encontrado"
    fi
    echo ""
    
    # Remover cache Python
    echo "3️⃣ Limpando cache Python..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    echo "   ✓ Cache Python limpo"
    echo ""
    
    # Remover logs
    echo "4️⃣ Removendo logs..."
    rm -rf logs/*.log 2>/dev/null || true
    echo "   ✓ Logs removidos"
    echo ""
    
    echo "✅ Purge concluído!"
    echo "🔄 Agora execute: bash run.sh"
    echo ""
    
    exit 0
fi

echo "🎙️ Analisador de Microfone com IA"
echo "=================================="
echo ""

# 1. Verificar Python
echo "[1/6] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado"
    exit 1
fi
echo "✓ Python $(python3 --version | cut -d' ' -f2)"

# 2. Criar venv
echo "[2/6] Verificando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
echo "✓ venv ativado"

# 3. Atualizar pip
echo "[3/6] Atualizando pip..."
pip install --upgrade pip -q
echo "✓ pip atualizado"

# 4. Instalar requirements Python
echo "[4/6] Instalando dependências Python..."
pip install -r requirements.txt --upgrade -q 2>&1 | grep -v "already satisfied" || true
echo "✓ Dependências Python instaladas"

# 4.5 Instalar dependências do Frontend (Node.js/npm)
echo "[4.5/6] Verificando dependências do Frontend..."
if [ ! -d "web-control/node_modules" ]; then
    echo "   Instalando pacotes npm para web-control..."
    cd web-control
    npm install --legacy-peer-deps 2>&1 | tail -5
    cd ..
    echo "✓ Dependências Frontend instaladas"
else
    echo "✓ Dependências Frontend já instaladas"
fi

# 5. Verificar dependências do sistema e validar imports
echo "[5/6] Verificando dependências do sistema e Python..."

# Ler arquivo DEPENDENCIES.txt
if [ ! -f "DEPENDENCIES.txt" ]; then
    echo "❌ Arquivo DEPENDENCIES.txt não encontrado!"
    echo "   Execute este script da raiz do projeto"
    exit 1
fi

# Detectar OS e gerenciador de pacotes
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
            DISTRO="CentOS/RHEL"
        elif command -v zypper &> /dev/null; then
            PKG_MANAGER="zypper"
            DISTRO="openSUSE"
        else
            PKG_MANAGER="unknown"
            DISTRO="Desconhecida"
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

# Função para converter nomes de pacotes para a distribuição
get_package_name() {
    local generic_name="$1"
    
    case "$PKG_MANAGER" in
        pacman)
            # Arch Linux - converter para pacman-style
            case "$generic_name" in
                portaudio19-dev) echo "portaudio" ;;
                build-essential) echo "base-devel" ;;
                libportaudio2) echo "portaudio" ;;
                *) echo "$generic_name" ;;
            esac
            ;;
        apt)
            # Debian/Ubuntu - mantém como está
            echo "$generic_name"
            ;;
        dnf|yum)
            # Fedora/RHEL
            case "$generic_name" in
                portaudio19-dev) echo "portaudio-devel" ;;
                build-essential) echo "gcc gcc-c++ make" ;;
                libportaudio2) echo "portaudio" ;;
                *) echo "$generic_name" ;;
            esac
            ;;
        zypper)
            # openSUSE
            case "$generic_name" in
                portaudio19-dev) echo "portaudio-devel" ;;
                build-essential) echo "gcc gcc-c++ make" ;;
                libportaudio2) echo "portaudio" ;;
                *) echo "$generic_name" ;;
            esac
            ;;
        brew)
            # macOS Homebrew
            case "$generic_name" in
                portaudio19-dev|libportaudio2) echo "portaudio" ;;
                *) echo "$generic_name" ;;
            esac
            ;;
        *)
            echo "$generic_name"
            ;;
    esac
}

# Função para verificar se pacote está instalado
is_package_installed() {
    local pkg_name="$1"
    
    case "$PKG_MANAGER" in
        pacman)
            pacman -Q "$pkg_name" &>/dev/null
            ;;
        apt)
            dpkg -l | grep -q "^ii.*${pkg_name}"
            ;;
        dnf)
            dnf list installed | grep -q "^${pkg_name}"
            ;;
        yum)
            yum list installed | grep -q "^${pkg_name}"
            ;;
        zypper)
            zypper se -i "$pkg_name" &>/dev/null
            ;;
        brew)
            brew list "$pkg_name" &>/dev/null
            ;;
        *)
            return 1
            ;;
    esac
}

# Detectar sistema
detect_package_manager
echo "   Sistema: $DISTRO ($PKG_MANAGER)"
echo ""

# Função para extrair dependências do DEPENDENCIES.txt
check_system_dependencies() {
    local missing_packages=""
    local missing_descriptions=""
    
    # Ler cada linha do DEPENDENCIES.txt
    while IFS='|' read -r dep_type dep_module dep_package dep_description dep_macos || [ -n "$dep_type" ]; do
        # Pular comentários e linhas vazias
        [[ "$dep_type" =~ ^#.*$ ]] && continue
        [[ -z "$dep_type" ]] && continue
        [[ "$dep_type" != "system" ]] && continue
        
        # Converter nome do pacote para a distribuição
        local converted_package=$(get_package_name "$dep_package")
        
        # Verificar se está instalado
        if ! is_package_installed "$converted_package"; then
            missing_packages="$missing_packages $converted_package"
            missing_descriptions="$missing_descriptions   - $dep_description ($converted_package)"$'\n'
            echo "   ❌ Faltando: $dep_description"
        else
            echo "   ✓ $dep_description"
        fi
    done < DEPENDENCIES.txt
    
    if [ -n "$missing_packages" ]; then
        echo ""
        echo "❌ Dependências do sistema ausentes:"
        echo -e "$missing_descriptions"
        echo ""
        
        case "$PKG_MANAGER" in
            pacman)
                echo "   Execute (Arch Linux):"
                echo "   sudo pacman -Sy $missing_packages"
                ;;
            apt)
                echo "   Execute (Debian/Ubuntu):"
                echo "   sudo apt-get update"
                echo "   sudo apt-get install -y $missing_packages"
                ;;
            dnf)
                echo "   Execute (Fedora/RHEL):"
                echo "   sudo dnf install -y $missing_packages"
                ;;
            yum)
                echo "   Execute (CentOS/RHEL):"
                echo "   sudo yum install -y $missing_packages"
                ;;
            zypper)
                echo "   Execute (openSUSE):"
                echo "   sudo zypper install -y $missing_packages"
                ;;
            brew)
                echo "   Execute (macOS):"
                echo "   brew install $missing_packages"
                ;;
            *)
                echo "   Gerenciador de pacotes não detectado!"
                echo "   Instale manualmente: $missing_packages"
                ;;
        esac
        echo ""
        
        return 1
    fi
    
    return 0
}

# Função para verificar módulos Python
check_python_dependencies() {
    local python_modules=""
    local missing_modules=""
    
    # Ler cada linha do DEPENDENCIES.txt para módulos Python
    while IFS='|' read -r dep_type dep_module dep_package dep_description dep_macos || [ -n "$dep_type" ]; do
        [[ "$dep_type" =~ ^#.*$ ]] && continue
        [[ -z "$dep_type" ]] && continue
        [[ "$dep_type" != "python" ]] && continue
        
        python_modules="$python_modules $dep_module:$dep_package"
    done < DEPENDENCIES.txt
    
    # Verificar cada módulo Python
    for module_info in $python_modules; do
        IFS=':' read -r module_name package_name <<< "$module_info"
        
        if ! python3 -c "import $module_name" 2>/dev/null; then
            missing_modules="$missing_modules $package_name"
            echo "   ❌ Faltando: $module_name ($package_name)"
        else
            echo "   ✓ $module_name"
        fi
    done
    
    if [ -n "$missing_modules" ]; then
        return 1
    fi
    
    return 0
}

# Verificar dependências do sistema
echo "   Verificando dependências do sistema..."
if ! check_system_dependencies; then
    echo "❌ Por favor, instale as dependências do sistema acima"
    exit 1
fi

echo ""
echo "   Verificando módulos Python..."
if ! check_python_dependencies; then
    echo ""
    echo "⚠️  Instalando dependências Python faltantes..."
    echo "   pip install -r requirements.txt --upgrade"
    
    pip install -r requirements.txt --upgrade 2>&1 | tail -10
    INSTALL_RESULT=$?
    
    if [ $INSTALL_RESULT -ne 0 ]; then
        echo ""
        echo "❌ Erro ao instalar dependências Python!"
        echo "   Verifique requirements.txt e tente novamente"
        exit 1
    fi
    
    echo ""
    echo "   Re-verificando módulos Python..."
    if ! check_python_dependencies; then
        echo ""
        echo "❌ Algumas dependências ainda não estão disponíveis"
        echo "   Verifique os erros acima e DEPENDENCIES.txt"
        exit 1
    fi
fi

echo "✓ Todas as dependências verificadas com sucesso"

# 6. Criar diretórios
echo "[6/6] Preparando estrutura..."
mkdir -p logs data sounds models
echo "✓ Diretórios criados"

echo ""
echo "✅ Setup completo!"
echo ""

# Iniciar backend em background
echo "🚀 Iniciando Backend (Python Flask)..."
python3 main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

# Aguardar backend estar pronto (com timeout)
echo "⏳ Aguardando Backend carregar..."
BACKEND_READY=0
for i in {1..30}; do
    if curl -s http://localhost:5000/api/status > /dev/null 2>&1; then
        echo "✅ Backend pronto em http://localhost:5000"
        BACKEND_READY=1
        break
    fi
    
    # Verificar se o processo backend ainda está rodando
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend parou inesperadamente"
        echo "Logs:"
        tail -20 /tmp/backend.log
        exit 1
    fi
    
    echo -n "."
    sleep 1
done

if [ $BACKEND_READY -eq 0 ]; then
    echo ""
    echo "⚠️  Backend não respondeu após 30s"
    echo "Tentando iniciar frontend mesmo assim..."
fi

echo ""
echo "🎨 Iniciando Frontend (Next.js)..."
cd web-control
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

# Aguardar frontend estar pronto (com timeout maior)
echo "⏳ Aguardando Frontend carregar..."
FRONTEND_READY=0
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend pronto em http://localhost:3000"
        FRONTEND_READY=1
        break
    fi
    
    # Verificar se o processo frontend ainda está rodando
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend parou inesperadamente"
        echo "Logs:"
        tail -20 /tmp/frontend.log
        exit 1
    fi
    
    echo -n "."
    sleep 1
done

if [ $FRONTEND_READY -eq 0 ]; then
    echo ""
    echo "⚠️  Frontend não respondeu após 60s"
    echo "Tentando abrir navegador mesmo assim..."
fi

echo ""
echo "✅ Aplicação pronta!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Abrindo interface no navegador..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Abrir navegador
if command -v xdg-open > /dev/null 2>&1; then
    xdg-open http://localhost:3000 > /dev/null 2>&1 &
elif command -v open > /dev/null 2>&1; then
    open http://localhost:3000 > /dev/null 2>&1 &
elif command -v start > /dev/null 2>&1; then
    start http://localhost:3000 > /dev/null 2>&1 &
else
    echo "⚠️  Navegador não detectado. Acesse manualmente: http://localhost:3000"
fi

echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:5000"
echo ""
echo "PIDs: Backend=$BACKEND_PID, Frontend=$FRONTEND_PID"
echo ""
echo "Para parar: pressione Ctrl+C"
echo ""

# Função para limpar processos quando o script é interrompido
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

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM

# Manter processo rodando e mostrar que está em execução
while true; do
    sleep 1
done
