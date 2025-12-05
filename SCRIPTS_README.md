# 📋 Scripts de Inicialização - Versão 2.0

## Resumo das Melhorias

Os scripts `run.sh` (Linux/Mac) e `run.bat` (Windows) foram completamente reescritos com validações completas e automáticas para **garantir que o projeto seja levantado com sucesso na primeira execução**.

### ✅ Funcionalidades Adicionadas

#### 1. **Validações Completas Automáticas**
- ✓ Verifica existência de Python 3.8+
- ✓ Cria venv automaticamente se não existir
- ✓ Atualiza pip automaticamente
- ✓ Valida cada pacote crítico em requirements.txt
- ✓ Identifica pacotes faltando e os instala
- ✓ Baixa modelos AI (Whisper, Phi-2) automaticamente
- ✓ Detecta GPU/CUDA disponível

#### 2. **Validações do Sistema**
- ✓ Verifica dependências de sistema (ffmpeg, portaudio, ALSA)
- ✓ Valida espaço em disco
- ✓ Verifica portas disponíveis (5000, 3000)
- ✓ Detecta e relata problemas específicos

#### 3. **Novas Opções de Linha de Comando**

##### Linux/Mac (`./run.sh`)
```bash
./run.sh              # Inicia com validações completas
./run.sh --diagnose  # Executa diagnóstico completo
./run.sh --clean     # Limpa cache do pip
./run.sh --reinstall # Reinstala tudo do zero
./run.sh --delete-venv # Remove venv
./run.sh --skip-checks # Inicia direto (não recomendado)
./run.sh --help      # Mostra ajuda
```

##### Windows (`run.bat`)
```cmd
run.bat              # Inicia com validações completas
run.bat --diagnose  # Executa diagnóstico completo
run.bat --clean     # Limpa cache do pip
run.bat --reinstall # Reinstala tudo do zero
run.bat --delete-venv # Remove venv
run.bat --skip-checks # Inicia direto (não recomendado)
run.bat --help      # Mostra ajuda
```

---

## 🔧 Fluxo de Execução

### Primeiro Uso (Automático)
```
1. Verifica Python (instala se precisar)
    ↓
2. Detecta/Cria venv
    ↓
3. Ativa venv e atualiza pip
    ↓
4. Valida requirements.txt (instala faltantes)
    ↓
5. Baixa modelo Whisper (140 MB) se precisar
    ↓
6. Detecta GPU/CUDA disponível
    ↓
7. Cria diretórios necessários
    ↓
8. Inicia aplicação em localhost:5000
```

### Execuções Subsequentes (Rápido)
```
1. Verifica se venv existe ✓
2. Ativa venv ✓
3. Valida requirements (já instalados) ✓
4. Inicia aplicação (2 segundos)
```

---

## 📊 Diagnóstico Completo

### `./diagnose.sh` (Linux/Mac)

Executa verificações detalhadas do sistema e salva relatório.

**Verifica:**
- Sistema operacional
- Dependências do sistema (ffmpeg, portaudio, ALSA)
- Python versão e pip
- Ambiente virtual
- Pacotes Python críticos
- GPU/CUDA disponível
- Modelos AI em cache
- Espaço em disco
- Arquivos de configuração
- Portas disponíveis

**Saída Exemplo:**
```
🔍 ffmpeg ... ✓ PASSOU
🔍 PortAudio ... ✓ PASSOU
🔍 Python 3 ... ✓ 3.11.0
🔍 GPU (CUDA) disponível ... ✓
   GPU: NVIDIA RTX 4090
   VRAM: 24.0GB
...

✓ Sistema pronto para usar!
Execute: ./run.sh
```

### `diagnose.bat` (Windows)

Versão Windows com verificações adaptadas para CMD.

**Verifica:**
- Sistema operacional
- Python e pip
- Ambiente virtual
- Pacotes Python críticos
- GPU/CUDA
- Modelos AI
- Arquivos necessários
- Diretórios
- Portas

---

## 🎯 Caso de Uso: Primeira Configuração

