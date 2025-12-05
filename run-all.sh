#!/bin/bash
# Universal - Roda Backend + Frontend separados

echo "🎙️ Analisador de Microfone - MODO UNIVERSAL"
echo "=============================================="
echo ""
echo "Este script roda Backend e Frontend em processos separados"
echo ""

# ============ COMANDO STOP ============
if [ "$1" = "stop" ] || [ "$1" = "stop-all" ]; then
    echo "🛑 Parando todos os serviços..."
    echo ""
    bash run-backend.sh stop 2>/dev/null || true
    bash run-frontend.sh stop 2>/dev/null || true
    sleep 1
    echo "✅ Todos os serviços parados"
    exit 0
fi

# ============ COMANDO CLEAN ============
if [ "$1" = "clean" ] || [ "$1" = "clean-all" ]; then
    echo "🧹 Limpando tudo..."
    echo ""
    bash run-backend.sh stop 2>/dev/null || true
    bash run-frontend.sh clean 2>/dev/null || true
    sleep 1
    echo "✅ Limpeza concluída"
    exit 0
fi

# ============ MODO HELP ============
if [ "$1" = "help" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    cat << 'EOF'
Analisador de Microfone - Scripts Separados

USO:
  # Rodar backend:
  bash run-backend.sh

  # Rodar frontend:
  bash run-frontend.sh

  # Rodar ambos (em terminal diferente para cada):
  Terminal 1: bash run-backend.sh
  Terminal 2: bash run-frontend.sh

  # Parar backend:
  bash run-backend.sh stop

  # Parar frontend:
  bash run-frontend.sh stop

  # Parar todos:
  bash run-all.sh stop

  # Limpar frontend:
  bash run-frontend.sh clean

  # Limpar tudo:
  bash run-all.sh clean

URLs:
  Backend API:  http://localhost:5000/api
  Backend Docs: http://localhost:5000/docs
  Frontend:     http://localhost:3000

Logs:
  Backend: tail -f /tmp/backend.log
  Frontend: tail -f /tmp/frontend.log

VANTAGENS:
  ✓ Backend e Frontend totalmente independentes
  ✓ Pode reiniciar um sem afetar o outro
  ✓ Fácil debugar cada parte separadamente
  ✓ Cada um com seu processo e logs
  ✓ Você controla quando rodar cada um
EOF
    exit 0
fi

# ============ MODO AUTOMÁTICO (AMBOS) ============

echo "⚠️  MODO AUTOMÁTICO - Rodando Backend + Frontend"
echo ""
echo "📝 Abra dois terminais diferentes e execute:"
echo ""
echo "   Terminal 1 (Backend):"
echo "   $ bash run-backend.sh"
echo ""
echo "   Terminal 2 (Frontend):"
echo "   $ bash run-frontend.sh"
echo ""
echo "OU para ver este menu:"
echo "   $ bash run-all.sh help"
echo ""
echo "Para parar todos os serviços:"
echo "   $ bash run-all.sh stop"
echo ""

exit 0
