# 🚀 Guia de Instalação - CUDA 11.8 e Cache Local

## Resumo

Este projeto foi configurado para usar:
- **PyTorch com CUDA 11.8** (GPU acceleration)
- **Cache local do pip** dentro do projeto (`pip-cache/`)
- **Python da venv SEMPRE** (nunca Python global)

---

## ⚙️ Instalação Automática

Execute o script de inicialização:

### Windows
```bash
run.bat
```

### Linux/Mac
```bash
./run.sh
```

O script vai:
1. ✅ Criar/ativar venv
2. ✅ Instalar PyTorch com CUDA 11.8 (com cache local)
3. ✅ Instalar outras dependências
4. ✅ Iniciar a aplicação

---

## 📦 Instalação Manual (se necessário)

### 1. Criar ambiente virtual
```bash
python -m venv venv
```

### 2. Ativar venv

**Windows:**
```bash
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar PyTorch com CUDA 11.8

**COM cache local:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --cache-dir pip-cache
```

**SEM cache local:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 4. Instalar demais dependências

```bash
pip install -r requirements.txt --cache-dir pip-cache
```

---

## 🔍 Verificar CUDA

Execute:

```bash
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA Available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

Esperado:
```
PyTorch: 2.7.1+cu118
CUDA Available: True
Device: NVIDIA GeForce GTX 3060 (ou similar)
```

---

## 💾 Cache Local do pip

Os downloads do pip são armazenados em `pip-cache/` dentro do projeto.

**Limpar cache:**
```bash
pip cache purge
```

**Ou manualmente:**
```bash
rmdir /s pip-cache  # Windows
rm -rf pip-cache    # Linux/Mac
```

---

## 🔄 Reinstalar Tudo do Zero

### Windows
```bash
run.bat --reinstall
```

### Linux/Mac
```bash
./run.sh --reinstall
```

Ou manualmente:
```bash
rmdir /s venv           # Windows: rmdir /s /q venv
rm -rf venv             # Linux/Mac
pip cache purge
python -m venv venv
# Ativar venv e seguir passos 3-4 acima
```

---

## ⚠️ Problemas Comuns

### PyTorch ainda em CPU
**Causa:** Versão errada foi instalada

**Solução:**
```bash
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --force-reinstall --no-cache-dir
```

### CUDA disponível mas não está sendo usado
**Causa:** Código pode estar usando CPU explicitamente

**Solução:** Verificar `ai/context_analyzer.py` e `audio/transcriber.py`

Ambos já têm detecção automática:
```python
self.device = "cuda" if torch.cuda.is_available() else "cpu"
```

### Download muito lento
**Causa:** Rede lenta ou índice PyTorch congestionado

**Solução:** Use cache local (já configurado) ou tente novamente

---

## 📋 Arquivo de Configuração

- `requirements.txt` - Dependências padrão (PyTorch não incluído)
- `requirements-cuda.txt` - Instruções para CUDA 11.8
- `run.bat` - Script de inicialização (Windows)
- `run.sh` - Script de inicialização (Linux/Mac)

---

## 🎯 O que foi feito

✅ Todos os scripts usam Python da **venv SEMPRE**
✅ Cache local do pip configurado (`pip-cache/`)
✅ PyTorch com CUDA 11.8 configurado
✅ Detecção automática de CUDA em ContextAnalyzer
✅ Detecção automática de CUDA em Transcriber (Whisper)
✅ run.bat com prompt interativo (opções de limpeza, reinstalação, etc)
✅ run.sh com même funcionalidade para Unix

---

**Dúvidas?** Verifique os logs em `logs/app.log`
