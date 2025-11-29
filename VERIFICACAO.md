# ✅ Checklist de Verificação

Guia para verificar se tudo está funcionando corretamente.

## 🔍 Verificação Rápida (5 minutos)

### 1. Verificar Instalação

```bash
# Python correto?
python --version
# Deve ser 3.8 ou superior

# Ambiente virtual ativado?
pip --version | grep venv
# Deve mostrar caminho do venv

# Dependências instaladas?
pip list | grep -E "flask|whisper|pyaudio"
# Deve mostrar os pacotes
```

### 2. Verificar Estrutura

```bash
# Arquivos principais existem?
test -f main.py && echo "✓ main.py"
test -f requirements.txt && echo "✓ requirements.txt"
test -f config_default.json && echo "✓ config_default.json"
test -d core && echo "✓ core/"
test -d web && echo "✓ web/"
test -d audio && echo "✓ audio/"
test -d ai && echo "✓ ai/"
```

### 3. Sintaxe Python

```bash
# Verificar erros de sintaxe
python -m py_compile main.py
python -m py_compile core/*.py
python -m py_compile audio/*.py
python -m py_compile ai/*.py
python -m py_compile web/*.py
python -m py_compile sound/*.py
python -m py_compile utils/*.py
```

### 4. Importações

```bash
# Testar importações principais
python -c "from core.config_manager import ConfigManager; print('✓ ConfigManager')"
python -c "from audio.processor import AudioProcessor; print('✓ AudioProcessor')"
python -c "from audio.transcriber import Transcriber; print('✓ Transcriber')"
python -c "from ai.keyword_detector import KeywordDetector; print('✓ KeywordDetector')"
python -c "from ai.context_analyzer import ContextAnalyzer; print('✓ ContextAnalyzer')"
python -c "from web.app import create_app; print('✓ Flask App')"
```

## 🎙️ Verificação de Áudio (2 minutos)

```bash
# Listar dispositivos de áudio
python -c "
from audio.processor import AudioProcessor
import json
devices = AudioProcessor.list_devices()
print(json.dumps(devices[:3], indent=2))
"
# Deve listar seus dispositivos de áudio
```

## 🧠 Verificação de IA (2 minutos)

```bash
# Teste KeywordDetector
python -c "
from ai.keyword_detector import KeywordDetector
detector = KeywordDetector()
detector.keywords = [{
    'id': 'test',
    'pattern': 'hello',
    'enabled': True,
    'weight': 1.0,
    'variations': [],
    'fuzzy_threshold': 0.8
}]
result = detector.detect('hello world')
print('✓ KeywordDetector funcionando' if result else '✗ Falhou')
"

# Teste ContextAnalyzer
python -c "
from ai.context_analyzer import ContextAnalyzer
analyzer = ContextAnalyzer()
print('✓ ContextAnalyzer inicializado')
# Cache inicializado?
print(f'✓ Cache tamanho: {analyzer.cache.max_size}')
"
```

## 🌐 Verificação de Web (1 minuto)

```bash
# Testar criação da app Flask
python -c "
from web.app import create_app
app = create_app()
with app.test_client() as client:
    response = client.get('/health')
    print(f'✓ Health check: {response.status_code}')
"
```

## 📚 Verificação de Documentação (1 minuto)

```bash
# Arquivos de documentação existem?
test -f README.md && echo "✓ README.md"
test -f DOCUMENTACAO_COMPLETA.md && echo "✓ DOCUMENTACAO_COMPLETA.md"
test -f QUICK_START.md && echo "✓ QUICK_START.md"
test -f EXEMPLOS_USO.md && echo "✓ EXEMPLOS_USO.md"
test -f TROUBLESHOOTING.md && echo "✓ TROUBLESHOOTING.md"
test -f CONTRIBUTING.md && echo "✓ CONTRIBUTING.md"
test -f STATUS.md && echo "✓ STATUS.md"
```

## 🧪 Rodar Testes (3 minutos)

```bash
# Rodar todos os testes
pytest tests/ -v

# Rodar específicos
pytest tests/test_audio.py -v
pytest tests/test_ai.py -v

# Com cobertura
pytest --cov=core --cov=audio --cov=ai
```

## 🚀 Teste de Execução (2 minutos)

