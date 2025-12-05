# Melhorias no run.sh - Tratamento de Timeout

## 🔧 Problemas Corrigidos

### ❌ Antes
- Script travava esperando `/api/config` indefinidamente
- Se o backend demorasse ou falhasse, o script não continuava
- Sem feedback claro sobre o que estava acontecendo
- Sem verificação se os processos estavam rodando

### ✅ Depois

#### 1. **Melhor Endpoint de Verificação**
```bash
# Antes
if curl -s http://localhost:5000/api/config > /dev/null 2>&1

# Depois
if curl -s http://localhost:5000/api/status > /dev/null 2>&1
```
- `/api/status` é mais simples e rápido que `/api/config`

#### 2. **Verificação de Processo**
```bash
# Verifica se o processo backend ainda está rodando
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend parou inesperadamente"
    tail -20 /tmp/backend.log  # Mostra logs do erro
    exit 1
fi
```

#### 3. **Fallback para Frontend**
```bash
if [ $BACKEND_READY -eq 0 ]; then
    echo "⚠️  Backend não respondeu após 30s"
    echo "Tentando iniciar frontend mesmo assim..."
fi
```
- Frontend é iniciado mesmo se backend demorar
- Permite que o app funcione parcialmente

#### 4. **Timeout Maior para Frontend**
```bash
# Antes: 30s
for i in {1..30}

# Depois: 60s
for i in {1..60}
```
- Frontend geralmente demora mais que backend
- Compilação Next.js pode levar tempo na primeira vez

#### 5. **Variáveis de Sucesso**
```bash
BACKEND_READY=0
FRONTEND_READY=0

# ... verificar

if [ $BACKEND_READY -eq 0 ]; then
    # Mostrar warning sem parar o script
fi
```

---

## 📊 Fluxo de Execução Novo

```
1. Setup (Python, venv, pip, imports, diretórios)
   ↓
2. Iniciar Backend (background)
   ↓
3. Aguardar Backend (máx 30s)
   - Se OK → ✅ "Backend pronto"
   - Se falhar → Mostra logs + ❌ exit
   - Se timeout → ⚠️ "Tentando iniciar frontend mesmo assim"
   ↓
4. Iniciar Frontend (background, web-control)
   ↓
5. Aguardar Frontend (máx 60s)
   - Se OK → ✅ "Frontend pronto"
   - Se falhar → Mostra logs + ❌ exit
   - Se timeout → ⚠️ "Tentando abrir navegador mesmo assim"
   ↓
6. Abrir navegador
   ↓
7. Manter aplicação rodando (while true)
   ↓
8. Ctrl+C → Cleanup (matar processos)
```

---

## 🚀 Como Usar

```bash
./run.sh
```

**Comportamentos:**

1. **Sucesso Total**
   ```
   ✅ Backend pronto em http://localhost:5000
   ✅ Frontend pronto em http://localhost:3000
   ✅ Aplicação pronta!
   🌐 Abrindo interface no navegador...
   ```

2. **Backend Falha Rapidamente**
   ```
   ❌ Backend parou inesperadamente
   Logs:
   [erro details]
   ```

3. **Backend Demora (mas não falha)**
   ```
   ⏳ Aguardando Backend carregar... ......
   ⚠️  Backend não respondeu após 30s
   Tentando iniciar frontend mesmo assim...
   
   🎨 Iniciando Frontend (Next.js)...
   ⏳ Aguardando Frontend carregar... ...
   ✅ Frontend pronto em http://localhost:3000
   ```

---

## 📝 Notas

- **Tempo Backend**: máx 30s (depois tenta frontend mesmo assim)
- **Tempo Frontend**: máx 60s (mais tempo pois compila)
- **Logs**: `/tmp/backend.log` e `/tmp/frontend.log`
- **PIDs**: Mostrados para monitoramento
- **Ctrl+C**: Limpa ambos os processos corretamente

---

## 🔍 Debug

Se algo der errado, verifique:

```bash
# Ver logs do backend
tail -f /tmp/backend.log

# Ver logs do frontend
tail -f /tmp/frontend.log

# Ver processos rodando
ps aux | grep -E "python3|node|npm"
```
