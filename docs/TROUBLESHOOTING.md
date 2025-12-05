# 🔧 Troubleshooting Guide

Guia de resolução de problemas comuns no Analisador de Microfone com IA.

## 🎙️ Problemas de Áudio

### Erro: "No module named 'pyaudio'"

**Causa**: PyAudio não está instalado corretamente.

**Solução Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**Solução Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-dev portaudio19-dev
pip install pyaudio
```

**Solução macOS:**
```bash
brew install portaudio
pip install pyaudio
```

### Erro: "No input device available"

**Causa**: Microfone não detectado ou não configurado.

**Solução:**
1. Verifique se o microfone está conectado
2. Vá para **Configurações > Áudio** na interface web
3. Selecione o dispositivo de áudio correto no dropdown "Device ID"
4. Reinicie a aplicação

### Áudio não está sendo capturado

**Verificar:**
- [ ] Microfone está conectado e ligado?
- [ ] Microfone está ativado nas configurações do SO?
- [ ] Volume do microfone não está mudo?
- [ ] Outro aplicativo está usando o microfone?

**Passos:**
1. Teste o microfone em outro aplicativo (Audacity, Discord)
2. Vá para **Dashboard** e clique em **Iniciar Captura**
3. Fale perto do microfone e veja se a barra de energia sobe
4. Se não subir, reinicie a aplicação

### Latência alta de transcrição

**Causas comuns:**
- Modelo Whisper muito grande
- CPU ocupada
- Conexão de internet lenta (para updates)

**Soluções:**
1. Use modelo "tiny" nas Configurações (mais rápido, menos preciso)
2. Feche outros aplicativos pesados
3. Verifique CPU em gerenciador de tarefas

---

## 🧠 Problemas com IA

### Whisper não está funcionando

**Erro: "ModuleNotFoundError: No module named 'whisper'"**

```bash
pip install openai-whisper
```

### Detecção de keywords não funciona

**Verificar:**
- [ ] Palavra-chave está habilitada?
- [ ] Confiança mínima não está muito alta?
- [ ] Padrão da palavra-chave está correto?

**Testes:**
1. Vá para **Palavras-Chave**
2. Clique em **Testar** próximo à palavra-chave
3. Digite texto que contenha a palavra
4. Veja se detecta

### Análise de contexto não funciona

**Causa**: Modelo de embeddings não baixado.

**Solução:**
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('distiluse-base-multilingual-cased-v2')"
```

---

## 🌐 Problemas de Interface Web

### Interface não carrega (erro 404/500)

**Causa**: Servidor Flask não iniciou corretamente.

**Solução:**
1. Verifique se porta 5000 está disponível
2. Procure erros no console
3. Tente trocar porta: `FLASK_PORT=5001 python main.py`

### Desconexão de WebSocket

**Causa**: Firewall ou proxy bloqueando WebSocket.

**Solução:**
1. Verifique firewall
2. Tente desabilitar proxy
3. Use `localhost` em vez de IP
4. Verifique porta 5000 em gerenciador de rede

### Tema Dark não persiste

**Solução:**
1. Limpe cache do navegador (Ctrl+Shift+Del)
2. Verifique localStorage:
   - F12 > Application > LocalStorage
   - Procure por `theme`
3. Reinicie navegador

### Gráfico de atividade não aparece

**Causa**: Chart.js não carregou.

**Solução:**
1. Verifique console (F12)
2. Verifique arquivo `web/static/index.html`
3. Limpe cache: Ctrl+Shift+Del + F5

---

## 💾 Problemas de Banco de Dados

### Erro: "database is locked"

**Causa**: Múltiplas instâncias da aplicação acessando BD.

**Solução:**
1. Feche todas as instâncias da aplicação
2. Delete `database/app.db`
3. Reinicie a aplicação

### Histórico vazio

**Causa**: Banco de dados não inicializou.

**Solução:**
```bash
python -c "from database.db_manager import init_db; init_db()"
```

### Configuração não salva

**Verificar:**
1. Arquivo `config.json` existe?
2. Pasta `database/` tem permissão de escrita?
3. Verificar em **Backup > Exportar Config**

---

## 📦 Problemas de Instalação

### Erro: "pip: command not found"

**Solução:**
```bash
# Windows
python -m pip install -r requirements.txt

# Linux/Mac
python3 -m pip install -r requirements.txt
```

### Ambiente virtual não ativa

**Windows:**
```bash
.\venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Dependência incompatível com Python

**Solução:**
1. Atualize Python para 3.8+
2. Crie novo venv: `python -m venv venv_novo`
3. Instale dependências novamente

---

## 🚀 Performance

### Aplicação lenta

**Checklist:**
- [ ] CPU alta? Feche aplicativos
- [ ] RAM baixa? Reinicie SO
- [ ] Modelo Whisper é pequeno? (use "tiny")
- [ ] Análise de contexto ativada? (desative se não usar)

**Verificar logs:**
```bash
tail -f logs/app.log
```

### Alto uso de memória

**Causas:**
- Cache de embeddings muito grande (limpar ou reduzir)
- Histórico de detecções muito longo

**Solução:**
1. Vá para **Backup > Reset Configuration**
2. Limpe logs antigos

---

## 🔐 Problemas de Segurança

### CORS error

**Erro: "Access to XMLHttpRequest blocked by CORS policy"**

**Solução:**
- Aplicação deve estar em `localhost:5000`
- Não acesse por IP se em rede diferente
- Verifique arquivo `web/app.py` para configuração CORS

---

## 📋 Coletando Informações para Debug

Se nenhuma solução funcionar, colete informações:

```bash
# Versão Python
python --version

# Versão do SO
python -c "import platform; print(platform.platform())"

# Listar dispositivos de áudio
python -c "from audio.processor import AudioProcessor; import json; print(json.dumps(AudioProcessor.list_devices(), indent=2))"

# Ver logs
cat logs/app.log

# Verificar portas
netstat -ano | grep 5000  # Windows
lsof -i :5000             # Linux/Mac
```

## 📞 Obter Ajuda

Se o problema persistir:

1. **Verifique documentação**: [DOCUMENTACAO_COMPLETA.md](DOCUMENTACAO_COMPLETA.md)
2. **Procure issues existentes**: [GitHub Issues](../../issues)
3. **Abra uma nova issue** com:
   - Versão do Python
   - Sistema Operacional
   - Passos para reproduzir
   - Logs (copie de `logs/app.log`)
   - Screenshots de erros

---

**Última atualização**: 2025
