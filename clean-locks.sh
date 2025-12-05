#!/bin/bash
# Script para limpar locks do Next.js e processos presos

echo "🧹 Limpando locks e processos..."

# Remover lock
LOCK_FILE="web-control/.next/dev/lock"
if [ -f "$LOCK_FILE" ]; then
    echo "❌ Encontrado: $LOCK_FILE"
    rm -f "$LOCK_FILE"
    echo "✅ Lock removido"
fi

# Remover diretório de lock
LOCK_DIR="web-control/.next/dev"
if [ -d "$LOCK_DIR" ]; then
    echo "🗑️  Limpando diretório: $LOCK_DIR"
    rm -rf "$LOCK_DIR"
    mkdir -p "$LOCK_DIR"
    echo "✅ Diretório recriado vazio"
fi

# Matar processos node/npm
echo "🔍 Matando processos node/npm..."
pkill -9 -f "npm run dev" 2>/dev/null || true
pkill -9 -f "next.*dev" 2>/dev/null || true
pkill -9 -f "node" 2>/dev/null || true
sleep 1

echo "✅ Limpeza completa!"
echo ""
echo "Você pode agora rodar:"
echo "  bash run-frontend.sh"
echo "  ou"
echo "  bash run.sh"
