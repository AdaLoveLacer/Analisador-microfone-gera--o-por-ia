# 📋 Documentação Completa - Analisador de Microfone com IA

## 🎯 Visão Geral do Projeto

Sistema standalone em Python que captura áudio do microfone em tempo real, transcreve usando Whisper, detecta palavras-chave contextualizadas com IA leve e toca efeitos sonoros correspondentes. Interface web rica para configuração persistente.

### Características Principais
- ✅ Transcrição em tempo real com Whisper (modelo leve)
- ✅ Detecção de palavras-chave + análise de contexto
- ✅ Reprodução de efeitos sonoros automática
- ✅ Interface web avançada com persistência
- ✅ Configurações salvassem em banco de dados
- ✅ Logging e histórico de detecções
- ✅ WebSocket para atualizações em tempo real
- ✅ Sistema de temas e personalização

---

## 📂 Estrutura do Projeto Final

```
analisador-microfone/
│
├── main.py                          # Entrada principal da aplicação
├── requirements.txt                 # Dependências Python
├── config_default.json              # Configurações padrão (read-only)
├── README.md                        # Instruções de uso
│
├── core/
│   ├── __init__.py
│   ├── analyzer.py                  # Engine principal (orquestra tudo)
│   ├── config_manager.py            # Gerencia configurações persistentes
│   └── event_logger.py              # Log de eventos e histórico
│
├── audio/
│   ├── __init__.py
│   ├── processor.py                 # Captura de áudio em tempo real
│   ├── transcriber.py               # Integração com Whisper
│   └── audio_utils.py               # Utilitários (normalização, etc)
│
├── ai/
│   ├── __init__.py
│   ├── keyword_detector.py          # Detecção de palavras-chave
│   ├── context_analyzer.py          # Análise semântica de contexto
│   └── similarity_utils.py          # Cálculos de similaridade
│
├── sound/
│   ├── __init__.py
│   ├── player.py                    # Reprodutor de sons
│   └── manager.py                   # Gerenciador de biblioteca de sons
│
├── web/
│   ├── __init__.py
│   ├── app.py                       # Flask app + rotas API
│   ├── websocket_handler.py         # WebSocket para streaming
│   ├── auth.py                      # Autenticação simples (opcional)
│   ├── api_routes.py                # Rotas RESTful
│   │
│   ├── static/
│   │   ├── index.html               # Interface principal
│   │   ├── css/
│   │   │   ├── style.css            # Estilos globais
│   │   │   ├── dark-theme.css       # Tema escuro
│   │   │   └── light-theme.css      # Tema claro
│   │   ├── js/
│   │   │   ├── main.js              # Lógica principal do frontend
│   │   │   ├── config-manager.js    # Gerenciamento de configurações
│   │   │   ├── websocket-client.js  # Cliente WebSocket
│   │   │   ├── ui-controller.js     # Controle de UI
│   │   │   └── utils.js             # Funções utilitárias
│   │   └── assets/
│   │       └── icons/
│   │
│   └── templates/
│       └── (opcional para renderização server-side)
│
├── database/
│   ├── __init__.py
│   ├── db_manager.py                # Gerenciador SQLite/JSON
│   ├── models.py                    # Modelos de dados
│   └── migrations.py                # Versionamento de schema
│
├── utils/
│   ├── __init__.py
│   ├── validators.py                # Validação de entrada
│   ├── exceptions.py                # Exceções customizadas
│   └── decorators.py                # Decoradores úteis
│
├── audio_library/                   # Biblioteca padrão de sons
│   ├── memes/
│   ├── efeitos/
│   └── notificacoes/
│
├── logs/
│   ├── app.log                      # Log geral
│   └── errors.log                   # Log de erros
│
└── tests/
    ├── test_audio.py
    ├── test_ai.py
    └── test_api.py
```

---

## 🗄️ Modelo de Dados

### config.json (Estrutura Principal)

