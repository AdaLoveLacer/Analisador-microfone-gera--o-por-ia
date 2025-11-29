/* Configuration Manager - Handles app configuration persistence */

class ConfigManager {
    constructor() {
        this.config = {};
        this.listeners = [];
    }

    /**
     * Fetch configuration from server
     */
    async fetchConfig() {
        try {
            const response = await fetch('/api/config');
            if (!response.ok) throw new Error('Failed to fetch config');
            this.config = await response.json();
            this._notifyListeners();
            return this.config;
        } catch (error) {
            console.error('Error fetching config:', error);
            throw error;
        }
    }

    /**
     * Save configuration to server
     */
    async saveConfig(config) {
        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            if (!response.ok) throw new Error('Failed to save config');
            this.config = config;
            this._notifyListeners();
            return await response.json();
        } catch (error) {
            console.error('Error saving config:', error);
            throw error;
        }
    }

    /**
     * Get configuration value
     */
    get(path, defaultValue = null) {
        let value = this.config;
        const keys = path.split('.');
        
        for (const key of keys) {
            if (value && typeof value === 'object' && key in value) {
                value = value[key];
            } else {
                return defaultValue;
            }
        }
        
        return value !== undefined ? value : defaultValue;
    }

    /**
     * Set configuration value locally (not saved)
     */
    set(path, value) {
        const keys = path.split('.');
        let obj = this.config;
        
        for (let i = 0; i < keys.length - 1; i++) {
            const key = keys[i];
            if (!(key in obj)) {
                obj[key] = {};
            }
            obj = obj[key];
        }
        
        obj[keys[keys.length - 1]] = value;
    }

    /**
     * Get all keywords
     */
    getKeywords() {
        return this.get('keywords', []);
    }

    /**
     * Get all sounds
     */
    getSounds() {
        return this.get('sounds', []);
    }

    /**
     * Export configuration
     */
    async exportConfig() {
        try {
            const response = await fetch('/api/config/export');
            if (!response.ok) throw new Error('Failed to export config');
            return await response.json();
        } catch (error) {
            console.error('Error exporting config:', error);
            throw error;
        }
    }

    /**
     * Import configuration
     */
    async importConfig(config) {
        try {
            const response = await fetch('/api/config/import', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            if (!response.ok) throw new Error('Failed to import config');
            this.config = config;
            this._notifyListeners();
            return await response.json();
        } catch (error) {
            console.error('Error importing config:', error);
            throw error;
        }
    }

    /**
     * Reset to defaults
     */
    async resetToDefaults() {
        try {
            const response = await fetch('/api/config/reset', { method: 'POST' });
            if (!response.ok) throw new Error('Failed to reset config');
            await this.fetchConfig();
            return await response.json();
        } catch (error) {
            console.error('Error resetting config:', error);
            throw error;
        }
    }

    /**
     * Register listener for config changes
     */
    onChange(callback) {
        this.listeners.push(callback);
    }

    _notifyListeners() {
        this.listeners.forEach(callback => {
            try {
                callback(this.config);
            } catch (error) {
                console.error('Error in config listener:', error);
            }
        });
    }

    /**
     * Get local storage persistence
     */
    getFromStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error(`Error getting from storage: ${key}`, error);
            return defaultValue;
        }
    }

    /**
     * Save to local storage
     */
    saveToStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error(`Error saving to storage: ${key}`, error);
        }
    }
}

// Create global config manager
const configManager = new ConfigManager();

// Initialize config on load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await configManager.fetchConfig();
        console.log('Configuration loaded:', configManager.config);
    } catch (error) {
        console.error('Failed to load configuration:', error);
    }
});
