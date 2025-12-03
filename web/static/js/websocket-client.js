/* WebSocket Client */

class WebSocketClient {
    constructor(serverUrl = null) {
        this.serverUrl = serverUrl || window.location.origin;
        this.socket = null;
        this.isConnected = false;
        this.callbacks = {
            connect: [],
            disconnect: [],
            transcript_update: [],
            keyword_detected: [],
            config_updated: [],
            status_update: [],
            error: []
        };
    }

    connect() {
        try {
            // Check if Socket.IO is loaded
            if (typeof io === 'undefined') {
                console.error('Socket.IO library not loaded. Make sure socket.io script is included.');
                setTimeout(() => this.connect(), 1000);
                return;
            }

            this.socket = io(this.serverUrl, {
                reconnection: true,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 5000,
                reconnectionAttempts: 5
            });

            // Handle connection
            this.socket.on('connect', () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this._trigger('connect');
                this._updateStatusIndicator(true);
            });

            // Handle disconnection
            this.socket.on('disconnect', () => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this._trigger('disconnect');
                this._updateStatusIndicator(false);
            });

            // Listen for all event types
            this.socket.on('transcript_update', (data) => this._trigger('transcript_update', data));
            this.socket.on('keyword_detected', (data) => this._trigger('keyword_detected', data));
            this.socket.on('config_updated', (data) => this._trigger('config_updated', data));
            this.socket.on('status_update', (data) => this._trigger('status_update', data));
            this.socket.on('audio_level', (data) => this._handleAudioLevel(data));
            this.socket.on('capture_started', (data) => this._handleCaptureStarted(data));
            this.socket.on('capture_stopped', (data) => this._handleCaptureStopped(data));
            this.socket.on('error', (data) => this._trigger('error', data));
            this.socket.on('connection_response', (data) => console.log('Server:', data));

        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }

    emit(event, data = {}) {
        if (this.socket && this.isConnected) {
            this.socket.emit(event, data);
        } else {
            console.warn(`Cannot emit ${event}: WebSocket not connected`);
        }
    }

    on(event, callback) {
        if (event in this.callbacks) {
            this.callbacks[event].push(callback);
        }
    }

    _trigger(event, data = null) {
        if (event in this.callbacks) {
            this.callbacks[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in callback for ${event}:`, error);
                }
            });
        }
    }

    _updateStatusIndicator(connected) {
        const indicator = document.getElementById('status-indicator');
        if (indicator) {
            if (connected) {
                indicator.classList.add('connected');
                indicator.innerHTML = '<i class="fas fa-check-circle"></i> Conectado';
            } else {
                indicator.classList.remove('connected');
                indicator.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Desconectado';
            }
        }
    }

    // Convenience methods
    startCapture() {
        this.emit('start_capture');
    }

    stopCapture() {
        this.emit('stop_capture');
    }

    updateConfig(config) {
        this.emit('update_config', config);
    }

    testSound(soundId) {
        this.emit('test_sound', { sound_id: soundId });
    }

    getStatus() {
        this.emit('get_status');
    }

    /**
     * Handle audio level update
     */
    _handleAudioLevel(data) {
        const level = data.level || 0;
        if (window.waveformVisualizer) {
            window.waveformVisualizer.updateAudioLevel(level);
        }
    }

    /**
     * Handle capture started
     */
    _handleCaptureStarted(data) {
        if (window.waveformVisualizer) {
            window.waveformVisualizer.startCapture();
        }
        this._trigger('capture_started', data);
    }

    /**
     * Handle capture stopped
     */
    _handleCaptureStopped(data) {
        if (window.waveformVisualizer) {
            window.waveformVisualizer.stopCapture();
        }
        this._trigger('capture_stopped', data);
    }
}
