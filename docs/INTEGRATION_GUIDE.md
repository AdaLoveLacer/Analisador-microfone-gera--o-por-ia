# 🔌 Integração Web-Control com Backend Python

## ✅ Feito

1. **`lib/api.ts`** - Cliente HTTP para todas as APIs
   ```typescript
   import { api } from "@/lib/api"
   
   // Exemplos:
   await api.startCapture()
   const keywords = await api.getKeywords()
   await api.createKeyword({ name: "Sus", pattern: "sus" })
   ```

2. **Dashboard** - Conectado com APIs
   - Status da aplicação (GET `/status`)
   - Controle de captura (POST `/capture/start|stop`)
   - LLM status (GET `/llm/status`)
   - Histórico (GET `/history`)

3. **`.env.local`** - Configuração
   ```
   NEXT_PUBLIC_API_URL=http://localhost:5000/api
   NEXT_PUBLIC_WS_URL=http://localhost:5000
   ```

## 🔴 Próximos (Prioridade)

- [ ] Keywords component - Conectar CRUD
- [ ] SoundLibrary component - Upload + GET/DELETE
- [ ] Settings component - GET/POST config
- [ ] History component - GET history com filtros
- [ ] Insights component - Gráficos com dados reais

## 🟡 Depois

- [ ] WebSocket para transcrição live
- [ ] WebSocket para audio levels
- [ ] Export funcionalidade
- [ ] Streaming (OBS) integração

## 🚀 Como Rodar

### Terminal 1 - Backend Python
```bash
cd /home/labubu/Documentos/GitHub/Analisador-microfone-gera--o-por-ia
python main.py
# Roda em http://localhost:5000
```

### Terminal 2 - Frontend Next.js
```bash
cd /home/labubu/Documentos/GitHub/Analisador-microfone-gera--o-por-ia/web-control
npm run dev
# Roda em http://localhost:3000
```

Pronto! Interface conectada! 🎉

