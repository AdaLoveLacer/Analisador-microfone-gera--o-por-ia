/* Settings Manager - Handles configuration UI */

class SettingsManager {
    constructor() {
        this.config = null;
        this.devices = [];
    }

    /**
     * Load and display settings
     */
    async _loadSettings() {
        try {
            // Carregar configuração
            const configRes = await fetch('/api/config');
            this.config = await configRes.json();

            // Carregar dispositivos de áudio
            const devicesRes = await fetch('/api/devices');
            const devicesData = await devicesRes.json();
            this.devices = devicesData.devices || [];

            // Carregar dispositivos Whisper (CPU/CUDA)
            const whisperDevicesRes = await fetch('/api/whisper-devices');
            const whisperDevicesData = await whisperDevicesRes.json();
            this.whisperDevices = whisperDevicesData.devices || [];

            console.log('Dispositivos de áudio encontrados:', this.devices);
            console.log('Dispositivos Whisper encontrados:', this.whisperDevices);

            // Renderizar formulários
            this._renderAudioSettings();
            this._renderWhisperSettings();
            this._renderAISettings();
        } catch (error) {
            console.error('Erro ao carregar configurações:', error);
        }
    }

    /**
     * Render audio settings form with device selection
     */
    _renderAudioSettings() {
        const audioForm = document.getElementById('audio-settings-form');
        if (!audioForm) return;

        const audioConfig = this.config.audio || {};
        let html = `
            <div class="mb-3">
                <label class="form-label"><i class="fas fa-microphone-alt"></i> Selecione o Dispositivo de Áudio</label>
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i> 
                    <strong>${this.devices.length} dispositivo(s) de áudio detectado(s)</strong>
                </div>
                <select id="config-device-id" class="form-select">
        `;

        // Adicionar opção padrão
        html += `
                    <option value="-1" ${audioConfig.device_id === -1 ? 'selected' : ''}>
                        🔊 Dispositivo Padrão do Sistema
                    </option>
        `;

        // Se não houver dispositivos além do padrão, mostrar mensagem
        if (!this.devices || this.devices.length === 0) {
            html += `
                    <optgroup label="Outros Dispositivos">
                        <option disabled>
                            ⚠️ Nenhum outro dispositivo detectado
                        </option>
                    </optgroup>
            `;
        } else {
            // Agrupar dispositivos por tipo (entrada/saída)
            const inputDevices = this.devices.filter(d => d.max_input_channels > 0);
            const outputDevices = this.devices.filter(d => d.max_output_channels > 0);

            if (inputDevices.length > 0) {
                html += `<optgroup label="🎙️ Dispositivos de Entrada (Microfone)">`;
                inputDevices.forEach(device => {
                    const isSelected = audioConfig.device_id === device.index;
                    html += `
                        <option value="${device.index}" ${isSelected ? 'selected' : ''}>
                            🎙️ ${device.name} (${device.max_input_channels}ch)
                        </option>
                    `;
                });
                html += `</optgroup>`;
            }

            if (outputDevices.length > 0) {
                html += `<optgroup label="🔊 Dispositivos de Saída (Colunas)">`;
                outputDevices.forEach(device => {
                    const isSelected = audioConfig.device_id === device.index;
                    html += `
                        <option value="${device.index}" ${isSelected ? 'selected' : ''}>
                            🔊 ${device.name} (${device.max_output_channels}ch)
                        </option>
                    `;
                });
                html += `</optgroup>`;
            }
        }

        html += `
                </select>
                <small class="form-text text-muted d-block mt-2">
                    <i class="fas fa-lightbulb"></i> 
                    Selecione seu microfone para capturar áudio. O dispositivo padrão é recomendado na maioria dos casos.
                </small>
            </div>

            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label"><i class="fas fa-wave-square"></i> Taxa de Amostragem (Hz)</label>
                        <input type="number" id="config-sample-rate" class="form-control" 
                               value="${audioConfig.sample_rate || 16000}" step="100">
                        <small class="form-text text-muted">Padrão: 16000 Hz (Whisper recomenda)</small>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label"><i class="fas fa-cubes"></i> Tamanho do Chunk</label>
                        <input type="number" id="config-chunk-size" class="form-control" 
                               value="${audioConfig.chunk_size || 2048}" step="256">
                        <small class="form-text text-muted">Padrão: 2048 (mais responsivo)</small>
                    </div>
                </div>
            </div>

            <div class="mb-3">
                <label class="form-label"><i class="fas fa-volume-mute"></i> Limite de Silêncio</label>
                <input type="number" id="config-silence-threshold" class="form-control" step="0.01"
                       value="${audioConfig.silence_threshold || 0.02}" min="0" max="1">
                <small class="form-text text-muted">
                    Padrão: 0.02 (quanto menor, mais sensível ao silêncio)
                </small>
            </div>

            <button id="btn-save-audio-settings" class="btn btn-primary w-100">
                <i class="fas fa-save"></i> Salvar Configurações de Áudio
            </button>
        `;

        audioForm.innerHTML = html;

        // Adicionar listener de salvar
        document.getElementById('btn-save-audio-settings')?.addEventListener('click', () => {
            this._saveAudioSettings();
        });
    }

