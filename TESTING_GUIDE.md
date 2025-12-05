# 🧪 Scripts de Teste Autônomo - Documentação

Esse projeto inclui uma suite completa de scripts para executar testes autônomos, com geração de relatórios detalhados.

---

## 📋 Scripts Disponíveis

### 1. **test_runner.py** - Executor Principal
Executa toda a suite de testes e gera relatórios JSON e HTML.

```bash
python test_runner.py
```

**O que faz:**
- ✅ Executa testes unitários (pytest)
- ✅ Executa testes de API
- ✅ Executa testes de integração
- ✅ Gera relatório JSON (`reports/test_results.json`)
- ✅ Gera relatório HTML (`reports/test_results.html`)

**Saída esperada:**
```
=======================
🧪 TEST RUNNER
=======================

[1/3] 🔬 Testes Unitários
✅ Unit Tests: 12/12 passed

[2/3] 🌐 Testes de API
✅ API Tests: 8/8 passed

[3/3] 🔗 Testes de Integração
✅ Integration Tests: 10/10 passed

====== RESUMO FINAL ======
✅ TODOS OS TESTES PASSARAM!
```

---

### 2. **test_backend.py** - Testes Específicos do Backend
Valida todos os módulos Python: analyzer, AI, audio, database.

```bash
python test_backend.py
```

**Testes inclusos:**
- ✅ Imports do Backend
- ✅ Core Analyzer
- ✅ Transcriber (Whisper)
- ✅ Keyword Detector
- ✅ Context Analyzer
- ✅ LLM Engine
- ✅ Database Manager
- ✅ Audio Utils
- ✅ Sound Player
- ✅ Config Manager

**Exemplo de saída:**
```
Testing: Imports do Backend... ✅ PASSED
Testing: Core Analyzer... ✅ PASSED
Testing: Transcriber (Whisper)... ✅ PASSED
Testing: LLM Engine... ✅ PASSED
...
Taxa de Sucesso: 100%
```

---

### 3. **test_frontend.sh** - Testes Específicos do Frontend
Valida TypeScript, build Next.js, linting e estrutura.

```bash
bash test_frontend.sh
```

**Testes inclusos:**
- ✅ Instalação de dependências
- ✅ Type checking (TypeScript)
- ✅ Linting (ESLint)
- ✅ Formatação (Prettier)
- ✅ Build de produção
- ✅ Validação de estrutura

**Arquivos verificados:**
```
✅ app/page.tsx
✅ components/dashboard.tsx
✅ components/keywords.tsx
✅ components/sound-library.tsx
✅ components/settings.tsx
✅ lib/api.ts
✅ package.json
```

---

### 4. **test_integration.py** - Testes de Integração End-to-End
Valida integração completa Backend + Frontend.

```bash
python test_integration.py
```

**Testes inclusos:**
- ✅ Backend Connectivity
- ✅ API Status Endpoint
- ✅ API Health Check
- ✅ Keywords CRUD (Create, Read, Update, Delete)
- ✅ Sounds Upload
- ✅ Config GET/POST
- ✅ Capture Start/Stop
- ✅ LLM Engine
- ✅ Database Persistence
- ✅ Error Handling

**Fluxo:**
```
1. Inicia backend em http://localhost:5000
2. Aguarda servidor ficar pronto
3. Executa testes de API
4. Valida CRUD de keywords
5. Testa upload de sons
6. Para o servidor
```

---

### 5. **run_all_tests.sh** - Master Test Runner (Linux/Mac)
Executa TODOS os testes de forma sequencial.

```bash
bash run_all_tests.sh
# ou
./run_all_tests.sh
```

**Sequência:**
```
[1/4] Backend Tests (Python)
[2/4] Frontend Tests (TypeScript/Next.js)
[3/4] Unit Tests (pytest)
[4/4] Integration Tests (E2E)
```

**Gera:**
- ✅ Relatório JSON
- ✅ Relatório HTML
- ✅ Resumo final

---

### 6. **run_all_tests.bat** - Master Test Runner (Windows)
Equivalente do run_all_tests.sh para Windows.

```cmd
run_all_tests.bat
```

**Funcionalidade idêntica ao bash:**
- Mesmos testes
- Mesma sequência
- Mesmo relatório

---

## 🚀 Como Usar

### Opção 1: Executar Tudo (Recomendado)
```bash
# Linux/Mac
./run_all_tests.sh

# Windows
run_all_tests.bat
```

### Opção 2: Testes Específicos
```bash
# Apenas Backend
python test_backend.py

# Apenas Frontend
bash test_frontend.sh

# Apenas Integração
python test_integration.py

# Gerenciador de testes
python test_runner.py
```