### Linux/Mac
```bash
# Primeiro, diagnosticar (opcional)
./diagnose.sh

# Depois, iniciar
./run.sh

# Se houver problemas
./run.sh --diagnose
```

### Windows
```cmd
# Primeiro, diagnosticar (opcional)
diagnose.bat

# Depois, iniciar
run.bat

# Se houver problemas
run.bat --diagnose
```

---

## 🔍 Resolução de Problemas

### Python não encontrado
**Linux/Mac:**
```bash
sudo apt install python3 python3-venv  # Ubuntu/Debian
brew install python3  # macOS
```

**Windows:**
- Baixe de https://www.python.org/downloads/
- **IMPORTANTE**: Marque "Add Python to PATH" durante instalação

### ffmpeg/PortAudio não encontrado
**Linux:**
```bash
sudo apt install ffmpeg portaudio19-dev libasound2-dev
```

**macOS:**
```bash
brew install ffmpeg portaudio
```

### GPU/CUDA não detectada
- Instale NVIDIA Driver mais recente
- Instale CUDA 11.8 Toolkit
- Execute o script novamente

### Espaço em disco insuficiente
- Modelos AI precisam ~4GB
- Whisper + Phi-2 = 3.8GB + 140MB
- Crie 20GB de espaço antes de iniciar

---

## 📝 Logs e Relatórios

Os scripts criam logs automáticos:
```
logs/
├── app.log          # Log da aplicação
├── errors.log       # Erros específicos
└── setup.log        # Log de setup (novo)
```

---

## 🚀 Performance

### Tempos Típicos

| Cenário | Tempo |
|---------|-------|
| Primeira execução (full setup) | 15-30 min |
| Com GPU disponível | 10-15 min |
| Execuções subsequentes | 2-3 seg |
| Diagnóstico completo | 30 seg |

---

## ⚙️ Variáveis de Ambiente (Opcional)

```bash
# Linux/Mac
export SKIP_GPU_CHECK=1      # Pula verificação GPU
export SKIP_MODEL_DOWNLOAD=1 # Pula download de modelos
export PYTHON_VERSION=3.11   # Force Python version

# Windows
set SKIP_GPU_CHECK=1
set SKIP_MODEL_DOWNLOAD=1
set PYTHON_VERSION=3.11
```

---

## 🔧 Desenvolvimento

Se você quer modificar os scripts:

**run.sh** (1500 linhas)
- Funções de validação modulares
- Fácil adicionar novos checks
- Compatível com bash e zsh

**run.bat** (600 linhas)
- Estrutura de labels (goto)
- Fácil adicionar novos checks
- Compatível com cmd.exe

**diagnose.sh** e **diagnose.bat**
- Independentes dos scripts principais
- Podem ser executados separadamente
- Não causam mudanças no sistema

---

## 📌 Checklist de Funcionalidades

- [x] Validar Python 3.8+
- [x] Criar venv automaticamente
- [x] Instalar requirements.txt
- [x] Validar pacotes críticos
- [x] Baixar modelo Whisper
- [x] Validar Phi-2 (transformers)
- [x] Detectar GPU/CUDA
- [x] Criar diretórios necessários
- [x] Suportar --diagnose
- [x] Suportar --clean
- [x] Suportar --reinstall
- [x] Suportar --skip-checks
- [x] Documentação completa
- [x] Scripts Windows e Linux
- [x] Tratamento de erros robusto

---

## 📞 Suporte

Se o script falhar:

1. Execute diagnóstico: `./run.sh --diagnose` ou `run.bat --diagnose`
2. Verifique a saída de erro
3. Siga as instruções oferecidas
4. Execute novamente: `./run.sh` ou `run.bat`

Se persistir, verifique:
- Python está no PATH
- Espaço em disco (mínimo 20GB)
- Conexão de internet (para downloads)
- Permissões de arquivo

---

## 🎓 Aprendizado

Estes scripts demonstram:
- Validação robusta de dependências
- Instalação automática de requirements
- Detecção de hardware (GPU)
- Tratamento de erros inteligente
- Suporte multiplataforma (Linux, macOS, Windows)
- Automação completa de setup

Use-os como referência para seus próprios projetos!