    /**
     * Save audio settings
     */
    async _saveAudioSettings() {
        try {
            const deviceId = parseInt(document.getElementById('config-device-id').value);
            const sampleRate = parseInt(document.getElementById('config-sample-rate').value);
            const chunkSize = parseInt(document.getElementById('config-chunk-size').value);
            const silenceThreshold = parseFloat(document.getElementById('config-silence-threshold').value);

            const payload = {
                'audio.device_id': deviceId,
                'audio.sample_rate': sampleRate,
                'audio.chunk_size': chunkSize,
                'audio.silence_threshold': silenceThreshold
            };

            const res = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                console.log('✓ Configurações de áudio salvas com sucesso!');
                alert('Configurações salvas! A aplicação será reiniciada com o novo dispositivo.');
            } else {
                alert('Erro ao salvar configurações');
            }
        } catch (error) {
            console.error('Erro ao salvar configurações de áudio:', error);
            alert('Erro ao salvar configurações');
        }
    }

    /**
     * Render Whisper settings
     */
    _renderWhisperSettings() {
        const whisperForm = document.getElementById('whisper-settings-form');
        if (!whisperForm) return;

        const whisperConfig = this.config.whisper || {};
        const models = [
            { value: 'tiny', label: 'Tiny (Muito Rápido - 39MB)', speed: '⚡⚡⚡' },
            { value: 'base', label: 'Base (Rápido - 142MB)', speed: '⚡⚡' },
            { value: 'small', label: 'Small (Balanceado - 466MB)', speed: '⚡' },
            { value: 'medium', label: 'Medium (Preciso - 1.5GB)', speed: '🐢' },
            { value: 'large', label: 'Large (Muito Preciso - 2.9GB)', speed: '🐢🐢' }
        ];

        let html = `
            <div class="mb-3">
                <label class="form-label"><i class="fas fa-robot"></i> Modelo Whisper</label>
                <select id="config-whisper-model" class="form-select">
        `;

        models.forEach(model => {
            const isSelected = whisperConfig.model === model.value ? 'selected' : '';
            html += `
                    <option value="${model.value}" ${isSelected}>
                        ${model.speed} ${model.label}
                    </option>
            `;
        });

        html += `
                </select>
                <small class="form-text text-muted d-block mt-2">
                    <i class="fas fa-info-circle"></i> 
                    Modelos maiores são mais precisos, mas mais lentos. Recomendado: "small"
                </small>
            </div>

            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label"><i class="fas fa-globe"></i> Idioma</label>
                        <select id="config-whisper-language" class="form-select">
                            <option value="pt" ${whisperConfig.language === 'pt' ? 'selected' : ''}>🇧🇷 Português (pt)</option>
                            <option value="en" ${whisperConfig.language === 'en' ? 'selected' : ''}>🇺🇸 English (en)</option>
                            <option value="es" ${whisperConfig.language === 'es' ? 'selected' : ''}>🇪🇸 Español (es)</option>
                            <option value="fr" ${whisperConfig.language === 'fr' ? 'selected' : ''}>🇫🇷 Français (fr)</option>
                            <option value="de" ${whisperConfig.language === 'de' ? 'selected' : ''}>🇩🇪 Deutsch (de)</option>
                            <option value="it" ${whisperConfig.language === 'it' ? 'selected' : ''}>🇮🇹 Italiano (it)</option>
                            <option value="ja" ${whisperConfig.language === 'ja' ? 'selected' : ''}>🇯🇵 日本語 (ja)</option>
                            <option value="zh" ${whisperConfig.language === 'zh' ? 'selected' : ''}>🇨🇳 中文 (zh)</option>
                            <option value="auto" ${whisperConfig.language === 'auto' ? 'selected' : ''}>🤖 Auto-detect (auto)</option>
                        </select>
                        <small class="form-text text-muted">Selecione o idioma da transcrição</small>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label"><i class="fas fa-bolt"></i> Processador</label>
                        <select id="config-whisper-device" class="form-select">
                            <option value="cpu" ${whisperConfig.device === 'cpu' ? 'selected' : ''}>
                                💻 CPU (Mais Compatível)
                            </option>
                            <option value="cuda" ${whisperConfig.device === 'cuda' ? 'selected' : ''}>
                                🚀 CUDA - GPU NVIDIA (Muito Mais Rápido)
                            </option>
                        </select>
                        <small class="form-text text-muted">
                            GPU NVIDIA é ~10x mais rápido que CPU
                        </small>
                    </div>
                </div>
            </div>

            <div class="alert alert-info">
                <i class="fas fa-lightbulb"></i>
                <strong>Dica:</strong> Use "small" ou "medium" para melhor qualidade com velocidade aceitável.
                Se tiver GPU NVIDIA com CUDA, será muito mais rápido!
            </div>

            <button id="btn-save-whisper-settings" class="btn btn-primary w-100">
                <i class="fas fa-save"></i> Salvar Configurações do Whisper
            </button>
        `;

        whisperForm.innerHTML = html;

        document.getElementById('btn-save-whisper-settings')?.addEventListener('click', () => {
            this._saveWhisperSettings();
        });
    }

    /**
     * Save Whisper settings
     */
    async _saveWhisperSettings() {
        try {
            const model = document.getElementById('config-whisper-model').value;
            const language = document.getElementById('config-whisper-language').value;
            const device = document.getElementById('config-whisper-device').value;

            const payload = {
                'whisper.model': model,
                'whisper.language': language,
                'whisper.device': device
            };

            const res = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                console.log('✓ Configurações do Whisper salvas com sucesso!');
                alert('Configurações salvas! Os modelos serão recarregados na próxima captura.');
            } else {
                alert('Erro ao salvar configurações');
            }
        } catch (error) {
            console.error('Erro ao salvar configurações do Whisper:', error);
            alert('Erro ao salvar configurações');
        }
    }

    /**
     * Render AI settings
     */
    _renderAISettings() {
        const aiForm = document.getElementById('ai-settings-form');
        if (!aiForm) return;

        const aiConfig = this.config.ai || {};
        let html = `
            <div class="mb-3">
                <label class="form-label"><i class="fas fa-brain"></i> Análise de Contexto Semântico</label>
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" id="config-context-analysis" 
                           ${aiConfig.context_analysis_enabled ? 'checked' : ''}>
                    <label class="form-check-label" for="config-context-analysis">
                        <strong>Habilitar análise inteligente de contexto</strong>
                    </label>
                </div>
                <small class="form-text text-muted d-block mt-2">
                    <i class="fas fa-info-circle"></i>
                    Usa IA para entender o contexto e variações da fala.
                    Exemplo: "Sus" detectará também "suspeitoso", "estranho", "fake"
                </small>
            </div>

            <div class="mb-3">
                <label class="form-label"><i class="fas fa-chart-line"></i> Confiança Mínima do Contexto</label>
                <div class="d-flex align-items-center gap-3">
                    <input type="range" id="config-min-confidence" class="form-range flex-grow-1"
                           min="0" max="1" step="0.05" value="${aiConfig.min_context_confidence || 0.6}">
                    <span id="confidence-value" class="badge bg-primary" style="font-size: 0.9em;">
                        ${(aiConfig.min_context_confidence || 0.6) * 100}%
                    </span>
                </div>
                <small class="form-text text-muted d-block mt-2">
                    <i class="fas fa-info-circle"></i>
                    Quanto maior, mais exigente na detecção (menos falsos positivos)
                </small>
            </div>

            <div class="alert alert-warning">
                <i class="fas fa-warning"></i>
                <strong>Nota:</strong> Análise de contexto pode aumentar o uso de CPU.
                Se estiver muito lento, reduza a confiança ou desabilite.
            </div>

            <button id="btn-save-ai-settings" class="btn btn-primary w-100">
                <i class="fas fa-save"></i> Salvar Configurações de IA
            </button>
        `;

        aiForm.innerHTML = html;

        // Adicionar listener de slider para mostrar valor em tempo real
        const confidenceSlider = document.getElementById('config-min-confidence');
        if (confidenceSlider) {
            confidenceSlider.addEventListener('input', (e) => {
                const percent = Math.round(e.target.value * 100);
                document.getElementById('confidence-value').textContent = percent + '%';
            });
        }

        document.getElementById('btn-save-ai-settings')?.addEventListener('click', () => {
            this._saveAISettings();
        });
    }

    /**
     * Save AI settings
     */
    async _saveAISettings() {
        try {
            const contextAnalysis = document.getElementById('config-context-analysis').checked;
            const minConfidence = parseFloat(document.getElementById('config-min-confidence').value);

            const payload = {
                'ai.context_analysis_enabled': contextAnalysis,
                'ai.min_context_confidence': minConfidence
            };

            const res = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                console.log('✓ Configurações de IA salvas com sucesso!');
                alert('Configurações salvas!');
            } else {
                alert('Erro ao salvar configurações');
            }
        } catch (error) {
            console.error('Erro ao salvar configurações de IA:', error);
            alert('Erro ao salvar configurações');
        }
    }
}

// Instanciar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.settingsManager = new SettingsManager();
});
