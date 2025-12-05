# 🎨 Prompt para V0 - Interface Gráfica do Analisador de Microfone

## COPIE E COLE ISTO NO V0:

---

Crie uma interface web moderna e intuitiva para um **Analisador de Microfone com IA** que funciona em tempo real. O projeto é um soundboard inteligente que detecta palavras-chave em áudio do microfone e toca efeitos sonoros automaticamente.

### 📋 Funcionalidades Principais:

1. **Dashboard Principal**
   - Botão grande "Iniciar Captura" / "Parar Captura" (com toggle visual)
   - Indicador de nível de áudio em tempo real (barra verde dinâmica)
   - Transcription em tempo real (live text feed)
   - Lista de detecções recentes (ultimas 5 com timestamp)
   - Status do backend de IA (Ollama / Transformers / Fallback)

2. **Abas Laterais (Tab Navigation)**
   - **Dashboard** (home)
   - **Palavras-Chave** (gerenciar keywords)
   - **Biblioteca de Sons** (upload e gerenciar sons)
   - **Configurações** (áudio, IA, visual)
   - **Histórico** (timeline de detecções)

3. **Seção de Palavras-Chave**
   - Tabela com todas as keywords (nome, padrão, variações, contexto, ativo/inativo)
   - Botão "+ Nova Palavra-Chave" abre modal
   - Modal com campos: Nome, Padrão, Variações (chips), Contexto (chips), Som associado (dropdown), Peso (slider)
   - Botões inline: Editar, Deletar, Testar
   - Toggle para ativar/desativar cada keyword
   - Busca/filtro para encontrar keywords

4. **Biblioteca de Sons**
   - Grid de cards com preview dos sons
   - Cada card mostra: thumbnail, nome, duração, volume, ações
   - Upload drag-and-drop para adicionar novos sons
   - Botões: Reproduzir, Editar, Deletar
   - Modal de edição: nome, volume, categoria

5. **Configurações**
   - **Áudio**: Device selector (dropdown), Sample rate, Sensibilidade (slider)
   - **Whisper**: Modelo (tiny/base/small), Idioma, Threshold de confiança
   - **IA**: Toggle para análise de contexto, Backend preferido, Temperatura (slider)
   - **Visual**: Tema (light/dark), Idioma, Refresh rate
   - Botão "Salvar" com feedback visual

6. **Histórico**
   - Timeline vertical com todas as detecções
   - Cada entry mostra: timestamp, texto transcrito, keyword detectada, confiança, som tocado
   - Filtros: por data, por keyword, por confiança
   - Botão export CSV/JSON
   - Gráfico de estatísticas (palavras mais detectadas)

### 🎨 Design & UX:

- **Tema**: Dark mode como padrão, toggle para light mode
- **Cores**: Neon/cyberpunk (roxo, azul, rosa, verde limão)
- **Animações**: Smooth transitions, pulsing indicators para eventos
- **Responsivo**: Desktop first, mas mobile-friendly
- **Icons**: Use Lucide icons para ícones
- **Font**: Geist ou Inter para texto moderno

### 🔄 Integrações via API (local):

Connect em http://localhost:5000/api:
- GET `/status` - Status da aplicação
- POST `/capture/start` - Iniciar captura
- POST `/capture/stop` - Parar captura
- GET `/keywords` - Listar palavras-chave
- POST `/keywords` - Criar nova
- PUT `/keywords/{id}` - Editar
- DELETE `/keywords/{id}` - Deletar
- GET `/sounds` - Listar sons
- POST `/sounds/upload` - Upload (multipart)
- POST `/sounds/{id}/preview` - Tocar preview
- GET `/config` - Configurações
- POST `/config` - Salvar config
- GET `/llm/status` - Status do LLM
- POST `/llm/generate` - Gerar com IA
- GET `/history` - Histórico

### ✨ Bonus Features (se tiver tempo):

- WebSocket em tempo real para atualizar stats
- Notificações desktop quando detecta keyword
- Gravação de clips quando detecta algo (3 segundos antes/depois)
- Presets salvos de configurações
- Keyboard shortcuts (Space = start/stop, etc)
- Visualizador de áudio (waveform em tempo real)

### 🎯 Importante:

- Faça bonito! Esse projeto vai impressionar people!
- Use componentes reutilizáveis (Button, Modal, Card, etc)
- Adicione loader/skeleton durante conexão
- Error handling com toasts amigáveis
- Feedback visual para todas as ações

---

## 🚀 DICAS EXTRAS:

1. **Estados**: Idle, Capturing, Processing, Detected (com cores diferentes)
2. **Animações de detecção**: Pulse effect quando detecta algo
3. **Soundboard visual**: Teclado customizável que apareça na interface
4. **Dark magic**: Glitch effects quando toca som (opcional, mas ficaria daora!)
5. **Mobile view**: Botões maiores, menos detalhes, design touch-friendly

---

Boa sorte! 🎉
