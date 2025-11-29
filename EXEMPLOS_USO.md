# 📚 Exemplos de Uso

Exemplos práticos de como usar o Analisador de Microfone com IA.

## 🎯 Caso de Uso 1: Stream Twitch com Efeitos

Detectar palavras-chave durante um stream e tocar efeitos sonoros automaticamente.

### Setup

1. **Crie suas palavras-chave:**
   - "sus" → som de "very sus" (500ms)
   - "cringe" → som de buzzer (200ms)
   - "gg" → som de aplausos

2. **Configure sons:**
   - Vá para **Biblioteca de Sons**
   - Upload dos seus arquivos MP3
   - Defina volume em 0.8 (não muito alto)

3. **Inicie captura:**
   - Clique em **Iniciar Captura**
   - Deixe rodando enquanto transmite

4. **Monitore:**
   - Dashboard mostra detecções em tempo real
   - Histórico registra tudo

---

## 🤖 Caso de Uso 2: Análise de Contexto

Detectar keywords apenas em contextos específicos (ex: "banco" só se contexto for "roubo" ou "crime").

### Exemplo: Detectar "banco" com contexto

```json
{
  "id": "key_banco_crime",
  "name": "Roubo de Banco",
  "pattern": "banco",
  "enabled": true,
  "sound_id": "sound_alarm",
  "variations": ["bancos", "bancário"],
  "context_keywords": ["roubo", "crime", "assalto", "dinheiro"],
  "context_weight": 0.5,
  "min_confidence": 0.7
}
```

### Como funciona:

1. Transcrição: "Um roubo aconteceu no banco hoje"
2. Detecção exata: encontra "banco"
3. Análise de contexto: verifica se texto contém palavras-chave de contexto
4. Se score de contexto > 0.5: **detecção confirmada** → toca som

---

## 📊 Caso de Uso 3: Análise de Padrões em Podcast

Registrar quando hosts mencionam temas específicos e gerar estatísticas.

### Configuração

```json
{
  "keywords": [
    {
      "id": "key_tech",
      "name": "Menção Tecnologia",
      "pattern": "tecnologia",
      "variations": ["tech", "AI", "inteligência artificial", "software"],
      "context_keywords": ["novo", "desenvolvendo", "criando"],
      "enabled": true
    },
    {
      "id": "key_games",
      "name": "Menção Games",
      "pattern": "game",
      "variations": ["videogame", "gaming", "jogo"],
      "enabled": true
    }
  ]
}
```

### Análise

1. Execute durante o podcast
2. Vá para **Histórico > Estatísticas**
3. Veja gráficos:
   - Palavras mais mencionadas
   - Tendências ao longo do tempo
   - Contexto das menções

---

## 🎓 Caso de Uso 4: Monitoramento de Aula

Detectar palavras específicas pronunciadas pelo professor para alertas ou registros.

### Setup para Aula

```json
{
  "keywords": [
    {
      "name": "Próxima Aula",
      "pattern": "próxima aula",
      "sound_id": "sound_chime",
      "enabled": true,
      "context_keywords": ["dia", "semana", "próximo"]
    },
    {
      "name": "Avaliação",
      "pattern": "avaliação",
      "sound_id": "sound_alert",
      "enabled": true,
      "context_keywords": ["prova", "teste", "exame"]
    }
  ],
  "ui": {
    "theme": "dark",
    "notification_style": "discrete"
  }
}
```

### Fluxo

1. Aluna inicia captura antes da aula
2. Sempre que professor menciona "próxima aula", som avisa
3. Histórico fica disponível para revisão

---

## 🎬 Caso de Uso 5: Dublagem/Legendagem

Usar o sistema para transcrever e registrar padrões de fala para criação de conteúdo.

### Exemplo: Analisar Sotaque

```python
# Script Python para processar histórico
from database.db_manager import Database
import json

db = Database()
transcriptions = db.get_all_transcriptions()

# Encontrar padrões
patterns = {}
for transcription in transcriptions:
    text = transcription['text'].lower()
    # Análise customizada
    # ...

# Exportar para análise
with open('padroes_sotaque.json', 'w') as f:
    json.dump(patterns, f, indent=2, ensure_ascii=False)
```

---

## 🎮 Caso de Uso 6: Multiplayer Gaming

Usar detecção de keywords para automações em jogos (Discord bot, chat).

### Integração com Discord

```python
# Pseudocódigo - integração customizada
from websocket_handler import WebSocketClient

client = WebSocketClient()

@client.on('keyword_detected')
def on_keyword(event):
    keyword_name = event['keyword_name']
    
    if keyword_name == "enemy":
        # Enviar alerta no Discord
        send_discord_message(f"Inimigo detectado! {event['confidence']:.0%}")
    
    elif keyword_name == "victory":
        # Celebrar
        send_discord_message("🎉 VITÓRIA!")
```

---

## 📝 Caso de Uso 7: Importação de Configurações

