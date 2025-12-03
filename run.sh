#!/bin/bash
# Script para iniciar o projeto em ambiente Unix/Linux/Mac
# Com opções para limpeza de cache e reinstalação

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções
show_help() {
    echo -e "${BLUE}"
    echo "Analisador de Microfone com IA - Script de Inicialização"
    echo -e "${NC}"
    echo ""
    echo "Uso: ./run.sh [opção]"
    echo ""
    echo "Opções:"
    echo "  (nenhuma)     Inicia aplicação normalmente"
    echo "  --clean       Limpa cache do pip"
    echo "  --reinstall   Reinstala tudo do zero (deleta venv + limpa cache)"
    echo "  --delete-venv Deleta apenas o ambiente virtual"
    echo "  --help, -h    Mostra esta mensagem"
    echo ""
    echo "Exemplos:"
    echo "  ./run.sh"
    echo "  ./run.sh --clean"
    echo "  ./run.sh --reinstall"
    echo ""
}

clean_cache() {
    echo -e "${YELLOW}[*] Limpando cache do pip...${NC}"
    pip cache purge
    echo -e "${GREEN}[OK] Cache limpo${NC}"
    echo ""
    echo "Use: ./run.sh"
    echo "(para iniciar normalmente)"
}

reinstall_all() {
    echo ""
    echo -e "${YELLOW}[AVISO] Isso vai:${NC}"
    echo "  1. Deletar ambiente virtual"
    echo "  2. Limpar cache do pip"
    echo "  3. Recriar venv"
    echo "  4. Reinstalar tudo"
    echo ""
    read -p "Deseja continuar? (s/n): " confirm
    
    if [[ ! "$confirm" =~ ^[Ss]$ ]]; then
        echo "Cancelado"
        return 1
    fi
    
    echo ""
    echo -e "${YELLOW}[*] Deletando ambiente virtual...${NC}"
    if [ -d "venv" ]; then
        rm -rf venv
        echo -e "${GREEN}[OK] venv deletado${NC}"
    else
        echo -e "${GREEN}[OK] venv não existe${NC}"
    fi
    
    echo -e "${YELLOW}[*] Limpando cache do pip...${NC}"
    pip cache purge
    echo -e "${GREEN}[OK] Cache limpo${NC}"
    
    echo ""
    echo -e "${GREEN}[OK] Pronto para nova instalação!${NC}"
    echo ""
    echo "Use: ./run.sh"
    echo "(para reinstalar tudo do zero)"
}

delete_venv() {
    echo -e "${YELLOW}[AVISO] Isso vai deletar o ambiente virtual${NC}"
    read -p "Deseja continuar? (s/n): " confirm
    
    if [[ ! "$confirm" =~ ^[Ss]$ ]]; then
        echo "Cancelado"
        return 1
    fi
    
    echo -e "${YELLOW}[*] Deletando venv...${NC}"
    if [ -d "venv" ]; then
        rm -rf venv
        echo -e "${GREEN}[OK] venv deletado${NC}"
    else
        echo -e "${GREEN}[OK] venv não existe${NC}"
    fi
}

# Processar argumentos
case "$1" in
    --help|-h)
        show_help
        exit 0
        ;;
    --clean)
        clean_cache
        exit 0
        ;;
    --reinstall)
        reinstall_all
        exit 0
        ;;
    --delete-venv)
        delete_venv
        exit 0
        ;;
    "")
        # Continuar com inicialização normal
        ;;
    *)
        echo -e "${RED}Opção desconhecida: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

# ======================================
# MODO NORMAL - Iniciar Aplicação
# ======================================

echo -e "${GREEN}=== Analisador de Microfone com IA ===${NC}\n"

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado. Por favor, instale Python 3.8+${NC}"
    echo "Instale com: sudo apt install python3 (Linux) ou brew install python3 (Mac)"
    exit 1
fi

echo -e "${GREEN}✓ Python encontrado: $(python3 --version)${NC}\n"

# Verifica qual tipo de venv existe
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Ambiente virtual encontrado (venv/)${NC}"
    
    # Pergunta sobre opções de setup
    echo ""
    echo -e "${BLUE}[?] Opcoes disponiveis:${NC}"
    echo "    1) Continuar com setup atual (padrao)"
    echo "    2) Limpar tudo e reinstalar do zero"
    echo "    3) Limpar apenas cache pip"
    echo ""
    read -p "    Escolha uma opcao (1-3, padrao=1): " setup_option
    setup_option=${setup_option:-1}
    
    if [ "$setup_option" = "2" ]; then
        echo -e "${YELLOW}[*] Limpando ambiente virtual...${NC}"
        rm -rf venv
        echo -e "${GREEN}[OK] venv deletado${NC}"
        echo -e "${YELLOW}[*] Limpando cache pip...${NC}"
        python3 -m pip cache purge 2>/dev/null
        echo -e "${GREEN}[OK] Cache pip limpo${NC}"
        echo -e "${YELLOW}[*] Criando novo venv...${NC}"
        python3 -m venv venv
        echo -e "${GREEN}[OK] Novo venv criado${NC}"
    elif [ "$setup_option" = "3" ]; then
        echo -e "${YELLOW}[*] Limpando cache pip...${NC}"
        source venv/bin/activate
        python3 -m pip cache purge 2>/dev/null
        echo -e "${GREEN}[OK] Cache pip limpo${NC}"
    fi
