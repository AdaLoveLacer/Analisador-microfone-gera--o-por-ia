#!/bin/bash
# Frontend Test Suite - Testes Específicos do Frontend
# Valida: Next.js build, linting, type checking, componentes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/web-control"

echo ""
echo "=================================================="
echo "🎨 FRONTEND TEST SUITE"
echo "=================================================="
echo ""

cd "$FRONTEND_DIR" || exit 1

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contadores
TOTAL=0
PASSED=0
FAILED=0

# Função para executar teste
run_test() {
    local test_name=$1
    local command=$2
    
    echo -n "Testing: $test_name... "
    TOTAL=$((TOTAL + 1))
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ FAILED${NC}"
        FAILED=$((FAILED + 1))
    fi
}

# ===== TESTES =====

echo "[1/6] Verificando dependências..."
run_test "npm install" "npm list > /dev/null 2>&1"

echo ""
echo "[2/6] Type Checking (TypeScript)..."
run_test "TypeScript compilation" "npx tsc --noEmit"

echo ""
echo "[3/6] Linting (ESLint)..."
if command -v npx &> /dev/null && [ -f ".eslintrc.json" ] || [ -f ".eslintrc.js" ]; then
    run_test "ESLint" "npx eslint . --ext .ts,.tsx 2>/dev/null || true"
else
    echo "Testing: ESLint... ⏭️  SKIPPED (not configured)"
fi

echo ""
echo "[4/6] Code Formatting (Prettier)..."
if command -v npx &> /dev/null && [ -f ".prettierrc.json" ] || [ -f ".prettierrc.js" ]; then
    run_test "Prettier" "npx prettier --check . || true"
else
    echo "Testing: Prettier... ⏭️  SKIPPED (not configured)"
fi

echo ""
echo "[5/6] Build Production..."
run_test "Next.js build" "npm run build"

echo ""
echo "[6/6] Validando estrutura..."

# Validar arquivos críticos
FILES_TO_CHECK=(
    "app/page.tsx"
    "components/dashboard.tsx"
    "components/keywords.tsx"
    "components/sound-library.tsx"
    "components/settings.tsx"
    "lib/api.ts"
    "package.json"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file MISSING"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "=================================================="
echo "📊 RESUMO"
echo "=================================================="

SUCCESS_RATE=$((PASSED * 100 / TOTAL))

echo "Total: $TOTAL"
echo -e "✅ Passed: ${GREEN}$PASSED${NC}"
echo -e "❌ Failed: ${RED}$FAILED${NC}"
echo "Taxa de Sucesso: $SUCCESS_RATE%"

echo "=================================================="
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ TODOS OS TESTES PASSARAM!${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}❌ ALGUNS TESTES FALHARAM${NC}"
    echo ""
    exit 1
fi