```json
{
  "app": {
    "version": "1.0.0",
    "debug": false,
    "log_level": "INFO",
    "auto_start_capture": false
  },
  
  "audio": {
    "device_id": -1,
    "sample_rate": 16000,
    "chunk_size": 2048,
    "channels": 1,
    "min_duration_seconds": 0.5,
    "silence_threshold": 0.02
  },
  
  "whisper": {
    "model": "base",
    "language": "pt",
    "task": "transcribe",
    "fp16": false,
    "device": "cpu"
  },
  
  "ai": {
    "context_analysis_enabled": true,
    "min_context_confidence": 0.6,
    "use_semantic_similarity": true,
    "embedding_model": "sentence-transformers/distiluse-base-multilingual-cased-v2"
  },
  
  "keywords": [
    {
      "id": "key_1",
      "name": "Sus",
      "pattern": "sus",
      "enabled": true,
      "sound_id": "sound_1",
      "variations": ["suspeitoso", "estranho", "fake"],
      "context_keywords": ["não acredito", "mente", "fingindo"],
      "weight": 1.0
    }
  ],
  
  "sounds": [
    {
      "id": "sound_1",
      "name": "Sus",
      "file_path": "audio_library/memes/sus.mp3",
      "volume": 0.8,
      "enabled": true,
      "category": "meme"
    }
  ],
  
  "ui": {
    "theme": "dark",
    "refresh_interval_ms": 100,
    "show_transcript": true,
    "show_confidence": true,
    "max_history_items": 100
  },
  
  "notifications": {
    "desktop_notify": false,
    "sound_on_detection": true,
    "log_detections": true
  }
}
```

### Database Schema (SQLite)

```sql
-- Configurações (persistentes)
CREATE TABLE config (
  id INTEGER PRIMARY KEY,
  key TEXT UNIQUE,
  value TEXT,
  data_type TEXT,
  updated_at TIMESTAMP
);

-- Palavras-chave
CREATE TABLE keywords (
  id TEXT PRIMARY KEY,
  name TEXT,
  pattern TEXT,
  enabled BOOLEAN,
  sound_id TEXT,
  variations TEXT,
  context_keywords TEXT,
  weight REAL,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Sons
CREATE TABLE sounds (
  id TEXT PRIMARY KEY,
  name TEXT,
  file_path TEXT,
  volume REAL,
  enabled BOOLEAN,
  category TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Histórico de detecções
CREATE TABLE detections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TIMESTAMP,
  text_detected TEXT,
  keyword_matched TEXT,
  confidence REAL,
  context_score REAL,
  sound_played TEXT
);

-- Histórico de transcrições
CREATE TABLE transcriptions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TIMESTAMP,
  text TEXT,
  confidence REAL,
  duration_seconds REAL
);
```

---

## 🎨 Interface Web - Seções Principais

### 1. **Dashboard**
- Status de captura (ON/OFF)
- Transcrição em tempo real (último 30 segundos)
- Contadores: Detecções, Transcrições
- Gráfico de atividade das últimas 2 horas
- Botão rápido: Iniciar/Parar captura

### 2. **Palavras-Chave**
- Tabela com todas as keywords
- Adicionar/Editar/Remover
- Ativar/Desativar por keyword
- Importar/Exportar como JSON
- Preview: Toque de som antes de salvar
- Validação em tempo real

### 3. **Biblioteca de Sons**
- Grid de sons (upload + visualização)
- Reproduzir preview
- Editar metadados (nome, categoria, volume)
- Organizar por categoria
- Arrastar/dropear para upload

### 4. **Configurações Avançadas**
- **Áudio**: Selecionar dispositivo, sample rate, sensibilidade
- **Whisper**: Modelo, idioma, confiança mínima
- **IA**: Habilitar análise de contexto, thresholds
- **UI**: Tema (dark/light), idioma, refresh rate
- **Notificações**: Desktop notify, log, som

### 5. **Histórico & Logs**
- Timeline de detecções (filtrable)
- Histórico de transcrições
- Exportar como CSV/JSON
- Buscar por texto
- Estatísticas por keyword

### 6. **Backup & Importação**
- Backup automático de configurações
- Restaurar de backup
- Importar preset de configurações
- Exportar tudo para portabilidade

---

## 🔧 Tecnologias e Dependências

### Backend (Python)
```
openai-whisper==20231214          # Transcrição
pyaudio==0.2.13                   # Áudio (ou sounddevice)
numpy==1.24.0                     # Processamento numérico
flask==3.0.0                      # Web framework
flask-cors==4.0.0                 # CORS
python-socketio==5.9.0            # WebSocket
sentence-transformers==2.2.2      # Embeddings semânticos
scikit-learn==1.3.0               # ML utilities
simpleaudio==1.1.24 (ou pygame)  # Reprodução de som
pydantic==2.0.0                   # Validação
python-dotenv==1.0.0              # Variáveis de ambiente
```

### Frontend (JavaScript)
- Vanilla JS (sem framework pesado)
- Chart.js para gráficos
- Bootstrap 5 ou Tailwind CSS
- Socket.IO cliente para WebSocket
- LocalStorage para persistência

---

## 🔌 API REST - Endpoints