```bash
# Iniciar aplicação (Ctrl+C para parar após iniciar)
python main.py

# Esperado:
# - Mensagem de inicialização
# - "Running on http://127.0.0.1:5000"
# - Sem erros críticos
```

## 🌐 Verificação da Interface Web

Após iniciar `python main.py`:

1. **Abrir navegador**: http://localhost:5000
2. **Verificar elementos**:
   - [ ] Navbar aparece
   - [ ] Sidebar com menu (Dashboard, Palavras-Chave, etc.)
   - [ ] Tema dark/light toggle funciona
   - [ ] Botão "Iniciar Captura" está visível
   - [ ] Tabelas respondem

3. **Testar navegação**:
   - [ ] Clique em cada aba (Dashboard, Keywords, etc.)
   - [ ] Conteúdo carrega
   - [ ] Tema muda ao clicar no toggle

4. **Verificar WebSocket**:
   - [ ] Abrir DevTools (F12)
   - [ ] Ir para Console
   - [ ] Procurar "Connected" (sem erros de conexão)

## 📊 Script de Verificação Completa

```bash
#!/bin/bash
# verify_setup.sh

echo "🔍 Analisador de Microfone - Verificação de Setup"
echo "=================================================="
echo ""

checks_passed=0
checks_failed=0

check() {
    if eval "$1" > /dev/null 2>&1; then
        echo "✓ $2"
        ((checks_passed++))
    else
        echo "✗ $2"
        ((checks_failed++))
    fi
}

# Verificações
check "python --version" "Python instalado"
check "test -f main.py" "main.py existe"
check "test -d core" "Diretório core existe"
check "test -d web" "Diretório web existe"
check "python -c 'import flask'" "Flask instalado"
check "python -c 'import whisper'" "Whisper instalado"
check "python -c 'import pyaudio'" "PyAudio instalado"
check "test -f requirements.txt" "requirements.txt existe"
check "test -f config_default.json" "config_default.json existe"

echo ""
echo "=================================================="
echo "Resultado: $checks_passed passados, $checks_failed falhados"

if [ $checks_failed -eq 0 ]; then
    echo "✅ Setup verificado com sucesso!"
    exit 0
else
    echo "⚠️ Alguns testes falharam. Veja acima."
    exit 1
fi
```

## 🔐 Verificação de Segurança

```bash
# Nenhuma senha em código?
grep -r "password" . --include="*.py" --exclude-dir=venv
# Não deve retornar valores sensíveis

# Nenhuma chave API exposta?
grep -r "api_key\|secret" . --include="*.py" --exclude-dir=venv
# Deve estar em .env ou variáveis de ambiente

# .env não está versionado?
test ! -f .env && echo "✓ .env não presente (bom)"
grep "\.env$" .gitignore && echo "✓ .env em .gitignore"
```

## 📈 Performance

```bash
# Verificar tempos de importação
python -m cProfile -s cumulative main.py --help 2>&1 | head -20

# Consumo de memória
python -c "
import tracemalloc
tracemalloc.start()
from core.analyzer import MicrophoneAnalyzer
from core.config_manager import ConfigManager
current, peak = tracemalloc.get_traced_memory()
print(f'Memória atual: {current / 1024 / 1024:.1f} MB')
print(f'Pico: {peak / 1024 / 1024:.1f} MB')
"
```

## 📋 Checklist Final

Antes de colocar em produção:

- [ ] Todos os arquivos Python compilam (`python -m py_compile`)
- [ ] Todos os imports funcionam
- [ ] Testes passam (`pytest tests/`)
- [ ] Documentação está completa
- [ ] Interface web carrega
- [ ] Microfone é detectado
- [ ] Nenhuma senha em código
- [ ] `.gitignore` está configurado
- [ ] `requirements.txt` atualizado
- [ ] Logs funcionam
- [ ] Database inicializa
- [ ] WebSocket conecta

## 🆘 Se algo falhar

1. **Veja mensagem de erro** (copie completa)
2. **Verifique logs**: `logs/app.log`
3. **Consulte**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. **Abra issue** com:
   - Comando que falhou
   - Erro completo
   - Seu ambiente (SO, Python version)

---

**Sucesso! ✅** Seu ambiente está pronto para usar o Analisador de Microfone com IA.
