## 🧠 LLM Engine - Quick Start

### O que foi implementado

**Novo motor de IA com suporte a Phi-2 via:**
- Transformers (local, recomendado)
- Ollama (opcional, mais rápido se já tiver)

### Instalação

```bash
# Já incluído no requirements.txt
pip install -r requirements.txt
```

Se tiver Ollama:
```bash
ollama pull phi
ollama serve  # em outra terminal
```

### Uso via API

```bash
# Status do LLM
curl http://localhost:5000/api/llm/status

# Gerar texto
curl -X POST http://localhost:5000/api/llm/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Olá, como", "max_tokens":50}'

# Analisar contexto
curl -X POST http://localhost:5000/api/llm/analyze-context \
  -H "Content-Type: application/json" \
  -d '{
    "text":"Que suspeito",
    "context_keywords":["fake","mente","não acredito"]
  }'

# Limpar cache
curl -X POST http://localhost:5000/api/llm/cache/clear
```

### Uso em Python

```python
from ai.llm_engine import LLMEngine

engine = LLMEngine()

# Gerar
response = engine.generate("Olá, como", max_tokens=50)

# Analisar contexto
result = engine.analyze_context(
    "Que suspeito",
    ["fake", "mente", "não acredito"]
)
print(result)  # {"relevant": True/False, "confidence": 0.0-1.0}

# Status
print(engine.get_status())
```

### Backend Strategy

Automaticamente usa (em ordem):
1. **Ollama** se estiver rodando
2. **Transformers** (Phi-2) se disponível
3. **Fallback** para sentence-transformers (degradado)

### Arquivos criados/modificados

- ✅ `ai/llm_engine.py` - Motor LLM
- ✅ `tests/test_llm_engine.py` - Testes
- ✅ `core/analyzer.py` - Integrado LLMEngine
- ✅ `web/api_routes.py` - Endpoints REST
- ✅ `requirements.txt` - Deps atualizadas
