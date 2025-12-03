/* Main Application Entry Point */

// Initialize global managers
const wsClient = new WebSocketClient();
const configManager = new ConfigManager();
const settingsManager = new SettingsManager();
const uiController = new UIController();
const waveformVisualizer = new WaveformVisualizer();

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🎙️ Analisador de Microfone - Iniciando...');

    // Load initial configuration
    try {
        await configManager.fetchConfig();
        console.log('✓ Configuração carregada');
    } catch (error) {
        console.error('✗ Erro ao carregar configuração:', error);
        uiController._showError('Erro ao carregar configuração do servidor');
    }

    // Connect WebSocket
    wsClient.connect();

    // Register WebSocket event listeners
    wsClient.on('connect', () => {
        console.log('✓ WebSocket conectado');
        wsClient.getStatus();
    });

    wsClient.on('disconnect', () => {
        console.log('✗ WebSocket desconectado');
    });

    wsClient.on('transcription_update', (data) => {
        console.log('Transcrição:', data.text);
        uiController.updateTranscript(data.text, data.confidence);
    });

    wsClient.on('keyword_detected', (data) => {
        console.log('Keyword detectada:', data.keyword_id);
        uiController.updateDetection(
            data.keyword_id,
            data.text,
            data.confidence,
            data.context_score
        );
    });

    wsClient.on('status_update', (data) => {
        console.log('Status:', data);
    });

    wsClient.on('error', (data) => {
        console.error('Erro do servidor:', data.message);
        uiController._showError(data.message);
    });

    // Auto-load dashboard
    uiController._initializeDashboard();

    console.log('✓ Aplicação pronta!');
});

// Graceful shutdown
window.addEventListener('beforeunload', () => {
    wsClient.stopCapture();
    wsClient.disconnect();
});