Usar presets para diferentes cenários sem reconfigurar.

### Criar Preset

1. **Configure tudo como quer**
2. **Vá para Backup > Exportar Config**
3. **Salve como `config_streaming.json`**

### Aplicar Preset

```bash
# Copie arquivo salvo para pasta raiz
cp config_streaming.json config.json
python main.py
```

### Diferentes Presets

- `config_streaming.json` - Sons altos, sensibilidade alta
- `config_office.json` - Sons baixos, sensibilidade baixa
- `config_analysis.json` - Muita análise de contexto
- `config_minimal.json` - Apenas detecção básica

---

## 🔧 Caso de Uso 8: Integração Customizada

Estender o sistema com lógica customizada.

### Adicionar Handler Customizado

```python
# myapp.py
from core.analyzer import MicrophoneAnalyzer
from core.config_manager import ConfigManager

# Inicializa
config = ConfigManager()
analyzer = MicrophoneAnalyzer(config)

# Registra callback customizado
def on_detection(detection):
    """Callback chamado quando keyword é detectada"""
    keyword_id = detection['keyword_id']
    confidence = detection['confidence']
    text = detection['text']
    
    # Lógica customizada
    if confidence > 0.9:
        print(f"✅ Alta confiança: {keyword_id}")
        # Fazer algo especial
    
    # Enviar para API externa
    import requests
    requests.post('https://seu-servidor.com/detections', json=detection)

analyzer.on_keyword_detected = on_detection

# Inicia
analyzer.start()

try:
    # Deixa rodando
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    analyzer.stop()
```

---

## 📱 Caso de Uso 9: Integração com Home Assistant

Usar detecções para automações em casa inteligente.

### Setup

```yaml
# configuration.yaml
automation:
  - alias: "Detectou Palavra-Chave"
    trigger:
      webhook_id: seu_webhook_id
    action:
      - service: light.turn_on
        entity_id: light.sala
      - service: media_player.play_media
        entity_id: media_player.speaker
        data:
          media_content_type: music
          media_content_id: "spotify:playlist:seu_playlist"
```

```python
# myapp.py - enviar webhook para Home Assistant
def on_detection(detection):
    import requests
    
    if detection['keyword_id'] == 'key_lights':
        requests.post(
            'http://192.168.1.100:8123/api/webhook/seu_webhook_id',
            json={'keyword': 'lights_on'}
        )
```

---

## 🎤 Caso de Uso 10: Treinamento de Reconhecimento

Usar histórico para melhorar modelos customizados.

### Exportar dados de treinamento

```python
from database.db_manager import Database
import json

db = Database()
detections = db.get_all_detections()

# Preparar dataset
dataset = []
for detection in detections:
    dataset.append({
        'text': detection['text'],
        'keyword': detection['keyword_id'],
        'confidence': detection['confidence'],
        'context_score': detection.get('context_score', 0)
    })

# Salvar
with open('training_data.json', 'w') as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print(f"Dataset com {len(dataset)} exemplos exportado!")
```

---

## ⚙️ Caso de Uso 11: Monitoramento Contínuo

Deixar aplicação rodando 24/7 com logs e alertas.

### Usando systemd (Linux)

```ini
# /etc/systemd/system/audio-analyzer.service
[Unit]
Description=Audio Analyzer Service
After=network.target

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/path/to/projeto
Environment="FLASK_PORT=5000"
ExecStart=/path/to/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Ativar
sudo systemctl enable audio-analyzer
sudo systemctl start audio-analyzer

# Monitorar
sudo systemctl status audio-analyzer
sudo journalctl -u audio-analyzer -f
```

---

## 🎙️ Caso de Uso 12: Análise de Reunião

Registrar e analisar reuniões com destaques automáticos.

### Config para Reuniões

```json
{
  "keywords": [
    {"name": "Action Item", "pattern": "ação", "sound_id": "sound_chime"},
    {"name": "Decision", "pattern": "decisão", "sound_id": "sound_ding"},
    {"name": "Deadline", "pattern": "prazo", "sound_id": "sound_alert"},
    {"name": "Risk", "pattern": "risco", "sound_id": "sound_warning"}
  ],
  "audio": {
    "sample_rate": 16000,
    "chunk_size": 2048
  }
}
```

### Depois da Reunião

1. Vá para **Histórico > Detecções**
2. Filtrar por tipo
3. Exportar para CSV
4. Importar em aplicação de notas

---

## 📞 Próximos Passos

Para implementar seus próprios casos de uso:

1. **Estude a documentação**: [DOCUMENTACAO_COMPLETA.md](DOCUMENTACAO_COMPLETA.md)
2. **Explore o código**: Comece por `core/analyzer.py`
3. **Rode os testes**: `pytest tests/` para entender o fluxo
4. **Customize**: Fork o projeto e adapte!

---

**Happy analyzing!** 🎙️✨
