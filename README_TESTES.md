# 🧪 Scripts de Teste Autônomo - Início Rápido

## ⚡ Comece Aqui

Para executar **TODOS** os testes de uma vez:

### Linux/Mac:
```bash
./run_all_tests.sh
```

### Windows:
```cmd
run_all_tests.bat
```

---

## 📋 Scripts Individuais

| Script | Propósito | Comando |
|--------|-----------|---------|
| **test_runner.py** | Orquestrador principal | `python test_runner.py` |
| **test_backend.py** | Valida módulos Python | `python test_backend.py` |
| **test_frontend.sh** | Valida TypeScript/Next.js | `bash test_frontend.sh` |
| **test_integration.py** | Testa Backend + Frontend | `python test_integration.py` |
| **run_all_tests.sh** | Executa tudo (Linux/Mac) | `./run_all_tests.sh` |
| **run_all_tests.bat** | Executa tudo (Windows) | `run_all_tests.bat` |

---

## 🎯 O Que Cada Teste Valida

### Backend Tests (10 verificações)
```
✅ Imports de todos os módulos
✅ MicrophoneAnalyzer inicialização
✅ Transcriber (Whisper)
✅ KeywordDetector
✅ ContextAnalyzer
✅ LLMEngine
✅ DatabaseManager
✅ AudioUtils
✅ SoundPlayer
✅ ConfigManager
```

### Frontend Tests (6 verificações)
```
✅ Dependências npm
✅ Type checking (TypeScript)
✅ ESLint
✅ Prettier formatting
✅ Next.js build
✅ Estrutura de arquivos
```

### Integration Tests (10 verificações)
```
✅ Backend connectivity
✅ API /status endpoint
✅ Health check
✅ Keywords CRUD
✅ Sounds upload
✅ Config GET/POST
✅ Capture control
✅ LLM Engine
✅ Database persistence
✅ Error handling
```

---

## 📊 Relatórios Gerados

Após os testes, dois arquivos são criados em `reports/`:

1. **test_results.json** - Dados estruturados
2. **test_results.html** - Visualização no navegador

Abrir:
```bash
# Linux/Mac
open reports/test_results.html

# Windows
start reports\test_results.html

# Qualquer sistema
python -m http.server 8000 --directory reports
```

---

## 🔧 Setup Rápido

### 1️⃣ Primeira Execução
```bash
# Linux/Mac
./run_all_tests.sh

# Windows - Use prompt com privilégios de admin
run_all_tests.bat
```

### 2️⃣ Problemas Comuns

**"Python não encontrado"**
```bash
# Instale Python 3.8+
python3 --version  # ou 'python' no Windows
```

**"pytest não encontrado"**
```bash
pip install pytest requests
```

**"Port 5000 já está em uso"**
```bash
# Feche o aplicativo na porta 5000
# Ou rode manualmente antes dos testes:
python main.py  # em outro terminal
```

---

## 🚀 Uso Avançado

### Rodar Testes Específicos
```bash
# Apenas Backend
python test_backend.py

# Apenas Frontend
bash test_frontend.sh

# Apenas Integração
python test_integration.py
```

### Com pytest diretamente
```bash
# Todos os testes
pytest tests/ -v

# Teste específico
pytest tests/test_api.py::test_status -v

# Com coverage
pytest tests/ --cov=. --cov-report=html
```

### Modo Verbose
```bash
# Ver detalhes de cada teste
python test_runner.py

# Com output completo
pytest tests/ -v --tb=long
```

---

## 📈 Exemplo de Saída

```
==================================================
🧪 MASTER TEST RUNNER - Analisador de Microfone
==================================================

[1/4] Backend Tests (Python)
---------------------------------
Testing: Imports do Backend... ✅ PASSED
Testing: Core Analyzer... ✅ PASSED
Testing: LLM Engine... ✅ PASSED
... (10 testes)
Taxa de Sucesso: 100%

[2/4] Frontend Tests (TypeScript/Next.js)
---------------------------------
Testing: npm install... ✅ PASSED
Testing: TypeScript compilation... ✅ PASSED
Testing: Next.js build... ✅ PASSED
... (6 testes)
Taxa de Sucesso: 100%

[3/4] Unit Tests (pytest)
---------------------------------
test_api.py::test_status PASSED
test_ai.py::test_keyword_detection PASSED
... (12+ testes)
Taxa de Sucesso: 100%

[4/4] Integration Tests (E2E)
---------------------------------
Testing: Backend Connectivity... ✅ PASSED
Testing: Keywords CRUD... ✅ PASSED
Testing: Capture Control... ✅ PASSED
... (10 testes)
Taxa de Sucesso: 100%

[Relatórios] Gerando relatórios...
Relatórios gerados em:
   - reports\test_results.json
   - reports\test_results.html

==================================================
📊 RESUMO FINAL
==================================================

Suites de Testes Executadas: 4
✅ Passaram: 4
❌ Falharam: 0

✅ TODOS OS TESTES PASSARAM!
```

---

## 🔍 Checklist de Pré-Teste

Antes de rodar os testes, verifique:

- [ ] Python 3.8+ instalado
- [ ] `pip install -r requirements.txt` executado
- [ ] Node.js/npm instalado (para testes frontend)
- [ ] Porta 5000 disponível (backend)
- [ ] Porta 3000 disponível (frontend)
- [ ] Microfone conectado (para testes de áudio)

---

## 📚 Documentação Completa

Para mais detalhes, veja: **TESTING_GUIDE.md**

Topics:
- ✅ Descrição detalhada de cada script
- ✅ Troubleshooting
- ✅ CI/CD integration (GitHub Actions, GitLab CI)
- ✅ Extensão dos testes
- ✅ Análise de cobertura

---

## 💡 Dicas

1. **Primeira vez?** Use `./run_all_tests.sh`
2. **Teste rápido?** Use `python test_backend.py`
3. **Editar código?** Use `pytest tests/ -v --watch`
4. **Integração contínua?** Copie workflow do TESTING_GUIDE.md

---

## 🎉 Resultado Esperado

```
✅ TODOS OS TESTES PASSARAM!
```

Taxa de sucesso: **100%**  
Tempo total: **~2-5 minutos**

---

**Pronto para testar? Execute agora:**

```bash
# Linux/Mac
./run_all_tests.sh

# Windows
run_all_tests.bat
```

Veja os resultados em: `reports/test_results.html` 🎯

---

*Última atualização: 4 de dezembro de 2025*
