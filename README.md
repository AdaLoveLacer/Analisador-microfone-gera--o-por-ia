# 🎙️ Analisador de Microfone com IA

Sistema avançado em Python para análise em tempo real do microfone, com transcrição automática usando Whisper, detecção de palavras-chave contextualizadas com IA para reprodução automática de efeitos sonoros de um determinado banco de dados.

## ✨ Características

- ✅ **Transcrição em Tempo Real**: Usando OpenAI Whisper (modelo leve)
- ✅ **Detecção Inteligente**: Keywords com fuzzy matching e variações
- ✅ **Análise de Contexto**: Embeddings semânticos com sentence-transformers
- ✅ **Interface Web Rica**: Dashboard moderno, responsivo e intuitivo
- ✅ **Configuração Persistente**: Todas as configurações salvas automaticamente
- ✅ **WebSocket em Tempo Real**: Atualizações instantâneas na interface
- ✅ **Histórico e Logs**: Rastreamento completo de detecções
- ✅ **Temas Dark/Light**: Personalizável conforme sua preferência
- ✅ **Backup/Importação**: Exporte e importe suas configurações

## 📋 Requisitos

- Python 3.8+
- Microfone funcional
- 4GB+ RAM (para modelo Whisper)
- ~5GB espaço em disco (para modelos)

## 🚀 Instalação Rápida

### 1. Clone ou crie o diretório

```bash
mkdir analisador-microfone
cd analisador-microfone
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
.\venv\Scripts\Activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 3. Instale dependências

```bash
pip install -r requirements.txt
```

### 4. Download do modelo Whisper (automático na primeira execução)

```bash
python -c "import whisper; whisper.load_model('base')"
```

### 5. Execute a aplicação

```bash
python main.py
```

A aplicação estará disponível em: **http://localhost:5000**

## 🎯 Como Usar

### Dashboard
1. Clique em **"Iniciar Captura"** para começar a analisar seu microfone
2. Veja a transcrição em tempo real na caixa de texto
3. Detecções aparecem automaticamente na lista

### Configurar Palavras-Chave
1. Vá para a aba **"Palavras-Chave"**
2. Clique em **"Nova Palavra-Chave"**
3. Preencha:
   - **Nome**: "Sus" (será exibido)
   - **Padrão**: "sus" (texto a detectar)
   - **Som**: Selecione qual som tocar
   - **Variações**: "suspeitoso, estranho, fake"
   - **Contexto**: "não acredito, mente, fingindo"

### Adicionar Sons
1. Vá para **"Biblioteca de Sons"**
2. Clique em **"Upload de Som"**
3. Selecione um arquivo .mp3 ou .wav
4. Configure nome, volume e categoria

### Configurações Avançadas
Na aba **"Configurações"**, você pode ajustar:
- **Áudio**: Device, sample rate, sensibilidade
- **Whisper**: Modelo, idioma, confiança
- **IA**: Análise de contexto, thresholds
- **UI**: Tema, idioma, refresh rate

### Histórico e Estatísticas
A aba **"Histórico"** mostra:
- Timeline de detecções
- Histórico de transcrições
- Estatísticas por palavra-chave
- Exportação em CSV/JSON

### Backup
Na aba **"Backup"**:
- Crie backups das suas configurações
- Restaure de backups anteriores
- Importe presets predefinidos
- Exporte tudo para portabilidade

## 📁 Estrutura do Projeto

```
analisador-microfone/
├── main.py                 # Entrada principal
├── requirements.txt        # Dependências
├── config_default.json     # Config padrão
├── core/
│   ├── analyzer.py        # Engine principal
│   ├── config_manager.py  # Gerenciador de config
│   └── event_logger.py    # Sistema de logs
├── audio/
│   ├── processor.py       # Captura de áudio
│   ├── transcriber.py     # Integração Whisper
│   └── audio_utils.py     # Utilitários
├── ai/
│   ├── keyword_detector.py    # Detecção fuzzy
│   └── context_analyzer.py    # Análise semântica
├── sound/
│   └── player.py          # Reprodutor de sons
├── web/
│   ├── app.py             # Flask app
│   ├── api_routes.py      # Endpoints REST
│   ├── websocket_handler.py
│   └── static/
│       ├── index.html
│       ├── css/
│       │   └── style.css
│       └── js/
│           ├── main.js
│           ├── config-manager.js
│           ├── ui-controller.js
│           └── websocket-client.js
├── database/
│   └── db_manager.py      # SQLite
├── utils/
│   ├── exceptions.py
│   └── validators.py
└── audio_library/         # Seus sons
    ├── memes/
    ├── efeitos/
    └── notificacoes/
