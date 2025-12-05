# 🚀 QUICKSTART - Scripts v2.0

## ⚡ 30 Segundos para Começar

### Linux/Mac
```bash
chmod +x run.sh                    # Tornar executável (uma vez)
./run.sh                            # Pronto! Tudo automático
```

### Windows
```cmd
run.bat                             # Pronto! Tudo automático
```

**Resultado:** Aplicação rodan em http://localhost:5000

---

## 📌 Primeiro Uso - Passo a Passo

### 1️⃣ Clonar o Repositório
```bash
git clone https://github.com/seu-user/Analisador-microfone-gera--o-por-ia.git
cd Analisador-microfone-gera--o-por-ia
```

### 2️⃣ Executar o Script
```bash
# Linux/Mac
./run.sh

# Windows
run.bat
```

### 3️⃣ Deixar Rodar
- ✓ Valida Python
- ✓ Cria venv
- ✓ Instala dependências
- ✓ Baixa modelos (primeira vez: ~15 min)
- ✓ Abre navegador em localhost:5000

**Pronto!** 🎉

---

## 🔧 Se Houver Problema

### Comando Diagnóstico
```bash
# Linux/Mac
./run.sh --diagnose

# Windows
run.bat --diagnose
```

**Mostra:**
- Status do sistema
- Pacotes instalados
- GPU disponível
- Recomendações

### Soluções Comuns

| Problema | Solução |
|----------|---------|
| Python não encontrado | [Baixe Python](https://www.python.org/downloads/) |
| ffmpeg não encontrado | `sudo apt install ffmpeg` |
| Porta 5000 em uso | Feche otra app na porta 5000 |
| Muito lento | Use GPU (instale CUDA 11.8) |
| Download quebrou | Execute novamente: `./run.sh` |

---

## 📚 Próximos Passos

### Próximas Execuções (Rápido)
```bash
# Sem validações (2-3 segundos)
./run.sh --skip-checks

# Com validações (normal)
./run.sh
```

### Reiniciar Limpo
```bash
# Se não conseguir resolver
./run.sh --reinstall

# Depois
./run.sh
```

### Entender Melhor
- Leia: `SCRIPTS_README.md` - Guia completo
- Leia: `SCRIPTS_UPGRADES.md` - O que mudou
- Leia: `SCRIPTS_v2_SUMMARY.md` - Resumo técnico

---

## ⚙️ Opções Avançadas

```bash
# Linux/Mac
./run.sh --help              # Mostra todas as opções
./run.sh --clean             # Limpa cache pip
./run.sh --delete-venv       # Remove venv
./run.sh --skip-checks       # Pula validações

# Windows
run.bat --help              # Mostra todas as opções
run.bat --clean             # Limpa cache pip
run.bat --delete-venv       # Remove venv
run.bat --skip-checks       # Pula validações
```

---

## 📊 Tempos Esperados

| Ação | Tempo |
|------|-------|
| Primeira execução (completo) | 15-30 min |
| Com GPU disponível | 10-15 min |
| Próximas execuções (normal) | 5-10 seg |
| Com --skip-checks | 2-3 seg |
| Diagnóstico completo | 30 seg |

---

## ✅ Checklist de Sucesso

- [ ] Python está instalado
- [ ] Script executou sem erros
- [ ] Navegador abriu em localhost:5000
- [ ] Página carregou
- [ ] Microfone funciona

Se tudo ✓, você está pronto!

---

## 🎓 O que os Scripts Fazem

### run.sh / run.bat
1. Valida Python 3.8+
2. Cria/detecta venv
3. Instala packages de requirements.txt
4. Valida cada package crítico
5. Baixa modelo Whisper
6. Detecta GPU/CUDA
7. Inicia aplicação

### diagnose.sh / diagnose.bat
1. Verifica sistema operacional
2. Testa Python e pip
3. Valida ambiente virtual
4. Testa cada pacote
5. Detecta GPU
6. Verifica modelos
7. Gera relatório

---

## 💡 Dicas

**Para desenvolvimento rápido:**
```bash
./run.sh --skip-checks    # Inicia em 2 segundos
```

**Para debug completo:**
```bash
./run.sh --diagnose       # Vê tudo que está instalado
```

**Para recomeçar:**
```bash
./run.sh --reinstall      # Remove venv e recria
./run.sh                   # Instala tudo novamente
```

**Para limpar cache pip:**
```bash
./run.sh --clean
./run.sh
```

---

## 🆘 Ainda com Problemas?

1. Execute: `./run.sh --diagnose` (ou `run.bat --diagnose`)
2. Leia a saída com atenção
3. Siga as recomendações oferecidas
4. Se precisar, veja `SCRIPTS_README.md` para mais detalhes

---

## 📝 TL;DR

```bash
./run.sh                    # Boom! Tudo funciona
# ou
run.bat                     # Boom! Tudo funciona (Windows)
```

Acesse http://localhost:5000

Pronto! 🚀
