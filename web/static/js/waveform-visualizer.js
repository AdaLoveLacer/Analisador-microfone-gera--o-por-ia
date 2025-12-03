/* Waveform Visualizer - Real-time audio visualization */

class WaveformVisualizer {
    constructor() {
        this.canvas = document.getElementById('waveform-canvas');
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        this.audioData = [];
        this.isCapturing = false;
        this.animationId = null;
        
        // Configurar tamanho real do canvas
        this._resizeCanvas();
        window.addEventListener('resize', () => this._resizeCanvas());
        
        // Cores
        this.colors = {
            background: '#1a1a1a',
            waveform: '#00ff00',
            grid: '#333333',
            text: '#888888'
        };

        // Iniciar animação
        this._animate();
    }

    /**
     * Resize canvas to fit container
     */
    _resizeCanvas() {
        const rect = this.canvas.getBoundingClientRect();
        this.canvas.width = rect.width * window.devicePixelRatio;
        this.canvas.height = rect.height * window.devicePixelRatio;
        this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }

    /**
     * Update audio data from WebSocket
     */
    updateAudioLevel(level) {
        // CORREÇÃO: Level já vem normalizado (0-1) do backend
        // Converter para amplitude em pixels (0 a altura/2)
        const maxHeight = (this.canvas.height / window.devicePixelRatio) * 0.4;
        // O level já está em escala 0-1 logarítmica
        const amplitude = Math.max(0, Math.min(maxHeight, level * maxHeight));
        
        this.audioData.push(amplitude);
        
        // Manter apenas os últimos pontos (buffer)
        // Quanto mais pontos, mais smootho o waveform
        const maxPoints = (this.canvas.width / window.devicePixelRatio) * 2;
        if (this.audioData.length > maxPoints) {
            this.audioData.shift();
        }
    }

    /**
     * Start capturing visualizer
     */
    startCapture() {
        this.isCapturing = true;
        this.audioData = [];
    }

    /**
     * Stop capturing visualizer
     */
    stopCapture() {
        this.isCapturing = false;
        // Fadeout suave
        setTimeout(() => {
            this.audioData = [];
        }, 500);
    }

    /**
     * Draw waveform
     */
    _draw() {
        const width = this.canvas.width / window.devicePixelRatio;
        const height = this.canvas.height / window.devicePixelRatio;
        const centerY = height / 2;

        // Limpar canvas
        this.ctx.fillStyle = this.colors.background;
        this.ctx.fillRect(0, 0, width, height);

        // Desenhar grid
        this._drawGrid(width, height);

        if (this.audioData.length === 0) {
            this._drawNoSignal(width, height);
            return;
        }

        // Desenhar waveform
        this.ctx.strokeStyle = this.colors.waveform;
        this.ctx.lineWidth = 2;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';

        const xStep = width / this.audioData.length;
        
        this.ctx.beginPath();
        this.audioData.forEach((amplitude, index) => {
            const x = index * xStep;
            const y = centerY - amplitude;
            
            if (index === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        });
        this.ctx.stroke();

        // Desenhar reflexo inferior (espelho)
        this.ctx.strokeStyle = this.colors.waveform + '44'; // Com transparência
        this.ctx.beginPath();
        this.audioData.forEach((amplitude, index) => {
            const x = index * xStep;
            const y = centerY + amplitude; // Invertido para espelho
            
            if (index === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        });
        this.ctx.stroke();

        // Desenhar linha central
        this.ctx.strokeStyle = this.colors.grid;
        this.ctx.lineWidth = 1;
        this.ctx.setLineDash([5, 5]);
        this.ctx.beginPath();
        this.ctx.moveTo(0, centerY);
        this.ctx.lineTo(width, centerY);
        this.ctx.stroke();
        this.ctx.setLineDash([]);

        // Calcular e mostrar nível RMS (decibéis)
        if (this.audioData.length > 0) {
            this._drawLevel(width, height);
        }
    }

    /**
     * Draw grid lines
     */
    _drawGrid(width, height) {
        this.ctx.strokeStyle = this.colors.grid;
        this.ctx.lineWidth = 0.5;

        // Grid horizontal (linhas)
        const hLines = 4;
        for (let i = 1; i < hLines; i++) {
            const y = (height / hLines) * i;
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(width, y);
            this.ctx.stroke();
        }

        // Grid vertical (colunas)
        const vLines = 8;
        for (let i = 1; i < vLines; i++) {
            const x = (width / vLines) * i;
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, height);
            this.ctx.stroke();
        }
    }

    /**
     * Draw "no signal" message
     */
    _drawNoSignal(width, height) {
        this.ctx.fillStyle = this.colors.text;
        this.ctx.font = 'italic 16px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(
            this.isCapturing ? '🎤 Aguardando som...' : '⏸️ Clique em "Iniciar Captura"',
            width / 2,
            height / 2
        );
    }

    /**
     * Draw current audio level
     */
    _drawLevel(width, height) {
        // Calcular RMS
        const rms = Math.sqrt(
            this.audioData.reduce((sum, val) => sum + val * val, 0) / this.audioData.length
        );
        
        // Converter para decibéis (simplificado)
        const db = 20 * Math.log10(rms / (height / 4) + 0.0001);
        const normalized = Math.max(0, Math.min(100, db + 40)); // Normalizar 0-100

        // Barra de nível
        const barWidth = 150;
        const barHeight = 20;
        const barX = width - barWidth - 10;
        const barY = 10;

        // Fundo da barra
        this.ctx.fillStyle = '#222222';
        this.ctx.fillRect(barX, barY, barWidth, barHeight);

        // Nível atual
        const fillColor = normalized > 80 ? '#ff4444' : normalized > 50 ? '#ffff00' : '#00ff00';
        this.ctx.fillStyle = fillColor;
        this.ctx.fillRect(barX, barY, (barWidth * normalized) / 100, barHeight);

        // Borda
        this.ctx.strokeStyle = this.colors.text;
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(barX, barY, barWidth, barHeight);

        // Label
        this.ctx.fillStyle = this.colors.text;
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'left';
        this.ctx.fillText(`${Math.round(normalized)}%`, barX + 5, barY + 15);
    }

    /**
     * Animation loop
     */
    _animate() {
        this._draw();
        this.animationId = requestAnimationFrame(() => this._animate());
    }

    /**
     * Destroy visualizer
     */
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
    }
}

// Instanciar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.waveformVisualizer = new WaveformVisualizer();
});
