/* UI Controller - Manages UI interactions and updates */

class UIController {
    constructor() {
        this.currentPage = 'dashboard';
        this.stats = {
            detections: 0,
            transcriptions: 0,
            uptime: 0
        };
        this.startTime = null;
        this.activityChart = null;
        this.activityData = [];
        
        this._initializeEventListeners();
        this._loadTheme();
    }

    /**
     * Initialize all event listeners
     */
    _initializeEventListeners() {
        // Page navigation
        document.querySelectorAll('.sidebar .nav-link').forEach(link => {
            link.addEventListener('click', (e) => this._handlePageChange(e));
        });

        // Capture control buttons
        document.getElementById('btn-start')?.addEventListener('click', () => this._startCapture());
        document.getElementById('btn-stop')?.addEventListener('click', () => this._stopCapture());

        // Theme toggle
        document.getElementById('theme-toggle')?.addEventListener('click', () => this._toggleTheme());

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === ' ' && e.target === document.body) {
                e.preventDefault();
                this._toggleCapture();
            }
        });
    }

    /**
     * Handle page navigation
     */
    _handlePageChange(event) {
        event.preventDefault();
        const link = event.currentTarget;
        const page = link.dataset.page;

        // Update active link
        document.querySelectorAll('.sidebar .nav-link').forEach(l => {
            l.classList.remove('active');
        });
        link.classList.add('active');

        // Update active page
        document.querySelectorAll('.page-content').forEach(p => {
            p.classList.remove('active');
        });
        document.getElementById(`page-${page}`)?.classList.add('active');

        this.currentPage = page;
        this._initializePage(page);
    }

    /**
     * Initialize page content
     */
    async _initializePage(page) {
        switch (page) {
            case 'dashboard':
                this._initializeDashboard();
                break;
            case 'keywords':
                await this._loadKeywords();
                break;
            case 'sounds':
                await this._loadSounds();
                break;
            case 'settings':
                await this._loadSettings();
                break;
            case 'history':
                await this._loadHistory();
                break;
            case 'backup':
                this._initializeBackup();
                break;
        }
    }

    /**
     * Initialize dashboard
     */
    _initializeDashboard() {
        if (!this.activityChart) {
            const ctx = document.getElementById('activity-chart');
            if (ctx) {
                this.activityChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Detecções',
                            data: [],
                            backgroundColor: 'rgba(13, 110, 253, 0.5)',
                            borderColor: 'rgb(13, 110, 253)',
                            tension: 0.1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 10
                            }
                        }
                    }
                });
            }
        }
    }

    /**
     * Load keywords list
     */
    async _loadKeywords() {
        try {
            const response = await fetch('/api/keywords');
            const data = await response.json();
            const keywords = data.keywords || [];

            const tbody = document.getElementById('keywords-body');
            if (!tbody) return;

            if (keywords.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Nenhuma palavra-chave configurada</td></tr>';
                return;
            }

            tbody.innerHTML = keywords.map(kw => `
                <tr>
                    <td><strong>${kw.name}</strong></td>
                    <td><code>${kw.pattern}</code></td>
                    <td><small>${kw.sound_id || '-'}</small></td>
                    <td>
                        <span class="badge ${kw.enabled ? 'bg-success' : 'bg-secondary'}">
                            ${kw.enabled ? 'Ativo' : 'Inativo'}
                        </span>
                    </td>
                    <td>
                        <small>${(kw.variations || []).join(', ') || '-'}</small>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="uiController._editKeyword('${kw.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="uiController._deleteKeyword('${kw.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            console.error('Error loading keywords:', error);
            this._showError('Erro ao carregar palavras-chave');
        }
    }

    /**
     * Load sounds list
     */
    async _loadSounds() {
        try {
            const response = await fetch('/api/sounds');
            const data = await response.json();
            const sounds = data.sounds || [];

            const grid = document.getElementById('sounds-grid');
            if (!grid) return;

            if (sounds.length === 0) {
                grid.innerHTML = '<div class="col-12 text-center text-muted">Nenhum som configurado</div>';
                return;
            }

            grid.innerHTML = sounds.map(sound => `
                <div class="col-md-4 mb-3">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">${sound.name}</h5>
                            <p class="card-text">
                                <small class="text-muted">
                                    ${sound.file_path}<br>
                                    Volume: ${Math.round(sound.volume * 100)}%<br>
                                    Categoria: ${sound.category}
                                </small>
                            </p>
                            <div class="btn-group" role="group">
                                <button class="btn btn-sm btn-primary" onclick="wsClient.testSound('${sound.id}')">
                                    <i class="fas fa-play"></i> Ouvir
                                </button>
                                <button class="btn btn-sm btn-secondary" onclick="uiController._editSound('${sound.id}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="uiController._deleteSound('${sound.id}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading sounds:', error);
            this._showError('Erro ao carregar sons');
        }
    }

    /**
     * Load settings
     */
    async _loadSettings() {
        try {
            const config = configManager.config;

            // Audio settings
            this._generateSettingsForm('audio-settings-form', config.audio || {}, 'audio');

            // Whisper settings
            this._generateSettingsForm('whisper-settings-form', config.whisper || {}, 'whisper');

            // AI settings
            this._generateSettingsForm('ai-settings-form', config.ai || {}, 'ai');

            // UI settings
            this._generateSettingsForm('ui-settings-form', config.ui || {}, 'ui');

            document.getElementById('btn-save-settings')?.addEventListener('click', () => this._saveSettings());
            document.getElementById('btn-reset-settings')?.addEventListener('click', () => this._resetSettings());
        } catch (error) {
            console.error('Error loading settings:', error);
            this._showError('Erro ao carregar configurações');
        }
    }

    /**
     * Generate settings form
     */
    _generateSettingsForm(containerId, settings, section) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const form = document.createElement('form');
        form.className = 'row g-3';
        form.id = `${section}-form`;

        Object.entries(settings).forEach(([key, value]) => {
            const fieldId = `${section}-${key}`;
            const label = this._humanize(key);

            let input;
            if (typeof value === 'boolean') {
                input = `
                    <div class="col-12">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="${fieldId}" ${value ? 'checked' : ''}>
                            <label class="form-check-label" for="${fieldId}">${label}</label>
                        </div>
                    </div>
                `;
            } else if (typeof value === 'number') {
                input = `
                    <div class="col-md-6">
                        <label for="${fieldId}" class="form-label">${label}</label>
                        <input type="number" class="form-control" id="${fieldId}" value="${value}">
                    </div>
                `;
            } else {
                input = `
                    <div class="col-md-6">
                        <label for="${fieldId}" class="form-label">${label}</label>
                        <input type="text" class="form-control" id="${fieldId}" value="${value}">
                    </div>
                `;
            }

            form.innerHTML += input;
        });

        container.innerHTML = '';
        container.appendChild(form);
    }

    /**
     * Save settings
     */
    async _saveSettings() {
        try {
            const config = {};
            
            ['audio', 'whisper', 'ai', 'ui'].forEach(section => {
                const form = document.getElementById(`${section}-form`);
                if (form) {
                    const sectionConfig = {};
                    form.querySelectorAll('[id^="' + section + '-"]').forEach(input => {
                        const key = input.id.replace(`${section}-`, '');
                        if (input.type === 'checkbox') {
                            sectionConfig[key] = input.checked;
                        } else if (input.type === 'number') {
                            sectionConfig[key] = parseFloat(input.value);
                        } else {
                            sectionConfig[key] = input.value;
                        }
                    });
                    config[section] = sectionConfig;
                }
            });

            await configManager.saveConfig(config);
            this._showSuccess('Configurações salvas com sucesso!');
        } catch (error) {
            console.error('Error saving settings:', error);
            this._showError('Erro ao salvar configurações');
        }
    }

    /**
     * Reset settings
     */
    async _resetSettings() {
        if (confirm('Tem certeza que deseja restaurar as configurações padrão?')) {
            try {
                await configManager.resetToDefaults();
                await this._loadSettings();
                this._showSuccess('Configurações restauradas!');
            } catch (error) {
                console.error('Error resetting settings:', error);
                this._showError('Erro ao restaurar configurações');
            }
        }
    }

    /**
     * Load history
     */
    async _loadHistory() {
        try {
            // Load detections
            const detectionsResp = await fetch('/api/detections?limit=50');
            const detections = await detectionsResp.json();
            this._renderDetections(detections.detections || []);

            // Load stats
            const statsResp = await fetch('/api/detections/stats');
            const stats = await statsResp.json();
            this._renderStats(stats);
        } catch (error) {
            console.error('Error loading history:', error);
            this._showError('Erro ao carregar histórico');
        }
    }

    /**
     * Render detections table
     */
    _renderDetections(detections) {
        const tbody = document.getElementById('detections-body');
        if (!tbody) return;

        if (detections.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Sem detecções</td></tr>';
            return;
        }

        tbody.innerHTML = detections.map(d => `
            <tr>
                <td><small>${new Date(d.timestamp).toLocaleString('pt-BR')}</small></td>
                <td>${d.text_detected}</td>
                <td><strong>${d.keyword_matched}</strong></td>
                <td>${Math.round(d.confidence * 100)}%</td>
                <td>${Math.round(d.context_score * 100)}%</td>
            </tr>
        `).join('');
    }

    /**
     * Render stats
     */
    _renderStats(stats) {
        const statsBody = document.getElementById('stats-body');
        if (!statsBody) return;

        const byKeyword = stats.by_keyword || {};
        const keywordStats = Object.entries(byKeyword)
            .map(([kw, count]) => `<li>${kw}: <strong>${count}</strong> detecções</li>`)
            .join('');

        statsBody.innerHTML = `
            <ul class="list-unstyled">
                <li>Total de Detecções: <strong>${stats.total_detections || 0}</strong></li>
                <li>Confiança Média: <strong>${Math.round((stats.avg_confidence || 0) * 100)}%</strong></li>
                <li>Score de Contexto Médio: <strong>${Math.round((stats.avg_context_score || 0) * 100)}%</strong></li>
            </ul>
            <h6 class="mt-3">Detecções por Palavra-Chave:</h6>
            <ul>${keywordStats}</ul>
        `;
    }

    /**
     * Initialize backup page
     */
    _initializeBackup() {
        document.getElementById('btn-create-backup')?.addEventListener('click', () => this._createBackup());
        document.getElementById('btn-restore-backup')?.addEventListener('click', () => {
            document.getElementById('backup-file-input').click();
        });
        document.getElementById('backup-file-input')?.addEventListener('change', (e) => this._handleBackupFile(e));
        document.getElementById('btn-export-all')?.addEventListener('click', () => this._exportAll());
    }

    /**
     * Create backup
     */
    async _createBackup() {
        try {
            const config = await configManager.exportConfig();
            const backup = {
                timestamp: new Date().toISOString(),
                version: '1.0.0',
                config: config
            };

            const element = document.createElement('a');
            element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(JSON.stringify(backup, null, 2)));
            element.setAttribute('download', `backup-${new Date().getTime()}.json`);
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);

            this._showSuccess('Backup criado com sucesso!');
        } catch (error) {
            console.error('Error creating backup:', error);
            this._showError('Erro ao criar backup');
        }
    }

    /**
     * Handle backup file
     */
    _handleBackupFile(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async (e) => {
            try {
                const backup = JSON.parse(e.target.result);
                await configManager.importConfig(backup.config);
                this._showSuccess('Backup restaurado com sucesso!');
            } catch (error) {
                console.error('Error restoring backup:', error);
                this._showError('Erro ao restaurar backup');
            }
        };
        reader.readAsText(file);
    }

    /**
     * Export all
     */
    async _exportAll() {
        try {
            const config = await configManager.exportConfig();
            const element = document.createElement('a');
            element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(JSON.stringify(config, null, 2)));
            element.setAttribute('download', `export-${new Date().getTime()}.json`);
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);

            this._showSuccess('Exportação criada com sucesso!');
        } catch (error) {
            console.error('Error exporting config:', error);
            this._showError('Erro ao exportar');
        }
    }

    /**
     * Start capture
     */
    async _startCapture() {
        try {
            wsClient.startCapture();
            this.startTime = new Date();
            document.getElementById('btn-start').style.display = 'none';
            document.getElementById('btn-stop').style.display = 'inline-block';
            document.getElementById('capture-status').className = 'alert alert-success';
            document.getElementById('capture-status').textContent = 'Status: Capturando...';
            this._showSuccess('Captura iniciada!');
        } catch (error) {
            console.error('Error starting capture:', error);
            this._showError('Erro ao iniciar captura');
        }
    }

    /**
     * Stop capture
     */
    _stopCapture() {
        wsClient.stopCapture();
        document.getElementById('btn-start').style.display = 'inline-block';
        document.getElementById('btn-stop').style.display = 'none';
        document.getElementById('capture-status').className = 'alert alert-info';
        document.getElementById('capture-status').textContent = 'Status: Parado';
        this._showSuccess('Captura parada!');
    }

    /**
     * Toggle capture
     */
    _toggleCapture() {
        const startBtn = document.getElementById('btn-start');
        if (startBtn.style.display !== 'none') {
            this._startCapture();
        } else {
            this._stopCapture();
        }
    }

    /**
     * Update transcription display
     */
    updateTranscript(text, confidence) {
        document.getElementById('transcript-display').textContent = text;
        document.getElementById('transcript-display').classList.add('active');
        document.getElementById('transcript-confidence').textContent = Math.round(confidence * 100);
        this.stats.transcriptions++;
        document.getElementById('stat-transcriptions').textContent = this.stats.transcriptions;
    }

    /**
     * Update detection display
     */
    updateDetection(keywordId, text, confidence, contextScore) {
        this.stats.detections++;
        document.getElementById('stat-detections').textContent = this.stats.detections;
        document.getElementById('stat-keyword').textContent = keywordId;

        const html = `
            <div class="list-group-item">
                <small class="text-muted">${new Date().toLocaleTimeString('pt-BR')}</small><br>
                <strong>${keywordId}</strong>: "${text}"<br>
                <small>Confiança: ${Math.round(confidence * 100)}% | Contexto: ${Math.round(contextScore * 100)}%</small>
            </div>
        `;
        document.getElementById('recent-detections').insertAdjacentHTML('afterbegin', html);
    }

    /**
     * Show success message
     */
    _showSuccess(message) {
        this._showAlert(message, 'success');
    }

    /**
     * Show error message
     */
    _showError(message) {
        this._showAlert(message, 'danger');
    }

    /**
     * Show alert
     */
    _showAlert(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.querySelector('.p-4')?.insertAdjacentElement('afterbegin', alert);
        
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    /**
     * Toggle theme
     */
    _toggleTheme() {
        const isDark = document.body.classList.toggle('dark-theme');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        
        const btn = document.getElementById('theme-toggle');
        if (isDark) {
            btn.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            btn.innerHTML = '<i class="fas fa-moon"></i>';
        }
    }

    /**
     * Load saved theme
     */
    _loadTheme() {
        const theme = localStorage.getItem('theme') || 'light';
        if (theme === 'dark') {
            document.body.classList.add('dark-theme');
            document.getElementById('theme-toggle').innerHTML = '<i class="fas fa-sun"></i>';
        }
    }

    /**
     * Humanize key names
     */
    _humanize(str) {
        return str
            .replace(/_/g, ' ')
            .replace(/^(.)/, (c) => c.toUpperCase())
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    /**
     * Delete keyword
     */
    async _deleteKeyword(id) {
        if (confirm('Tem certeza?')) {
            try {
                await fetch(`/api/keywords/${id}`, { method: 'DELETE' });
                await this._loadKeywords();
                this._showSuccess('Palavra-chave deletada!');
            } catch (error) {
                this._showError('Erro ao deletar');
            }
        }
    }

    /**
     * Edit keyword
     */
    _editKeyword(id) {
        this._showError('Edição inline em breve!');
    }

    /**
     * Delete sound
     */
    async _deleteSound(id) {
        if (confirm('Tem certeza?')) {
            try {
                await fetch(`/api/sounds/${id}`, { method: 'DELETE' });
                await this._loadSounds();
                this._showSuccess('Som deletado!');
            } catch (error) {
                this._showError('Erro ao deletar');
            }
        }
    }

    /**
     * Edit sound
     */
    _editSound(id) {
        this._showError('Edição de som em breve!');
    }
}

// Create global UI controller
const uiController = new UIController();

// Connect WebSocket and setup callbacks
document.addEventListener('DOMContentLoaded', () => {
    wsClient.connect();

    // Register callbacks
    wsClient.on('transcript_update', (data) => {
        if (data) uiController.updateTranscript(data.text, data.confidence);
    });

    wsClient.on('keyword_detected', (data) => {
        if (data) uiController.updateDetection(data.keyword_id, data.text, data.confidence, data.context_score);
    });

    wsClient.on('status_update', (data) => {
        console.log('Status updated:', data);
    });

    // Initialize dashboard
    uiController._initializeDashboard();
});
