# 🔧 Troubleshooting - Audio Visualization

Se você tiver algum problema com a visualização de áudio, siga este guia.

---

## ❌ Problema: Canvas Não Aparece

### Solução 1: Verificar Console do Navegador
1. Pressione `F12` para abrir o Developer Tools
2. Vá na aba `Console`
3. Procure por erros em vermelho
4. Se vir erro relacionado a `waveform-canvas`, o HTML não foi carregado corretamente

### Solução 2: Verificar HTML
- Abra `web/static/index.html`
- Procure por: `<canvas id="waveform-canvas"`
- Se não existir, o arquivo precisa ser atualizado

### Solução 3: Limpar Cache
1. Pressione `Ctrl + Shift + Delete` (Limpar Cache)
2. Recarregue a página `Ctrl + F5` (Hard Refresh)

---

## ❌ Problema: Canvas Aparece Mas Não Atualiza

### Causa Provável: WebSocket Não Conectado

**Verificar Conexão**:
1. No console (F12), execute:
   ```javascript
   console.log('WebSocket conectado?', socket.connected);
   ```
2. Se output for `false`, WebSocket não está funcionando

### Solução 1: Verificar Servidor
```bash
# Verifique se o servidor está rodando
Get-Process -Name "python" | Select-Object Id, ProcessName
```

Se não houver processo Python, inicie:
```bash
cd "g:\VSCODE\Analisador-microfone-geração-por-ia"
.\venv\Scripts\Activate.ps1
python web/app.py
```

### Solução 2: Verificar URL do Servidor
No console do navegador (F12):
```javascript
console.log('Conectado a:', socket.io.uri);
```

Deve retornar algo como: `http://localhost:5000/socket.io/?...`

### Solução 3: Reiniciar Servidor
```bash
# Parar todos os processos Python
Get-Process -Name "python" | Stop-Process -Force

# Aguardar 2 segundos
Start-Sleep -Seconds 2

# Reiniciar
python web/app.py
```

---

## ❌ Problema: "Received 0 audio level updates" (Teste falhou)

### Causa Provável: Microfone Não Respondendo

**Verificar Microfone**:
1. Abra `Settings` → `Sound`
2. Verifique se algum microfone está ativo
3. Tente falar ou fazer barulho próximo ao microfone

### Solução 1: Testar Captura
```bash
python test_audio_level_callback.py
```

Se receber erro `ModuleNotFoundError`, execute:
```bash
$env:PYTHONPATH="g:\VSCODE\Analisador-microfone-geração-por-ia"
```

### Solução 2: Selecionar Dispositivo Correto
1. Acesse http://localhost:5000
2. Vá em "Settings" (Configurações)
3. Na seção "Audio Devices", selecione outro dispositivo
4. Tente novamente

### Solução 3: Aumentar Volume
- Verifique se o microfone não está silenciado
- Aumente o volume na seção de "Sound Settings" do Windows

---

## ❌ Problema: Servidor Não Inicia

### Erro: ModuleNotFoundError

**Solução**:
```bash
cd "g:\VSCODE\Analisador-microfone-geração-por-ia"
$env:PYTHONPATH="g:\VSCODE\Analisador-microfone-geração-por-ia"
.\venv\Scripts\python.exe web/app.py
```

### Erro: Address already in use

**Causa**: Porta 5000 já está em uso

**Solução**:
```bash
# Parar processos em uso
Get-Process -Name "python" | Stop-Process -Force

# Aguardar
Start-Sleep -Seconds 3

# Reiniciar
python web/app.py
```

### Erro: RuntimeError: Click will abort

**Solução**: Execute com ambiente preparado:
```bash
.\venv\Scripts\Activate.ps1
python web/app.py
```

---

## ❌ Problema: Canvas Atualiza Muito Rápido/Lento

### Muito Rápido (Parece quebrado)
- Isso é normal no início (muitos eventos)
- O visualizador usa `requestAnimationFrame` que limita a 60 FPS
- Se continuar anormalmente, verifique a aba `Performance` do DevTools

### Muito Lento (Lag)
1. Feche outras abas do navegador
2. Limpe cache: `Ctrl + Shift + Delete`
3. Tente em outro navegador (Chrome/Edge/Firefox)

---

## ✅ Verificação Rápida (Tudo Certo?)

Execute este checklist:

- [ ] Servidor rodando: `http://localhost:5000` acessível
- [ ] Console sem erros: F12 → Console (sem mensagens vermelhas)
- [ ] WebSocket conectado: `socket.connected === true`
- [ ] Microfone funcionando: Fale próximo ao mic
- [ ] Canvas visível: Verde/amarelo/vermelho aparecendo

Se todos estiverem ✓, está tudo funcionando! 🎉

---

## 📊 Teste Completo

Para fazer um teste completo do sistema:

```bash
# Terminal 1: Iniciar servidor
cd "g:\VSCODE\Analisador-microfone-geração-por-ia"
.\venv\Scripts\Activate.ps1
python web/app.py

# Terminal 2 (em paralelo): Testar callbacks
python test_audio_level_callback.py

# Terminal 3: Verificar processos
Get-Process -Name "python" | Select-Object Id, ProcessName
```

**Resultado esperado**:
- Terminal 1: Servidor rodando sem erros
- Terminal 2: "✅ SUCCESS: Received X audio level updates"
- Terminal 3: Mínimo 2 processos Python

---

## 🆘 Problema Não Listado?

Se o problema não está aqui:

1. **Verifique os logs do servidor**:
   - Mensagens aparecem no Terminal onde você rodou `python web/app.py`
   - Procure por mensagens de erro em vermelho

2. **Verifique o console do navegador**:
   - F12 → Console
   - F12 → Network (veja WebSocket status)

3. **Teste a API manualmente**:
   ```bash
   curl http://localhost:5000/api/status
   ```

---

## 📞 Informações de Debug

Quando reportar um problema, inclua:

```javascript
// Execute no console (F12) e copie o output:
console.log({
    "connected": socket.connected,
    "uri": socket.io.uri,
    "navigator.userAgent": navigator.userAgent,
    "window.waveformVisualizer": window.waveformVisualizer ? 'exists' : 'missing'
});
```

Isso ajuda a diagnosticar o problema mais rápido!

---

**Última atualização**: 29 de Novembro de 2025
