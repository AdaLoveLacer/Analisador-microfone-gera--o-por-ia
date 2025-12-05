#!/bin/bash
# Master Test Runner - Executa toda a suite de testes de forma autônoma
# Suporta: Backend tests, Frontend tests, Integration tests, Relatórios

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções
print_header() {
    echo ""
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${YELLOW}[$1]${NC} $2"
    echo "-" 
}

# ========== SETUP ==========

print_header "🧪 MASTER TEST RUNNER - Analisador de Microfone com IA"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado${NC}"
    exit 1
fi

# Verificar venv
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Criando ambiente virtual...${NC}"
    python3 -m venv venv
fi

# Ativar venv
source venv/bin/activate

# Instalar pytest se necessário
pip install pytest requests -q 2>/dev/null || true

# ========== TESTES ==========

TESTS_PASSED=0
TESTS_FAILED=0

# 1. Backend Tests
print_section "1/4" "Backend Tests (Python)"

if python test_backend.py; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# 2. Frontend Tests
print_section "2/4" "Frontend Tests (TypeScript/Next.js)"

if [ -f "test_frontend.sh" ]; then
    if bash test_frontend.sh; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
else
    echo -e "${YELLOW}⏭️  SKIPPED (test_frontend.sh não encontrado)${NC}"
fi

# 3. Unit Tests (pytest)
print_section "3/4" "Unit Tests (pytest)"

if python -m pytest tests/ -v --tb=short 2>/dev/null; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${YELLOW}⏭️  Unit tests exited with errors${NC}"
fi

# 4. Integration Tests
print_section "4/4" "Integration Tests (E2E)"

if python test_integration.py; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# ========== RELATÓRIOS ==========

print_section "Relatórios" "Gerando relatórios..."

# Executar test_runner.py para gerar relatórios completos
python test_runner.py || true

if [ -d "reports" ]; then
    echo -e "${GREEN}✓ Relatórios gerados:${NC}"
    [ -f "reports/test_results.json" ] && echo "  - reports/test_results.json"
    [ -f "reports/test_results.html" ] && echo "  - reports/test_results.html"
fi

# ========== RESUMO FINAL ==========

print_header "📊 RESUMO FINAL"

TOTAL_SUITES=$((TESTS_PASSED + TESTS_FAILED))

echo "Suites de Testes Executadas: $TOTAL_SUITES"
echo -e "${GREEN}✅ Passaram: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Falharam: $TESTS_FAILED${NC}"

echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ TODOS OS TESTES PASSARAM!${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}❌ ALGUNS TESTES FALHARAM${NC}"
    echo ""
    echo "Para mais detalhes, veja:"
    echo "  - reports/test_results.html (relatório visual)"
    echo "  - reports/test_results.json (dados estruturados)"
    echo ""
    exit 1
fi
