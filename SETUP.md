# 🚀 Guia de Setup - Scripts Melhorados

Os scripts `run.bat` (Windows) e `run.sh` (Linux/Mac) foram atualizados com opções avançadas para gerenciar a instalação.

---

## 📋 Opções Disponíveis

### Windows (run.bat)

```bash
# Iniciar normalmente (padrão)
run.bat

# Limpar cache do pip
run.bat --clean

# Reinstalar tudo do zero (deleta venv + limpa cache)
run.bat --reinstall

# Deletar apenas o ambiente virtual
run.bat --delete-venv

# Ver ajuda
run.bat --help
run.bat -h
```

### Linux/Mac (run.sh)

```bash
# Iniciar normalmente (padrão)
./run.sh

# Limpar cache do pip
./run.sh --clean

# Reinstalar tudo do zero (deleta venv + limpa cache)
./run.sh --reinstall

# Deletar apenas o ambiente virtual
./run.sh --delete-venv

# Ver ajuda
./run.sh --help
./run.sh -h
```

---

## 🔧 O que cada opção faz

### Inicialização Normal (padrão)

```bash
run.bat          # Windows
./run.sh         # Linux/Mac
```

**Passos:**
1. ✅ Verifica se Python está instalado
2. ✅ Cria ambiente virtual (se não existir)
3. ✅ Ativa ambiente virtual
4. ✅ Instala dependências (primeira vez)
5. ✅ Baixa modelo Whisper (primeira vez)
6. ✅ Cria diretórios necessários (logs, database, audio_library)
7. ✅ **Abre navegador automaticamente** em http://localhost:5000
8. ✅ Inicia servidor Flask na porta 5000

**Saída esperada:**
```
[OK] Python encontrado
[OK] Ambiente virtual ativado
[OK] Dependências instaladas
[OK] Modelo Whisper pronto
Abrindo navegador em 5 segundos...
Acesse: http://localhost:5000

 * Running on http://127.0.0.1:5000
```

✨ **O navegador vai abrir automaticamente após 3 segundos!**

---
1. ✅ Verifica se Python está instalado
2. ✅ Cria ambiente virtual (se não existir)
3. ✅ Ativa ambiente virtual
4. ✅ Instala dependências (primeira vez apenas)
5. ✅ Download do modelo Whisper (se não existir)
6. ✅ Cria diretórios necessários
7. ✅ Inicia a aplicação
8. 🌐 Acessa http://localhost:5000

---

### Limpar Cache do Pip

```bash
run.bat --clean      # Windows
./run.sh --clean     # Linux/Mac
```

**Quando usar:**
- Quando há problemas de compatibilidade
- Antes de uma reinstalação
- Se houver erros de cache corrompido

**Passos:**
1. ✅ Executa `pip cache purge`
2. ✅ Informa que deve usar `run.bat` normalmente depois

**Tempo:** ~30 segundos

---

### Reinstalar Tudo do Zero

```bash
run.bat --reinstall      # Windows
./run.sh --reinstall     # Linux/Mac
```

**Quando usar:**
- Quando há muitos problemas de dependência
- Após atualizar Python
- Para começar completamente do zero
- Se houve mudanças significativas no requirements.txt

**Passos:**
1. ⚠️ Pede confirmação
2. 🗑️ Deleta pasta `venv`
3. 🧹 Limpa cache do pip
4. ✅ Pronto para nova instalação
5. Use `run.bat` novamente para reinstalar

**Tempo:** ~5 minutos

---

### Deletar Apenas a Venv

```bash
run.bat --delete-venv      # Windows
./run.sh --delete-venv     # Linux/Mac
```

**Quando usar:**
- Quando quer recriar o ambiente virtual
- Para liberar espaço em disco
- Se o venv está corrompido mas quer manter pip cache

**Passos:**
1. ⚠️ Pede confirmação
2. 🗑️ Deleta pasta `venv`
3. Use `run.bat` novamente para recriar

**Tempo:** ~1 segundo

---

## 🎯 Fluxogramas de Decisão

### "A aplicação não inicia"

