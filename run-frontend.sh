#!/bin/bash
# Frontend only - Analisador de Microfone com IA

set -e

echo "🎨 Analisador de Microfone - FRONTEND"
echo "======================================"
echo ""

# ============ COMANDO STOP ============
if [ "$1" = "stop" ]; then
    echo "🛑 Parando Frontend..."
    pkill -9 -f "npm run dev" 2>/dev/null || true
    pkill -9 -f "node.*next" 2>/dev/null || true
    pkill -9 -f "next.*dev" 2>/dev/null || true
    sleep 1

    # Remover lock dev do next caso exista (stale lock)
    LOCK_FILE="web-control/.next/dev/lock"
    if [ -f "$LOCK_FILE" ]; then
        echo "⚠️  Lock do Next.js encontrado ($LOCK_FILE). Removendo..."
        rm -f "$LOCK_FILE" 2>/dev/null || true
        echo "✓ Lock removido"
    fi

    echo "✅ Frontend parado"
    exit 0
fi

# ============ COMANDO CLEAN ============
if [ "$1" = "clean" ]; then
    echo "🧹 Limpando Frontend..."
    bash "$0" stop 2>/dev/null || true
    echo "🔎 Removendo cache .next e cache do node_modules (se existirem)..."
    rm -rf web-control/.next web-control/node_modules/.cache 2>/dev/null || true
    # Garantir remoção do lock
    LOCK_FILE="web-control/.next/dev/lock"
    if [ -f "$LOCK_FILE" ]; then
        echo "⚠️  Lock do Next.js ainda existia ($LOCK_FILE). Removendo..."
        rm -f "$LOCK_FILE" 2>/dev/null || true
        echo "✓ Lock removido"
    fi

    echo "✅ Limpeza concluída"
    exit 0
fi

# ============ SETUP ============

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║ FRONTEND - Verificando Dependências                           ║"
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

echo "════════════════════════════════════════════════════════════════"
echo "✅ SETUP FRONTEND COMPLETO!"
echo "════════════════════════════════════════════════════════════════"
echo ""

# ============ INICIAR FRONTEND ============

echo "🚀 Iniciando Frontend (Next.js)..."

# Verificar e remover lock stale do next antes de iniciar
LOCK_FILE="web-control/.next/dev/lock"
if [ -f "$LOCK_FILE" ]; then
    echo "⚠️  Encontrado arquivo de lock: $LOCK_FILE"
    # Se houver um processo next/npm rodando que possivelmente esteja usando este lock, informa ao usuário
    if pgrep -f "npm run dev" > /dev/null 2>&1 || pgrep -f "next.*dev" > /dev/null 2>&1; then
        echo "ℹ️  Parece que outra instância do next dev está rodando. Pare-a antes de iniciar este script."
        echo "   Para forçar a remoção do lock use: bash run-frontend.sh stop  (ou clean)"
        echo ""
    else
        echo "🧹 Nenhuma instância detectada — removendo lock stale e prosseguindo..."
        rm -f "$LOCK_FILE" 2>/dev/null || true
    fi
fi

cd web-control
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "⏳ Aguardando Frontend..."
FRONTEND_READY=0
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1 || curl -s http://localhost:3001 > /dev/null 2>&1; then
        FRONTEND_URL=$(curl -s http://localhost:3000 > /dev/null 2>&1 && echo "http://localhost:3000" || echo "http://localhost:3001")
        echo "✅ Frontend pronto em $FRONTEND_URL"
        FRONTEND_READY=1
        break
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend parou!"
        echo "Verifique logs:"
        tail -30 /tmp/frontend.log
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
echo "✅ FRONTEND RODANDO!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Frontend (Next.js): http://localhost:3000 (ou 3001)"
echo ""
echo "PID: $FRONTEND_PID"
echo ""
echo "💡 Dicas:"
echo "  - Para parar:    bash run-frontend.sh stop"
echo "  - Para logs:     tail -f /tmp/frontend.log"
echo "  - Para limpar:   bash run-frontend.sh clean"
echo ""

# Abrir navegador
if command -v xdg-open > /dev/null 2>&1; then
    xdg-open "http://localhost:3000" > /dev/null 2>&1 &
elif command -v open > /dev/null 2>&1; then
    open "http://localhost:3000" > /dev/null 2>&1 &
fi

# Limpeza ao sair
cleanup() {
    echo ""
    echo ""
    echo "🛑 Parando Frontend..."
    kill $FRONTEND_PID 2>/dev/null || true
    sleep 1
    echo "✅ Frontend parado"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "Executando em FOREGROUND (pressione Ctrl+C para parar)"
echo ""

while true; do
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "⚠️  Frontend morreu!"
        tail -20 /tmp/frontend.log
        break
    fi
    sleep 2
done
