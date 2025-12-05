# 🎤 AI Microphone Analyzer - Soundboard Inteligente

Uma interface web moderna e intuitiva para análise de microfone com IA em tempo real. Detecta palavras-chave em áudio do microfone e toca efeitos sonoros automaticamente.

## ✨ Funcionalidades Principais

### 🎯 Dashboard
- **Controle de Captura**: Botão de start/stop com indicadores visuais pulsantes
- **Nível de Áudio em Tempo Real**: Barra de progresso dinâmica com efeitos glow
- **Transcrição ao Vivo**: Feed de texto com cursor animado
- **Detecções Recentes**: Últimas 5 keywords detectadas com timestamps e confiança
- **Status do Sistema**: Informações sobre backend IA, modelo Whisper e keywords ativas

### 🔑 Gerenciamento de Keywords
- Tabela completa com todas as keywords (nome, padrão, variações, contexto)
- Modal de criação/edição com campos avançados
- Sistema de variações e contexto com badges
- Toggle para ativar/desativar individualmente
- Busca e filtros
- Teste de keywords em tempo real

### 🎵 Biblioteca de Sons
- Grid visual de cards com preview
- Upload drag-and-drop de arquivos de áudio
- Waveform placeholder visual
- Controles de volume e categoria
- Player integrado para preview
- Gerenciamento completo (editar, deletar)

### 📊 Insights e Análise
- **Estatísticas em Tempo Real**: Total de detecções, média por hora, taxa de acerto
- **Gráficos Interativos**:
  - Linha temporal de detecções semanais
  - Barras de padrão de uso por hora
  - Pizza de distribuição por categoria
- **Heatmap Semanal**: Mapa de calor por dia e período
- **Top Keywords**: Ranking das palavras mais detectadas com tendências
- **Insights Avançados**: Análise de padrões e comportamento

### 🏆 Gamificação
- **Sistema de Níveis**: XP, progressão e ranks
- **Conquistas**: 45+ achievements com raridades (common, rare, epic, legendary)
- **Leaderboard**: Ranking de keywords mais usadas
- **Desafios**: Diários, semanais e mensais com recompensas
- **Streak System**: Contador de dias consecutivos
- **Badges e Títulos**: Sistema de recompensas visuais

### 📡 Integração com Streaming
- **OBS WebSocket**: Controle de cenas, fontes e filtros
- **Streamer.bot**: Envio de alertas para Twitch/YouTube chat
- **Auto Scene Switching**: Mude cenas baseado em keywords
- **Filter Effects**: Ative filtros temporários automaticamente
- **Chat Alerts**: Mensagens automáticas com cooldown
- **Ações Automáticas**: Vincule keywords a ações de streaming

### 🎙️ Comandos de Voz Avançados
- **Comandos de Sistema**: Volume up/down, mute, controles básicos
- **Comandos de App**: Start/stop capture, navegação, configurações
- **Macros Complexas**: Execute múltiplas ações com um comando
- **Teclado/Mouse**: Simule teclas e cliques por voz
- **Hotword Detection**: Ativação por palavra-chave
- **Feedback Sonoro**: Confirmação auditiva de comandos

### 🧠 Treinamento de IA Personalizado
- **Fine-tuning**: Treine o modelo com suas gravações
- **Datasets Customizados**: Crie e gerencie conjuntos de dados
- **Sons Não-Verbais**: Detecte risadas, tosse, suspiros automaticamente
- **Variações de Sotaque**: Suporte multi-sotaque e pronúncia
- **Métricas de Qualidade**: Acompanhe acurácia e confiança
- **Export/Import**: Compartilhe modelos treinados

### ⚙️ Configurações Avançadas

#### 🎤 Áudio
- Seleção de dispositivo de entrada
- Taxa de amostragem configurável (8-48 kHz)
- Sensibilidade de detecção ajustável
- Redução de ruído automática
- Ganho automático (AGC)

#### 🗣️ Whisper
- Seleção de modelo (tiny, base, small, medium)
- Idioma configurável (PT, EN, ES, auto-detect)
- Threshold de confiança ajustável
- Otimizações de processamento

#### 🤖 IA
- Toggle de análise de contexto
- Backend preferido (Ollama, Transformers, Fallback)
- Temperatura de geração
- Timeout de processamento

#### ⚡ Performance
- **Buffer Size**: Configurável (256-2048 ms)
- **Modo Low-Latency**: Reduz latência
- **GPU Acceleration**: Usa GPU para processamento
- **Cache Inteligente**: Armazena transcrições
- **Multi-threading**: 1-8 threads configuráveis

