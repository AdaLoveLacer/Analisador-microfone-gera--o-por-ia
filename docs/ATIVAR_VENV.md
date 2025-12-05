# 🔧 Como Ativar Ambiente Virtual (venv)

## ⚠️ IMPORTANTE - Você Tentou Errado!

```powershell
# ❌ ERRADO (SyntaxError):
python .\.venv\Scripts\Activate.ps1
python .\.venv\Scripts\activate.bat

# ✅ CORRETO para PowerShell:
.\.venv\Scripts\Activate.ps1

# ✅ CORRETO para Command Prompt (cmd):
.\.venv\Scripts\activate.bat
```

**Por que deu erro?**
- Você tentou executar scripts com `python`
- Mas `activate.ps1` e `activate.bat` são scripts do SO, não Python!
- Resultado: Python tentou interpretá-los como código Python → SyntaxError

---

## ✅ Formas Corretas

### 🪟 Windows (PowerShell)

```powershell
# Opção 1: Usar run.bat (RECOMENDADO)
run.bat

# Opção 2: Ativar manualmente
.\.venv\Scripts\Activate.ps1

# Se der erro de permissões, execute como Admin e faça:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 🪟 Windows (Command Prompt / cmd)

```cmd
# Opção 1: Usar run.bat (RECOMENDADO)
run.bat

# Opção 2: Ativar manualmente
.\.venv\Scripts\activate.bat
```

### 🐧 Linux / 🍎 macOS

```bash
# Opção 1: Usar run.sh (RECOMENDADO)
bash run.sh

# Opção 2: Ativar manualmente
source venv/bin/activate

# OU
. venv/bin/activate
```

---

## 🎯 Verificar se Funcionou

Depois de ativar, você deve ver o nome da venv no prompt:

```powershell
# PowerShell (Windows)
(.venv) PS G:\VSCODE\Analisador-microfone-geração-por-ia>
     ↑ Vem de (.venv)

# Command Prompt (Windows)
(.venv) C:\Users\...>

# Linux/Mac
(.venv) user@computer:~$
```

---

## 📋 Passo a Passo

### Windows (PowerShell)

```powershell
# 1. Navegue até a pasta do projeto
cd G:\VSCODE\Analisador-microfone-geração-por-ia

# 2. Ative a venv
.\.venv\Scripts\Activate.ps1

# 3. Você deve ver (.venv) no prompt
# Se não vir, erro de permissões:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 4. Tente novamente
.\.venv\Scripts\Activate.ps1

# 5. Verifique Python
python --version
```

### Windows (Command Prompt)

```cmd
REM 1. Navegue até a pasta do projeto
cd G:\VSCODE\Analisador-microfone-geração-por-ia

REM 2. Ative a venv
.\.venv\Scripts\activate.bat

REM 3. Você deve ver (.venv) no prompt

REM 4. Verifique Python
python --version
```

### Linux/Mac

```bash
# 1. Navegue até a pasta do projeto
cd ~/Analisador-microfone-geração-por-ia

# 2. Ative a venv
source venv/bin/activate

# 3. Você deve ver (venv) no prompt

# 4. Verifique Python
python3 --version
```

---

## 🐛 Se Ainda Não Funcionar

### Erro: "PowerShell is not allowed to run scripts"

**Solução**:
```powershell
# Execute como Admin
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Tente novamente
.\.venv\Scripts\Activate.ps1
```

### Erro: "venv not found"

**Solução**:
```powershell
# Recrie a venv
python -m venv .venv

# Ative
.\.venv\Scripts\Activate.ps1
```

### Erro: ".venv/Scripts/ não encontrado"

**Solução**:
```powershell
# Verifique se existe
ls .venv/Scripts/

# Se não existe, crie:
python -m venv .venv
```

---

## 🎯 Usar o Script (RECOMENDADO)

```bash
# Windows
run.bat

# Linux/Mac
bash run.sh
```

**O script faz tudo automaticamente:**
- ✅ Verifica Python
- ✅ Cria venv se não existir
- ✅ Ativa venv
- ✅ Instala dependências
- ✅ Abre navegador
- ✅ Inicia aplicação

---

## 💡 Dicas

### Desativar venv
```bash
deactivate
```

### Mudar nome de venv
Se criou `.venv` mas precisa de `venv`:
```bash
mv .venv venv
```

### Ver qual Python está ativo
```bash
which python      # Linux/Mac
where python      # Windows
```

### Deletar venv
```bash
# Windows
rmdir /s .venv

# Linux/Mac
rm -rf venv
```

---

## 🚀 Agora Tente Novamente

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python --version

# Linux/Mac
source venv/bin/activate
python3 --version
```

✅ **Deve funcionar agora!**

---

**Se ainda tiver problemas**: Veja [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