```

## 🔧 Configuração

### Arquivo config.json
Todas as configurações são salvas em `config.json`:

```json
{
  "audio": {
    "device_id": -1,
    "sample_rate": 16000,
    "chunk_size": 2048
  },
  "whisper": {
    "model": "base",
    "language": "pt"
  },
  "keywords": [
    {
      "id": "key_sus",
      "name": "Sus",
      "pattern": "sus",
      "enabled": true,
      "sound_id": "sound_sus"
    }
  ]
}
```

### Variáveis de Ambiente
Configure em `.env` (veja `.env.example`):

```bash
FLASK_ENV=development
WHISPER_MODEL=base
AUDIO_DEVICE_ID=-1
```

## 📊 Performance *precisa de revisão*

- **Latência de Transcrição**: ~2 segundos (modelo base)
- **Latência de Detecção**: ~500ms
- **Consumo de Memória**: ~400-500MB
- **CPU**: ~20-30% em repouso, ~70% durante transcrição
-------------------------------------------------------------
## 🐛 Troubleshooting

### Erro: "No module named 'pyaudio'"
```bash
pip install --upgrade pyaudio
# Se falhar, tente:
pip install pipwin
pipwin install pyaudio
```

### Erro: "CUDA not available"
Use CPU:
```
WHISPER_DEVICE=cpu python main.py
```

### Áudio não está sendo detectado
1. Verifique o dispositivo de áudio:
   - Na aba Configurações, seção Áudio
   - Selecione o dispositivo correto
2. Teste o microfone no sistema

### WebSocket desconectando
Verifique firewall ou proxy bloqueando WebSockets na porta 5000

## 📝 Logs

Logs são salvos em:
- `logs/app.log` - Logs gerais
- Database SQLite - Histórico estruturado

Veja em **Histórico** na interface web

## 🔒 Segurança

- ✅ Validação de todas as entradas
- ✅ CORS configurado
- ✅ Sem dados sensíveis em logs
- ✅ Arquivo de config protegido
- ✅ Análise local (sem envio a servidores)

## 📦 Dependências Principais

- **whisper** - Transcrição (OpenAI)
- **pyaudio** - Captura de áudio
- **flask** - Web framework
- **socketio** - WebSocket
- **sentence-transformers** - Embeddings
- **thefuzz** - Fuzzy matching
- **pygame** - Reprodução de som

## 🚧 Roadmap

- [ ] Suporte a múltiplos idiomas
- [ ] Gravação de sessões
- [ ] Análise de sentimento
- [ ] Integração com Discord/Twitch
- [ ] Mobile app
- [ ] GPU acceleration

## 📄 Licença

Projeto de código aberto. Use livremente!

## 🤝 Contribuindo

Encontrou um bug? Tem uma ideia?
- Abra uma issue
- Mande um pull request
- Compartilhe feedback

## 📞 Suporte

Para dúvidas, problemas ou sugestões:
1. Verifique a [documentação completa](DOCUMENTACAO_COMPLETA.md)
2. Consulte os logs em `logs/`
3. Veja o histórico na interface web

---

**Desenvolvido com ❤️ e IA** | 2025