#### 🎨 Visual
- Tema dark/light (cyberpunk por padrão)
- Idioma da interface
- Taxa de atualização
- Toggle de animações
- Efeitos de glitch

### 📜 Histórico
- Timeline completa de todas as detecções
- Filtros por data, keyword e confiança
- Export para CSV/JSON
- Gráficos de estatísticas
- Busca avançada

## 🎨 Design

### Tema Cyberpunk/Neon
- **Cores**: Roxo (primary), Azul (secondary), Rosa (accent), Verde limão (success)
- **Efeitos**: Glow, pulse, smooth transitions
- **Animações**: Feedback visual em todas as ações
- **Responsivo**: Desktop first, mobile-friendly

### Componentes UI
- Baseado em **shadcn/ui** com Radix UI
- **Lucide Icons** para ícones modernos
- **Recharts** para gráficos interativos
- **Sonner** para notificações toast
- **Tailwind CSS v4** para estilização

## 🔌 Integração com API

Conecta-se ao backend Python via `http://localhost:5000/api`:

### Endpoints Disponíveis

#### Status e Controle
- `GET /status` - Status da aplicação
- `POST /capture/start` - Iniciar captura
- `POST /capture/stop` - Parar captura

#### Keywords
- `GET /keywords` - Listar palavras-chave
- `POST /keywords` - Criar nova
- `PUT /keywords/{id}` - Editar
- `DELETE /keywords/{id}` - Deletar

#### Sons
- `GET /sounds` - Listar sons
- `POST /sounds/upload` - Upload (multipart)
- `POST /sounds/{id}/preview` - Tocar preview

#### Configurações
- `GET /config` - Configurações
- `POST /config` - Salvar config

#### IA
- `GET /llm/status` - Status do LLM
- `POST /llm/generate` - Gerar com IA

#### Histórico
- `GET /history` - Histórico de detecções

## 🚀 Como Usar

1. **Instale as dependências**:
\`\`\`bash
npm install
\`\`\`

2. **Inicie o servidor de desenvolvimento**:
\`\`\`bash
npm run dev
\`\`\`

3. **Certifique-se que o backend está rodando**:
\`\`\`bash
# O backend Python deve estar em http://localhost:5000
\`\`\`

4. **Acesse a aplicação**:
\`\`\`
http://localhost:3000
\`\`\`

## 📦 Tecnologias

- **Next.js 16** - Framework React com App Router
- **React 19.2** - Biblioteca UI
- **TypeScript** - Type safety
- **Tailwind CSS v4** - Estilização
- **SWR** - Data fetching e caching
- **Recharts** - Gráficos interativos
- **shadcn/ui** - Componentes UI
- **Lucide Icons** - Ícones modernos
- **Sonner** - Toast notifications

## 🎯 Estrutura do Projeto

\`\`\`
├── app/
│   ├── layout.tsx          # Layout principal com tema
│   ├── page.tsx            # Página principal com navegação
│   └── globals.css         # Estilos globais e tema cyberpunk
├── components/
│   ├── dashboard.tsx       # Dashboard principal
│   ├── keywords.tsx        # Gerenciamento de keywords
│   ├── sound-library.tsx   # Biblioteca de sons
│   ├── insights.tsx        # Análise e gráficos
│   ├── gamification.tsx    # Sistema de conquistas
│   ├── streaming-integration.tsx  # OBS e Streamer.bot
│   ├── voice-commands.tsx  # Comandos de voz
│   ├── ai-training.tsx     # Treinamento de IA
│   ├── settings.tsx        # Configurações
│   ├── history.tsx         # Histórico
│   ├── sidebar.tsx         # Navegação lateral
│   └── ui/                 # Componentes shadcn/ui
└── lib/
    └── utils.ts            # Funções utilitárias

\`\`\`

## 🌟 Destaques

- **Interface Cyberpunk**: Design moderno com cores neon e efeitos glow
- **Tempo Real**: Atualizações instantâneas via SWR
- **Análise Profunda**: Gráficos, heatmaps e insights detalhados
- **Gamificação Completa**: Conquistas, ranking e desafios
- **Streaming Ready**: Integração nativa com OBS e plataformas
- **IA Personalizável**: Treine o modelo com sua voz
- **Performance**: Cache inteligente e GPU acceleration
- **Acessibilidade**: Comandos de voz e atalhos de teclado

## 📝 Licença

MIT License - Sinta-se livre para usar e modificar!

---

**Desenvolvido com 💜 usando Next.js, React e Tailwind CSS**
