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
    exit 1
fi

echo -e "${GREEN}✓ Python encontrado: $(python3 --version)${NC}\n"

# Verifica/cria ambiente virtual
if [ ! -d "venv" ]; then
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
echo -e "${GREEN}✓ Ambiente virtual ativado${NC}\n"

# Instala dependências
if [ ! -f "venv/installed.txt" ]; then
    echo -e "${YELLOW}📥 Instalando dependências (primeira execução)...${NC}"
    echo "Isso pode levar alguns minutos..."
    echo ""
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERRO] Falha ao instalar dependências${NC}"
        exit 1
    fi
    touch venv/installed.txt
    echo -e "${GREEN}✓ Dependências instaladas${NC}\n"
else
    echo -e "${GREEN}✓ Dependências já instaladas${NC}\n"
fi

# Download do modelo Whisper
echo -e "${YELLOW}🧠 Verificando modelo Whisper...${NC}"
python3 -c "import whisper; whisper.load_model('base')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[*] Baixando modelo Whisper (isso pode levar alguns minutos)...${NC}"
    python3 -c "import whisper; whisper.load_model('base')"
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

python3 main.py
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}[ERRO] Falha ao iniciar aplicação${NC}"
    exit 1
fi