elif [ -d ".venv" ]; then
    echo -e "${GREEN}✓ Ambiente virtual encontrado (.venv/)${NC}"
    # Renomeia para venv para consistência
    mv .venv venv
    echo -e "${GREEN}✓ Renomeado .venv para venv${NC}"
else
    echo -e "${YELLOW}📦 Criando ambiente virtual...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERRO] Falha ao criar ambiente virtual${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Ambiente virtual criado${NC}\n"
fi

# Ativa ambiente virtual
echo -e "${YELLOW}🔧 Ativando ambiente virtual...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERRO] Falha ao ativar ambiente virtual${NC}"
    exit 1
fi

# IMPORTANTE: Sempre usa Python da venv
PYTHON_BIN="venv/bin/python3"
echo -e "${GREEN}✓ Ambiente virtual ativado${NC}"
echo -e "${YELLOW}[*] Usando Python da venv: $PYTHON_BIN${NC}"
echo ""

# Instala dependências (com Python da venv)
if [ ! -f "venv/installed.txt" ]; then
    echo -e "${YELLOW}📥 Instalando dependências (primeira execução)...${NC}"
    echo "Isso pode levar alguns minutos..."
    echo ""
    
    # Cria diretório de cache se não existir
    mkdir -p pip-cache
    
    # Atualiza pip primeiro
    $PYTHON_BIN -m pip install --upgrade pip --cache-dir pip-cache
    
    # Instala PyTorch com CUDA 11.8 PRIMEIRO (sem --quiet para ver erros reais)
    echo -e "${YELLOW}[*] Instalando PyTorch com CUDA 11.8...${NC}"
    echo "Isso pode levar alguns minutos..."
    $PYTHON_BIN -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --cache-dir pip-cache
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}[AVISO] Falha ao instalar PyTorch com CUDA${NC}"
        echo -e "${YELLOW}[*] Tentando CPU fallback...${NC}"
        $PYTHON_BIN -m pip install torch torchvision torchaudio --cache-dir pip-cache
    fi
    echo ""
    
    # Agora instala demais dependências
    echo -e "${YELLOW}[*] Instalando demais dependências...${NC}"
    $PYTHON_BIN -m pip install -r requirements.txt --cache-dir pip-cache
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERRO] Falha ao instalar dependências${NC}"
        exit 1
    fi
    
    touch venv/installed.txt
    echo -e "${GREEN}✓ Dependências instaladas${NC}\n"
else
    echo -e "${GREEN}✓ Dependências já instaladas${NC}\n"
    
    # Verifica se PyTorch com CUDA está instalado
    $PYTHON_BIN -c "import torch; cuda_status = 'CUDA' if torch.cuda.is_available() else 'CPU'; device_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'; print(f'PyTorch {torch.__version__} - Device: {device_name}')" 2>/dev/null
    
    echo ""
fi

# Download do modelo Whisper (com Python da venv)
echo -e "${YELLOW}🧠 Verificando modelo Whisper...${NC}"
$PYTHON_BIN -c "import whisper; whisper.load_model('base')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[*] Baixando modelo Whisper (isso pode levar alguns minutos)...${NC}"
    $PYTHON_BIN -c "import whisper; whisper.load_model('base')"
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}[AVISO] Falha ao baixar Whisper. Tente mais tarde.${NC}"
    fi
fi
echo -e "${GREEN}✓ Modelo Whisper pronto${NC}\n"

# Cria diretórios necessários
mkdir -p logs
mkdir -p database
mkdir -p audio_library/{memes,efeitos,notificacoes}

# Inicia a aplicação
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}[*] Iniciando aplicação...${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Acesse: http://localhost:5000${NC}"
echo ""
echo -e "${YELLOW}Abrindo navegador em 5 segundos...${NC}"
echo "Pressione Ctrl+C para parar"
echo ""

# Abre a URL no navegador padrão (com delay para o servidor iniciar)
sleep 3
if command -v xdg-open > /dev/null; then
    # Linux
    xdg-open http://localhost:5000 &
elif command -v open > /dev/null; then
    # macOS
    open http://localhost:5000 &
fi

# IMPORTANTE: Sempre usa Python da venv
$PYTHON_BIN main.py
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}[ERRO] Falha ao iniciar aplicação${NC}"
    exit 1
fi