```
GET    /api/status                 # Status geral da app
POST   /api/capture/start          # Iniciar captura
POST   /api/capture/stop           # Parar captura
GET    /api/capture/status         # Status de captura

GET    /api/config                 # Obter configurações
POST   /api/config                 # Atualizar configurações
GET    /api/config/export          # Exportar JSON
POST   /api/config/import          # Importar JSON

GET    /api/keywords               # Listar keywords
POST   /api/keywords               # Criar keyword
PUT    /api/keywords/:id           # Atualizar keyword
DELETE /api/keywords/:id           # Deletar keyword

GET    /api/sounds                 # Listar sounds
POST   /api/sounds/upload          # Upload de som
PUT    /api/sounds/:id             # Atualizar som
DELETE /api/sounds/:id             # Deletar som
POST   /api/sounds/:id/preview     # Toque de preview

GET    /api/detections             # Histórico de detecções
GET    /api/detections/stats       # Estatísticas
GET    /api/transcriptions         # Histórico de transcrições

POST   /api/test/keyword/:id       # Testar keyword/som
POST   /api/backup/create          # Criar backup
POST   /api/backup/restore         # Restaurar backup

WS     /ws                         # WebSocket para updates em tempo real
```

---

## 📡 WebSocket Events

```javascript
// Cliente → Servidor
ws.emit('start_capture')
ws.emit('stop_capture')
ws.emit('update_keyword', {...})
ws.emit('update_config', {...})
ws.emit('test_sound', {sound_id: '...'})

// Servidor → Cliente
ws.on('transcript_update', data)       // Transcrição em tempo real
ws.on('keyword_detected', data)        // Keyword detectada
ws.on('config_updated', data)          // Config atualizada
ws.on('status_update', data)           // Status geral
ws.on('error', data)                   // Erro
```

---

## 🚀 Fluxo de Funcionamento

```
┌─────────────────┐
│   Microfone     │
└────────┬────────┘
         │ (bytes)
         ▼
┌─────────────────┐
│ AudioProcessor  │ ◄─── Captura contínua em chunks
│ (pyaudio)       │
└────────┬────────┘
         │ (audio chunk)
         ▼
┌─────────────────┐
│   Transcriber   │ ◄─── Whisper transcreve em thread
│   (Whisper)     │
└────────┬────────┘
         │ (texto)
         ▼
┌──────────────────────┐
│ KeywordDetector      │ ◄─── Busca exatas + variações
└────────┬─────────────┘
         │ (match?)
         ▼
┌──────────────────────┐
│ ContextAnalyzer      │ ◄─── Embeddings + cosine similarity
│ (sentence-trans.)    │
└────────┬─────────────┘
         │ (score > threshold?)
         ▼
┌──────────────────────┐
│ SoundPlayer          │ ◄─── Toca som correspondente
└──────────────────────┘

┌──────────────────────┐
│   WebSocket/API      │ ◄─── Atualiza frontend em tempo real
│  (notifica eventos)  │
└──────────────────────┘

┌──────────────────────┐
│  EventLogger         │ ◄─── Log de tudo em database
└──────────────────────┘
```

---

## 📝 Checklist de Implementação

Veja a seção TODO LIST abaixo para rastreamento detalhado.

---

## 🎯 Metas de Performance

- **Latência de captura**: < 100ms
- **Latência de transcrição**: < 2s (modelo base)
- **Latência de detecção**: < 500ms
- **Consumo de memória**: < 500MB (Whisper base)
- **CPU**: < 30% em repouso, < 70% durante transcrição

---

## 🔒 Segurança

- ✅ Validação de entrada em todos os endpoints
- ✅ CORS configurado restritivamente
- ✅ Nenhum dado sensível em logs
- ✅ Arquivos de som armazenados localmente
- ✅ Config persistida com permissões restritas

---

## 📦 Instalação Rápida

```bash
# Clone ou crie o diretório
mkdir analisador-microfone
cd analisador-microfone

# Crie virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows

# Instale dependências
pip install -r requirements.txt

# Baixe modelo Whisper (ocorre automaticamente)
python -c "import whisper; whisper.load_model('base')"

# Execute
python main.py
```

---

## 🧪 Testing

- Testes unitários para AI e audio
- Testes de integração para API
- Testes de UI no navegador
- Testes de carga (simulação de keywords)

---

## 📚 Referências

- [Whisper Docs](https://github.com/openai/whisper)
- [Sentence Transformers](https://www.sbert.net/)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)

---

## 🎓 Notas de Desenvolvimento

1. **Threads**: Use para captura e processamento separados (não bloqueia UI)
2. **Buffer Circular**: Mantenha sempre os últimos N segundos em memória
3. **Cache de Embeddings**: Reutilize para mesmas frases (otimização)
4. **Config Hot-reload**: Detecte mudanças em tempo real sem reiniciar
5. **Graceful Shutdown**: Finalize threads corretamente ao encerrar

