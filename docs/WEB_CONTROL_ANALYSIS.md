# 📊 Análise Web-Control vs Projeto Python

## ✅ O que Está Ótimo (Usar como está)

1. **Dashboard**
   - ✅ UI bem estruturada com Radix-UI
   - ✅ Cards informativos
   - ✅ Botão Start/Stop captura
   - ✅ Audio level visualization
   - ✅ Recent detections list

2. **Keywords Management**
   - ✅ Tabela com busca/filtro
   - ✅ Modal para criar/editar
   - ✅ Toggle ativo/inativo
   - ✅ Chips para variações e contexto
   - ✅ Weight slider (0-1)

3. **Settings**
   - ✅ Abas bem organizadas (Audio, Whisper, IA, Performance, Visual)
   - ✅ Sliders para valores numéricos
   - ✅ Select dropdowns para seleções

4. **Sidebar Navigation**
   - ✅ Menu lateral limpo
   - ✅ 10 abas bem pensadas

## ⚠️ O que Precisa Ajustar

### 1. **Componentes Extras (Remover/Simplificar)**
- ❌ Gamification (não faz sentido no projeto)
- ❌ Streaming Integration (não é foco)
- ❌ Voice Commands (fora do escopo)
- ❌ AI Training (complexo demais agora)

**Ação:** Remover essas 4 abas da sidebar

### 2. **API Integration (Conectar com Python Backend)**

**Problema Atual:** Dados são mockados/simulados

**O que fazer:**
```tsx
// Conectar com http://localhost:5000/api
- GET /status → status da app
- POST /capture/start → toggle captura
- GET /keywords → listar keywords
- POST /keywords → criar
- PUT /keywords/{id} → editar
- DELETE /keywords/{id} → deletar
- GET /sounds → listar sons
- POST /sounds/upload → upload (multipart)
- GET /config → carregar config
- POST /config → salvar config
- GET /llm/status → status da IA
```

### 3. **Sound Library**
**Adicionar:**
- Upload drag-and-drop (multipart/form-data)
- Preview player para cada som
- Volume control por som

### 4. **WebSocket em Tempo Real**
**Falta conectar:**
```tsx
// Para atualizar em tempo real:
- Transcrição ao vivo (via socket)
- Detecções instantâneas (via socket)
- Níveis de áudio (via socket)
```

### 5. **History Component**
**Adicionar:**
- Conexão com `/history` endpoint
- Timeline vertical
- Filtros por data/keyword/confiança
- Export CSV/JSON

### 6. **Insights Component**
**Adicionar:**
- Gráficos de keywords mais detectadas
- Gráfico de confiança ao longo do tempo
- Estatísticas gerais

## 🔧 Prioridade de Ajustes

### 🔴 CRÍTICO (Fazer Agora)
1. [ ] Remover Gamification, Streaming, Voice Commands, AI Training
2. [ ] Conectar Dashboard com `/capture/start` e `/capture/stop`
3. [ ] Conectar Keywords com `/keywords` CRUD
4. [ ] Conectar Settings com `/config` GET/POST
5. [ ] Conectar Sound Library com `/sounds` GET e upload

### 🟠 IMPORTANTE (Próximo)
1. [ ] WebSocket para transcrição live
2. [ ] WebSocket para audio levels
3. [ ] History com dados reais
4. [ ] Insights com gráficos reais

### 🟡 LEGAL TER (Depois)
1. [ ] Export funcionalidade
2. [ ] Presets de configuração
3. [ ] Keyboard shortcuts
4. [ ] Notificações desktop

## 📝 Mapeamento de Endpoints

```
Web-Control                    ↔ Python Backend (localhost:5000)

Dashboard
├─ Start/Stop              → POST /api/capture/start|stop
├─ Status                  → GET /api/status
└─ Detections              → WebSocket ou GET /api/history

Keywords Tab
├─ List                    → GET /api/keywords
├─ Create                  → POST /api/keywords
├─ Edit                    → PUT /api/keywords/{id}
├─ Delete                  → DELETE /api/keywords/{id}
└─ Test                    → POST /api/test/keyword/{id}

Sounds Tab
├─ List                    → GET /api/sounds
├─ Upload                  → POST /api/sounds (multipart)
├─ Preview                 → POST /api/sounds/{id}/preview
└─ Delete                  → DELETE /api/sounds/{id}

Settings Tab
├─ Get Config             → GET /api/config
├─ Save Config            → POST /api/config
├─ Audio Devices          → GET /api/devices
└─ Whisper Devices        → GET /api/whisper-devices

History Tab
├─ Get History            → GET /api/history?limit=100
└─ Export                 → GET /api/history/export?format=csv|json

LLM Integration
├─ Status                 → GET /api/llm/status
├─ Generate               → POST /api/llm/generate
└─ Analyze Context        → POST /api/llm/analyze-context
```

## 🚀 Próximos Passos

1. **Sessão 1:** Remover componentes extras + conectar APIs críticas
2. **Sessão 2:** WebSocket + History + Insights
3. **Sessão 3:** Polish + Features bonus