### Opção 3: Com pytest diretamente
```bash
# Todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/test_api.py -v

# Com coverage
pytest tests/ --cov=. --cov-report=html
```

---

## 📊 Relatórios

Os scripts geram dois tipos de relatórios em `reports/`:

### JSON Report (`test_results.json`)
Dados estruturados para análise programática:

```json
{
  "timestamp": "2025-12-04T15:30:00",
  "duration": 125.45,
  "suites": [
    {
      "name": "Unit Tests",
      "total": 12,
      "passed": 12,
      "failed": 0,
      "success_rate": 100.0,
      "tests": [
        {
          "test_name": "test_imports",
          "status": "PASS",
          "duration": 0.5,
          "timestamp": "2025-12-04T15:30:01"
        }
      ]
    }
  ]
}
```

### HTML Report (`test_results.html`)
Visualização bonita com:
- ✅ Resumo geral
- ✅ Detalhes por suite
- ✅ Status de cada teste
- ✅ Taxa de sucesso
- ✅ Timestamp

**Abrir no navegador:**
```bash
# Linux/Mac
open reports/test_results.html

# Windows
start reports\test_results.html

# Qualquer sistema
python -m http.server 8000 --directory reports
# Acessar: http://localhost:8000/test_results.html
```

---

## 🔧 Configuração

### Variáveis de Ambiente
Você pode customizar os testes com variáveis:

```bash
# Backend URL (padrão: http://localhost:5000)
export BACKEND_URL=http://localhost:5000

# Frontend URL (padrão: http://localhost:3000)
export FRONTEND_URL=http://localhost:3000

# Timeout da API (padrão: 5 segundos)
export API_TIMEOUT=10
```

### pytest.ini
Arquivo de configuração pytest já incluído:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

---

## 📈 Métricas de Sucesso

Cada suite busca 100% de sucesso:

```
Backend:        ✅ 10/10 testes
Frontend:       ✅ 6/6 testes
Integration:    ✅ 10/10 testes
Unit (pytest):  ✅ 12/12+ testes
---
TOTAL:          ✅ 100% taxa de sucesso
```

---

## ⚠️ Troubleshooting

### Problema: "Python não encontrado"
```bash
# Certifique-se de ter Python 3.8+ instalado
python3 --version

# No Windows, use 'python' em vez de 'python3'
python --version
```

### Problema: "ModuleNotFoundError: No module named 'pytest'"
```bash
# Instale pytest
pip install pytest requests

# Ou use o requirements.txt
pip install -r requirements.txt
```

### Problema: "Address already in use (port 5000)"
```bash
# Feche o servidor que está usando a porta 5000
# Ou modifique BACKEND_URL em test_integration.py

# Linux/Mac - encontrar processo
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Problema: "Frontend tests falhando"
```bash
# Verifique se você está no diretório correto
cd web-control

# Instale dependências
npm install

# Limpe node_modules e reinstale
rm -rf node_modules pnpm-lock.yaml
npm install
```

### Problema: "Integration tests timeout"
```bash
# Aumentar timeout em test_integration.py:
# Mude API_TIMEOUT = 5 para API_TIMEOUT = 10

# Ou inicie o backend manualmente em outro terminal:
python main.py

# Depois rode os testes
python test_integration.py
```

---

## 🔍 CI/CD Integration

### GitHub Actions
Exemplo de workflow para executar testes automaticamente:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest requests
      
      - name: Run all tests
        run: bash run_all_tests.sh
      
      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: test-reports
          path: reports/
```

### GitLab CI
```yaml
test:
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - bash run_all_tests.sh
  artifacts:
    paths:
      - reports/
    when: always
```

---

## 📝 Próximos Passos

Sugestões para expandir os testes:

1. **Cobertura de Código**
   ```bash
   pytest tests/ --cov=. --cov-report=html
   ```

2. **Testes de Performance**
   ```bash
   pytest tests/ -v --durations=10
   ```

3. **Testes de Segurança**
   ```bash
   pip install bandit
   bandit -r . -ll
   ```

4. **Testes de Acessibilidade (Frontend)**
   ```bash
   npm install --save-dev @axe-core/react
   ```

5. **Load Testing**
   ```bash
   pip install locust
   locust -f locustfile.py
   ```

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs: `logs/app.log`
2. Veja o relatório HTML: `reports/test_results.html`
3. Rode com verbose: `python test_runner.py`
4. Abra uma issue no GitHub

---

**Última atualização:** 4 de dezembro de 2025  
**Versão:** 1.0  
**Status:** ✅ Produção
