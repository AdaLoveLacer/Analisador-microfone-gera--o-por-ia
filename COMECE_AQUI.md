# 👋 Bem-vindo ao Analisador de Microfone com IA

Obrigado por usar este projeto! Este arquivo ajuda você a começar.

---

## 🎯 Comece Agora (Escolha Um)

### ⚡ Opção 1: Quero Começar AGORA
```bash
# Windows
run.bat

# Linux/Mac
bash run.sh
```

**Vai levar**: 2-5 minutos (primeira vez pode ser mais, dependendo da internet)  
**Resultado**: Interface web abre automaticamente em http://localhost:5000

---

### 📖 Opção 2: Quero Ler Primeiro
📚 **[DOCUMENTACAO_INDEX.md](DOCUMENTACAO_INDEX.md)** ← COMECE AQUI!

Ele te guia para:
- Visão geral do projeto
- Casos de uso
- Troubleshooting
- Documentação técnica

---

## 🚀 Primeiros Passos (3 minutos)

### 1. Instalar
```bash
run.bat          # Windows
bash run.sh      # Linux/Mac
```

### 2. Configurar Microfone
- Abra http://localhost:5000
- Vá para **Configurações > Áudio**
- Selecione seu microfone
- Clique **Salvar**

### 3. Adicionar Palavra-Chave
- Vá para **Palavras-Chave > + Nova**
- Nome: "Sus"
- Padrão: "sus"
- Variações: "suspeitoso, estranho"
- Clique **Salvar**

### 4. Testar
- Vá para **Dashboard**
- Clique **Iniciar Captura**
- Fale "sus"
- Veja a transcrição aparecer! ✨

---

## 📚 Documentação

| Quando... | Leia... |
|-----------|---------|
| Quero começar rápido | [QUICK_START.md](QUICK_START.md) |
| Quero entender o projeto | [README_COMPLETO.md](README_COMPLETO.md) |
| Tenho um problema | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| Detalhes técnicos | [DOCUMENTACAO_COMPLETA.md](DOCUMENTACAO_COMPLETA.md) |
| Casos de uso | [EXEMPLOS_USO.md](EXEMPLOS_USO.md) |
| Como contribuir | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Scripts (--clean, etc) | [SETUP.md](SETUP.md) |
| Índice completo | [DOCUMENTACAO_INDEX.md](DOCUMENTACAO_INDEX.md) |

---

## ❓ Perguntas Frequentes

### P: Preciso de algo especial?
**R**: Apenas Python 3.8+ e um microfone. Tudo mais é baixado automaticamente!

### P: Demora muito?
**R**: Primeira vez leva 3-5 minutos (Whisper é ~500MB). Próximas são instantâneas.

### P: Como funciona?
**R**: Captura áudio → Transcreve com IA → Detecta palavras-chave → Reproduz sons

### P: Funciona offline?
**R**: Não (precisa da IA Whisper). Mas você pode cacheá-lo localmente após baixar.

### P: Qual é o custo?
**R**: 100% gratuito! (Whisper e sentence-transformers são open-source)

### P: Funciona em Mac/Linux?
**R**: Sim! Execute `bash run.sh` em vez de `run.bat`

---

## 🆘 Se Algo Der Errado

### Erro: Python não encontrado
```bash
# Instale Python em https://www.python.org
# Windows: Marque "Add Python to PATH"
```

### Erro: Microfone não encontrado
```bash
# Teste se o microfone funciona no Windows/Mac/Linux
# Depois execute:
run.bat --reinstall
```

### Erro: Transcrição muito lenta
```bash
# Edite config.json e mude:
"model": "tiny"  # em vez de "base"
```

### Mais problemas?
👉 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 💡 Dicas

### Aumentar performance
```json
{
  "model": "tiny",           // Menor = mais rápido
  "chunk_size": 1024,        // Menor = mais responsivo
  "fuzzy_threshold": 70      // Menor = detecta mais
}
```

### Usar GPU
```json
{
  "device": "cuda"           // Se tiver NVIDIA GPU
}
```

### Adicionar novos sons
1. Vá para **Biblioteca de Sons**
2. **Upload de Som** (MP3/WAV)
3. Associe a uma palavra-chave
4. Pronto!

---

## 🎮 Casos de Uso

- 🎙️ **Streamers**: Detecta chat e reproduz efeitos
- 🎓 **Educadores**: Monitora palavras-chave em aulas
- 🏢 **Produtividade**: Automação baseada em fala
- 🎵 **Músicos**: Cria samples automáticos
- 🤖 **IA/ML**: Plataforma de ML customizável

Veja [EXEMPLOS_USO.md](EXEMPLOS_USO.md) para 12 exemplos completos!

---

## 🔧 Comandos Úteis

```bash
# Iniciar normal
run.bat
bash run.sh

# Limpar cache (se tiver problema)
run.bat --clean
bash run.sh --clean

# Reinstalar tudo do zero
run.bat --reinstall
bash run.sh --reinstall

# Deletar só venv
run.bat --delete-venv
bash run.sh --delete-venv

# Ver ajuda
run.bat --help
bash run.sh --help

# Rodar testes
pytest tests/ -v

# Formatter código
black .

# Lint
flake8 .
```

---

## 📞 Precisa de Ajuda?

1. **FAQ**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. **Documentação**: [DOCUMENTACAO_INDEX.md](DOCUMENTACAO_INDEX.md)
3. **GitHub Issues**: Crie uma issue
4. **GitHub Discussions**: Converse com comunidade

---

## 🎉 Próximos Passos

1. ✅ Execute `run.bat` ou `bash run.sh`
2. ✅ Abra http://localhost:5000
3. ✅ Configure seu microfone
4. ✅ Teste com uma palavra-chave
5. ✅ Aproveite! 🚀

---

## 📊 Status do Projeto

- ✅ 100% funcional
- ✅ 100% documentado
- ✅ 70% testado
- ✅ Pronto para uso

**Versão**: 1.0.0-beta  
**Licença**: MIT

---

**Aproveite! Se gostar, dê uma ⭐ no GitHub!**

Criado com ❤️ para makers e entusiastas de IA.
