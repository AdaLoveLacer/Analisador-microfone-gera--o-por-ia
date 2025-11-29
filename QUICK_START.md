# 🚀 QUICK START

Comece a usar o Analisador em 5 minutos!

## 1️⃣ Instalação (2 minutos)

### Windows
```bash
# Abrir PowerShell em pasta do projeto
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
python main.py
```

### Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

**OU** use o script automático:
```bash
run.bat
```

### Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

**OU** use o script automático:
```bash
bash run.sh
# ou
chmod +x run.sh
./run.sh
```

## 📋 Opções do Script

O script `run.bat` (Windows) e `run.sh` (Linux/Mac) agora têm opções avançadas:

```bash
# Iniciar normalmente
run.bat

# Limpar cache do pip (se tiver problemas)
run.bat --clean

# Reinstalar tudo do zero
run.bat --reinstall

# Ver todas as opções
run.bat --help
```

**Veja [SETUP.md](SETUP.md) para detalhes completos das opções.

## 2️⃣ Acessar Interface (1 minuto)

Abra navegador: **http://localhost:5000**

## 3️⃣ Configuração Básica (2 minutos)

### Passo 1: Selecionar Microfone
- Vá para **Configurações > Áudio**
- Selecione seu microfone em "Device ID"
- Clique **Salvar**

### Passo 2: Adicionar Sua Primeira Palavra-Chave
- Vá para **Palavras-Chave**
- Clique **+ Nova Palavra-Chave**
- Preencha:
  - **Nome**: "Sus"
  - **Padrão**: "sus"
  - **Variações**: "suspeitoso, estranho"
  - **Som**: (deixe vazio por enquanto)
- Clique **Salvar**

### Passo 3: Testar Detecção
- Vá para **Dashboard**
- Clique **Iniciar Captura**
- Fale a palavra "sus" próximo ao microfone
- Veja a transcrição na caixa de texto
- Detecção aparece na lista

## 4️⃣ Próximos Passos

### Adicionar Sons
1. Prepare arquivo MP3 ou WAV
2. Vá para **Biblioteca de Sons**
3. Clique **Upload de Som**
4. Selecione arquivo e configure volume
5. Volte para palavras-chave e associe o som

### Explorar Recursos
- **Dashboard**: Monitore transcrições em tempo real
- **Histórico**: Veja estatísticas de detecções
- **Backup**: Exporte/importe suas configurações
- **Configurações**: Ajuste modelos de IA e áudio

---

## 📚 Recursos

| Recurso | Para... |
|---------|---------|
| [SETUP.md](SETUP.md) | Opções avançadas dos scripts |
| [README.md](README.md) | Guia completo |
| [DOCUMENTACAO_COMPLETA.md](DOCUMENTACAO_COMPLETA.md) | Documentação técnica |
| [EXEMPLOS_USO.md](EXEMPLOS_USO.md) | Casos de uso reais |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Resolver problemas |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribuir ao projeto |

---

## 🎯 Checklist de Setup

- [ ] Python instalado (3.8+)
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Aplicação iniciada (`python main.py`)
- [ ] Interface acessível (`localhost:5000`)
- [ ] Microfone funcionando
- [ ] Primeira palavra-chave criada
- [ ] Detecção testada

---

## ⚡ Comandos Úteis

```bash
# Executar aplicação
python main.py

# Rodar testes
pytest tests/

# Verificar erros (linting)
flake8 core audio ai sound web

# Formatar código
black .

# Verificar tipos
mypy core/

# Ver logs
tail -f logs/app.log
```

---

## 🆘 Se algo não funcionar

1. **Verifique Python**: `python --version` (deve ser 3.8+)
2. **Use script de limpeza**: `run.bat --clean`
3. **Reinstale tudo**: `run.bat --reinstall`
4. **Veja logs**: `logs/app.log`
5. **Consulte**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
6. **Veja opções avançadas**: [SETUP.md](SETUP.md)

---

## ❓ Dúvidas?

- 📖 Leia [DOCUMENTACAO_COMPLETA.md](DOCUMENTACAO_COMPLETA.md)
- 💡 Veja [EXEMPLOS_USO.md](EXEMPLOS_USO.md)
- 🔧 Consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Aproveite! 🎙️**
