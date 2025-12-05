#!/bin/bash
# ============================================================
# WATCHDOG - Monitor e Auto-Restart do Backend
# ============================================================
# Monitora a saúde do backend e reinicia automaticamente
# se detectar travamento ou crash.
#
# Uso:
#   bash watchdog.sh start   - Inicia o watchdog em background
#   bash watchdog.sh stop    - Para o watchdog
#   bash watchdog.sh status  - Verifica se o watchdog está rodando
#   bash watchdog.sh logs    - Mostra os logs do watchdog
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configurações
WATCHDOG_PID_FILE="/tmp/watchdog.pid"
WATCHDOG_LOG="/tmp/watchdog.log"
BACKEND_LOG="/tmp/backend.log"
BACKEND_URL="http://localhost:5000/api/status"
CHECK_INTERVAL=3           # Segundos entre cada verificação
UNHEALTHY_THRESHOLD=3      # Quantas verificações falhas para reiniciar
RESTART_COOLDOWN=30        # Segundos mínimos entre reinícios
MAX_RESTARTS=5             # Máximo de reinícios antes de desistir
RESTART_WINDOW=300         # Janela de tempo em segundos para contar reinícios

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    # Para o arquivo de log, sem cores
    echo "[$timestamp] $1" | sed 's/\x1b\[[0-9;]*m//g' >> "$WATCHDOG_LOG"
    # Para o terminal, com cores
    echo -e "[$timestamp] $1"
}

log_info() {
    log "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    log "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    log "${RED}[ERROR]${NC} $1"
}

log_success() {
    log "${GREEN}[OK]${NC} $1"
}

# Verifica se o backend está saudável
check_backend_health() {
    # Verificar se o processo Python ainda existe
    if ! pgrep -f "python.*main" > /dev/null 2>&1 && ! pgrep -f "main.py" > /dev/null 2>&1; then
        return 1  # Processo não existe
    fi
    
    # Verificar se a API responde
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$BACKEND_URL" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        return 0  # Saudável
    else
        return 1  # Não saudável
    fi
}

# Reinicia o backend
restart_backend() {
    log_warn "🔄 Reiniciando backend..."
    
    # Parar processo existente
    pkill -9 -f "python.*main" 2>/dev/null || true
    pkill -9 -f "main.py" 2>/dev/null || true
    sleep 2
    
    # Iniciar novo processo
    cd "$SCRIPT_DIR"
    
    # Ativar venv se existir
    if [ -f "venv/bin/python" ]; then
        source venv/bin/activate
        venv/bin/python main.py >> "$BACKEND_LOG" 2>&1 &
    else
        python3 main.py >> "$BACKEND_LOG" 2>&1 &
    fi
    
    local backend_pid=$!
    log_info "Backend iniciado com PID: $backend_pid"
    
    # Aguardar backend ficar pronto
    local wait_count=0
    while [ $wait_count -lt 30 ]; do
        if check_backend_health; then
            log_success "✅ Backend reiniciado com sucesso!"
            return 0
        fi
        sleep 1
        wait_count=$((wait_count + 1))
    done
    
    log_error "❌ Backend não respondeu após reinício"
    return 1
}