```
├─ run.bat
│  └─ Se falhar → run.bat --clean → run.bat
│
└─ Se continuar falhando → run.bat --reinstall → run.bat
```

### "Tenho problema de compatibilidade"

```
run.bat --clean → run.bat
```

### "Atualizei Python"

```
run.bat --reinstall → run.bat
```

### "Requirements.txt mudou"

```
run.bat --clean → run.bat
```

### "Quero começar do zero"

```
run.bat --reinstall → run.bat
```

### "Preciso liberar espaço"

```
run.bat --delete-venv → run.bat
```

---

## 📊 Comparação de Opções

| Opção | Deleta venv? | Limpa cache pip? | Reinstala deps? | Tempo |
|-------|--------------|------------------|-----------------|-------|
| (normal) | ✗ | ✗ | ✗ | 30s |
| --clean | ✗ | ✅ | ✗ | 30s |
| --delete-venv | ✅ | ✗ | ✅ | 5m |
| --reinstall | ✅ | ✅ | ✅ | 5m |

---

## ✅ Checklist de Instalação

### Primeira Vez
- [ ] Clonar projeto
- [ ] Abrir terminal na pasta do projeto
- [ ] `run.bat` (ou `./run.sh`)
- [ ] Esperar Whisper baixar (~5 minutos)
- [ ] Acessar http://localhost:5000
- [ ] Configurar microfone
- [ ] Pronto! 🎉

### Se Tiver Problema
- [ ] Tentar `run.bat --clean` depois `run.bat`
- [ ] Se não funcionar: `run.bat --reinstall` depois `run.bat`
- [ ] Ver logs em `logs/app.log`
- [ ] Consultar [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🔍 Verificar Instalação

Após iniciar com sucesso, verifique:

```bash
# 1. Venv foi criado?
dir venv              # Windows
ls -la venv           # Linux/Mac

# 2. Dependências instaladas?
pip list | grep flask
pip list | grep whisper
pip list | grep pygame

# 3. Modelo Whisper baixado?
python -c "import whisper; print(whisper.__file__)"

# 4. Aplicação rodando?
# Acesse: http://localhost:5000
```

---

## 🚨 Troubleshooting Comum

### "ModuleNotFoundError: No module named 'flask'"

```bash
run.bat --clean
run.bat
```

### "CUDA out of memory"

```bash
# Usar CPU em vez de GPU
set WHISPER_DEVICE=cpu    # Windows
export WHISPER_DEVICE=cpu # Linux/Mac
run.bat
```

### "venv corrompido"

```bash
run.bat --reinstall
run.bat
```

### "Muito lento na primeira execução"

- Paciência! Whisper está fazendo download (~500MB)
- Veja progresso no console
- Próximas execuções serão rápidas

### "Porta 5000 já está em uso"

```python
# Editar main.py e mudar:
app.run(host="0.0.0.0", port=5001)  # ou outra porta
```

---

## 📚 Próximas Etapas

Após inicializar com sucesso:

1. 📖 Leia [QUICK_START.md](QUICK_START.md)
2. 🎯 Configure seu microfone
3. 💡 Explore [EXEMPLOS_USO.md](EXEMPLOS_USO.md)
4. 🚀 Comece a usar!

---

## 💡 Dicas Avançadas

### Usar Python 3.11 específico

```bash
# Windows
"C:\Python311\python.exe" -m venv venv

# Linux/Mac
python3.11 -m venv venv
```

### Offline mode (sem download de Whisper)

Se já tiver modelo baixado anteriormente:

```bash
# O script detectará automaticamente
# No cache em ~/.cache/whisper/
```

### Virtual environment customizado

```bash
# Usar venv em outro lugar
python -m venv C:\outro\local\venv
C:\outro\local\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## 🆘 Ajuda Adicional

- 📖 [README.md](README.md) - Guia geral
- 🔧 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problemas comuns
- ✅ [VERIFICACAO.md](VERIFICACAO.md) - Checklist de validação
- 💡 [EXEMPLOS_USO.md](EXEMPLOS_USO.md) - Casos de uso

---

**Happy Setup! 🚀**