# Função principal do watchdog
run_watchdog() {
    log_info "🐕 Watchdog iniciado"
    log_info "   Intervalo de verificação: ${CHECK_INTERVAL}s"
    log_info "   Limite de falhas: $UNHEALTHY_THRESHOLD"
    log_info "   Cooldown entre reinícios: ${RESTART_COOLDOWN}s"
    log_info "   Máximo de reinícios: $MAX_RESTARTS em ${RESTART_WINDOW}s"
    
    local unhealthy_count=0
    local restart_times=()
    local last_restart=0
    
    while true; do
        sleep "$CHECK_INTERVAL"
        
        if check_backend_health; then
            if [ $unhealthy_count -gt 0 ]; then
                log_success "Backend recuperado após $unhealthy_count verificação(ões) falha(s)"
            fi
            unhealthy_count=0
        else
            unhealthy_count=$((unhealthy_count + 1))
            log_warn "Backend não responde (falha #$unhealthy_count de $UNHEALTHY_THRESHOLD)"
            
            if [ $unhealthy_count -ge $UNHEALTHY_THRESHOLD ]; then
                local current_time=$(date +%s)
                
                # Verificar cooldown
                local time_since_restart=$((current_time - last_restart))
                if [ $time_since_restart -lt $RESTART_COOLDOWN ]; then
                    log_warn "Aguardando cooldown... (${time_since_restart}s de ${RESTART_COOLDOWN}s)"
                    continue
                fi
                
                # Limpar reinícios antigos da janela
                local new_restart_times=()
                for t in "${restart_times[@]}"; do
                    if [ $((current_time - t)) -lt $RESTART_WINDOW ]; then
                        new_restart_times+=("$t")
                    fi
                done
                restart_times=("${new_restart_times[@]}")
                
                # Verificar limite de reinícios
                if [ ${#restart_times[@]} -ge $MAX_RESTARTS ]; then
                    log_error "❌ Máximo de $MAX_RESTARTS reinícios atingido em ${RESTART_WINDOW}s"
                    log_error "   Algo está seriamente errado. Verifique os logs:"
                    log_error "   tail -100 $BACKEND_LOG"
                    log_error "Watchdog entrando em modo de espera (5 minutos)..."
                    sleep 300
                    restart_times=()  # Reset após espera
                    continue
                fi
                
                # Reiniciar
                if restart_backend; then
                    restart_times+=("$current_time")
                    last_restart=$current_time
                    unhealthy_count=0
                else
                    log_error "Falha ao reiniciar backend"
                fi
            fi
        fi
    done
}

# Comando: start
start_watchdog() {
    if [ -f "$WATCHDOG_PID_FILE" ]; then
        local pid=$(cat "$WATCHDOG_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "⚠️  Watchdog já está rodando (PID: $pid)"
            exit 1
        fi
        rm -f "$WATCHDOG_PID_FILE"
    fi
    
    echo "🐕 Iniciando Watchdog em background..."
    
    # Rotacionar log se muito grande
    if [ -f "$WATCHDOG_LOG" ] && [ $(stat -f%z "$WATCHDOG_LOG" 2>/dev/null || stat -c%s "$WATCHDOG_LOG" 2>/dev/null || echo 0) -gt 1048576 ]; then
        mv "$WATCHDOG_LOG" "${WATCHDOG_LOG}.old"
    fi
    
    # Iniciar em background
    nohup bash "$0" _run >> "$WATCHDOG_LOG" 2>&1 &
    local pid=$!
    echo "$pid" > "$WATCHDOG_PID_FILE"
    
    echo "✅ Watchdog iniciado (PID: $pid)"
    echo ""
    echo "Para ver logs: tail -f $WATCHDOG_LOG"
    echo "Para parar:    bash watchdog.sh stop"
}

# Comando: stop
stop_watchdog() {
    if [ -f "$WATCHDOG_PID_FILE" ]; then
        local pid=$(cat "$WATCHDOG_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🛑 Parando Watchdog (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
            sleep 1
            kill -9 "$pid" 2>/dev/null || true
            rm -f "$WATCHDOG_PID_FILE"
            echo "✅ Watchdog parado"
        else
            echo "ℹ️  Watchdog não estava rodando"
            rm -f "$WATCHDOG_PID_FILE"
        fi
    else
        echo "ℹ️  Watchdog não está rodando"
    fi
}

# Comando: status
status_watchdog() {
    echo "🐕 Status do Watchdog"
    echo "====================="
    
    if [ -f "$WATCHDOG_PID_FILE" ]; then
        local pid=$(cat "$WATCHDOG_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "✅ Watchdog: RODANDO (PID: $pid)"
        else
            echo "❌ Watchdog: PARADO (PID antigo: $pid)"
            rm -f "$WATCHDOG_PID_FILE"
        fi
    else
        echo "❌ Watchdog: PARADO"
    fi
    
    echo ""
    echo "Backend:"
    if check_backend_health; then
        echo "✅ Backend: SAUDÁVEL"
    else
        if pgrep -f "python.*main" > /dev/null 2>&1 || pgrep -f "main.py" > /dev/null 2>&1; then
            echo "⚠️  Backend: PROCESSO EXISTE mas não responde"
        else
            echo "❌ Backend: PARADO"
        fi
    fi
    
    echo ""
    echo "Logs:"
    echo "  Watchdog: $WATCHDOG_LOG"
    echo "  Backend:  $BACKEND_LOG"
}

# Comando: logs
show_logs() {
    if [ -f "$WATCHDOG_LOG" ]; then
        tail -50 "$WATCHDOG_LOG"
    else
        echo "ℹ️  Nenhum log do watchdog encontrado"
    fi
}

# Processar comando
case "${1:-}" in
    start)
        start_watchdog
        ;;
    stop)
        stop_watchdog
        ;;
    status)
        status_watchdog
        ;;
    logs)
        show_logs
        ;;
    _run)
        # Comando interno para execução em background
        run_watchdog
        ;;
    *)
        echo "🐕 Watchdog - Monitor Automático do Backend"
        echo ""
        echo "Uso:"
        echo "  bash watchdog.sh start   - Inicia o watchdog"
        echo "  bash watchdog.sh stop    - Para o watchdog"
        echo "  bash watchdog.sh status  - Verifica status"
        echo "  bash watchdog.sh logs    - Mostra logs recentes"
        echo ""
        echo "Configurações:"
        echo "  Intervalo de verificação: ${CHECK_INTERVAL}s"
        echo "  Limite de falhas:         $UNHEALTHY_THRESHOLD verificações"
        echo "  Cooldown entre reinícios: ${RESTART_COOLDOWN}s"
        echo "  Máximo de reinícios:      $MAX_RESTARTS em ${RESTART_WINDOW}s"
        ;;
esac
