// Settings Management Module
class SettingsManager {
    constructor() {
        this.settings = {};
        this.currentSection = 'general';
        this.unsavedChanges = false;
        this.init();
    }

    async init() {
        await this.loadSettings();
        this.setupEventListeners();
        this.showSection('general');
    }

    setupEventListeners() {
        // Track changes in all form elements
        document.addEventListener('change', (e) => {
            if (e.target.matches('input, select, textarea')) {
                this.markUnsaved();
            }
        });

        // Warn before leaving with unsaved changes
        window.addEventListener('beforeunload', (e) => {
            if (this.unsavedChanges) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    }

    async loadSettings() {
        try {
            const response = await api.get('/settings');
            this.settings = response.settings || this.getDefaultSettings();
            this.renderAllSettings();
        } catch (error) {
            console.error('Failed to load settings:', error);
            this.settings = this.getDefaultSettings();
            this.renderAllSettings();
        }
    }

    getDefaultSettings() {
        return {
            general: {
                appName: 'RealtyScanner',
                language: 'he',
                timezone: 'Asia/Jerusalem',
                theme: 'auto',
                dateFormat: 'DD/MM/YYYY',
                itemsPerPage: 25
            },
            scanning: {
                defaultScanInterval: 30,
                retryInterval: 5,
                maxRetries: 3,
                concurrentScans: 3,
                requestDelay: 1.0,
                timeout: 30
            },
            notifications: {
                globalNotifications: true,
                quietStart: '23:00',
                quietEnd: '07:00',
                maxNotificationsPerHour: 10,
                urgentPriceThreshold: 10,
                newPropertyPriority: 'normal'
            },
            storage: {
                propertyRetention: 90,
                logRetention: 30,
                notificationRetention: 60,
                autoVacuum: true,
                backupFrequency: 'daily'
            },
            security: {
                sessionTimeout: 60,
                requirePassword: false,
                apiRateLimit: 100,
                enableCors: false
            },
            advanced: {
                logLevel: 'INFO',
                enableFileLogging: true,
                debugMode: false,
                mockData: false
            }
        };
    }

    showSection(sectionName) {
        // Update navigation
        document.querySelectorAll('.settings-nav .nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[href="#${sectionName}"]`)?.classList.add('active');

        // Update content sections
        document.querySelectorAll('.settings-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${sectionName}-settings`)?.classList.add('active');

        this.currentSection = sectionName;
    }

    renderAllSettings() {
        this.renderGeneralSettings();
        this.renderScanningSettings();
        this.renderNotificationSettings();
        this.renderStorageSettings();
        this.renderSecuritySettings();
        this.renderAdvancedSettings();
    }

    renderGeneralSettings() {
        const general = this.settings.general || {};
        
        utils.updateElement('app-name', general.appName, 'value');
        utils.updateElement('app-language', general.language, 'value');
        utils.updateElement('timezone', general.timezone, 'value');
        utils.updateElement('theme', general.theme, 'value');
        utils.updateElement('date-format', general.dateFormat, 'value');
        utils.updateElement('items-per-page', general.itemsPerPage, 'value');
    }

    renderScanningSettings() {
        const scanning = this.settings.scanning || {};
        
        utils.updateElement('default-scan-interval', scanning.defaultScanInterval, 'value');
        utils.updateElement('retry-interval', scanning.retryInterval, 'value');
        utils.updateElement('max-retries', scanning.maxRetries, 'value');
        utils.updateElement('concurrent-scans', scanning.concurrentScans, 'value');
        utils.updateElement('request-delay', scanning.requestDelay, 'value');
        utils.updateElement('timeout', scanning.timeout, 'value');
    }

    renderNotificationSettings() {
        const notifications = this.settings.notifications || {};
        
        utils.updateElement('global-notifications', notifications.globalNotifications, 'checked');
        utils.updateElement('quiet-start', notifications.quietStart, 'value');
        utils.updateElement('quiet-end', notifications.quietEnd, 'value');
        utils.updateElement('max-notifications-per-hour', notifications.maxNotificationsPerHour, 'value');
        utils.updateElement('urgent-price-threshold', notifications.urgentPriceThreshold, 'value');
        utils.updateElement('new-property-priority', notifications.newPropertyPriority, 'value');
    }

    renderStorageSettings() {
        const storage = this.settings.storage || {};
        
        utils.updateElement('property-retention', storage.propertyRetention, 'value');
        utils.updateElement('log-retention', storage.logRetention, 'value');
        utils.updateElement('notification-retention', storage.notificationRetention, 'value');
        utils.updateElement('auto-vacuum', storage.autoVacuum, 'checked');
        utils.updateElement('backup-frequency', storage.backupFrequency, 'value');
    }

    renderSecuritySettings() {
        const security = this.settings.security || {};
        
        utils.updateElement('session-timeout', security.sessionTimeout, 'value');
        utils.updateElement('require-password', security.requirePassword, 'checked');
        utils.updateElement('api-rate-limit', security.apiRateLimit, 'value');
        utils.updateElement('enable-cors', security.enableCors, 'checked');
    }

    renderAdvancedSettings() {
        const advanced = this.settings.advanced || {};
        
        utils.updateElement('log-level', advanced.logLevel, 'value');
        utils.updateElement('enable-file-logging', advanced.enableFileLogging, 'checked');
        utils.updateElement('debug-mode', advanced.debugMode, 'checked');
        utils.updateElement('mock-data', advanced.mockData, 'checked');
    }

    markUnsaved() {
        this.unsavedChanges = true;
        
        // Update save button
        const saveBtn = document.querySelector('[onclick="settingsManager.saveAllSettings()"]');
        if (saveBtn) {
            saveBtn.classList.add('btn-warning');
            saveBtn.innerHTML = '<i class="fas fa-save"></i> Save All Settings*';
        }
    }

    clearUnsaved() {
        this.unsavedChanges = false;
        
        // Reset save button
        const saveBtn = document.querySelector('[onclick="settingsManager.saveAllSettings()"]');
        if (saveBtn) {
            saveBtn.classList.remove('btn-warning');
            saveBtn.innerHTML = '<i class="fas fa-save"></i> Save All Settings';
        }
    }

    collectAllSettings() {
        return {
            general: {
                appName: document.getElementById('app-name')?.value || 'RealtyScanner',
                language: document.getElementById('app-language')?.value || 'he',
                timezone: document.getElementById('timezone')?.value || 'Asia/Jerusalem',
                theme: document.getElementById('theme')?.value || 'auto',
                dateFormat: document.getElementById('date-format')?.value || 'DD/MM/YYYY',
                itemsPerPage: parseInt(document.getElementById('items-per-page')?.value) || 25
            },
            scanning: {
                defaultScanInterval: parseInt(document.getElementById('default-scan-interval')?.value) || 30,
                retryInterval: parseInt(document.getElementById('retry-interval')?.value) || 5,
                maxRetries: parseInt(document.getElementById('max-retries')?.value) || 3,
                concurrentScans: parseInt(document.getElementById('concurrent-scans')?.value) || 3,
                requestDelay: parseFloat(document.getElementById('request-delay')?.value) || 1.0,
                timeout: parseInt(document.getElementById('timeout')?.value) || 30
            },
            notifications: {
                globalNotifications: document.getElementById('global-notifications')?.checked || false,
                quietStart: document.getElementById('quiet-start')?.value || '23:00',
                quietEnd: document.getElementById('quiet-end')?.value || '07:00',
                maxNotificationsPerHour: parseInt(document.getElementById('max-notifications-per-hour')?.value) || 10,
                urgentPriceThreshold: parseInt(document.getElementById('urgent-price-threshold')?.value) || 10,
                newPropertyPriority: document.getElementById('new-property-priority')?.value || 'normal'
            },
            storage: {
                propertyRetention: parseInt(document.getElementById('property-retention')?.value) || 90,
                logRetention: parseInt(document.getElementById('log-retention')?.value) || 30,
                notificationRetention: parseInt(document.getElementById('notification-retention')?.value) || 60,
                autoVacuum: document.getElementById('auto-vacuum')?.checked || false,
                backupFrequency: document.getElementById('backup-frequency')?.value || 'daily'
            },
            security: {
                sessionTimeout: parseInt(document.getElementById('session-timeout')?.value) || 60,
                requirePassword: document.getElementById('require-password')?.checked || false,
                apiRateLimit: parseInt(document.getElementById('api-rate-limit')?.value) || 100,
                enableCors: document.getElementById('enable-cors')?.checked || false
            },
            advanced: {
                logLevel: document.getElementById('log-level')?.value || 'INFO',
                enableFileLogging: document.getElementById('enable-file-logging')?.checked || false,
                debugMode: document.getElementById('debug-mode')?.checked || false,
                mockData: document.getElementById('mock-data')?.checked || false
            }
        };
    }

    async saveAllSettings() {
        const settings = this.collectAllSettings();
        
        try {
            utils.showAlert('Saving settings...', 'info');
            const response = await api.put('/settings', settings);
            
            if (response.success) {
                this.settings = settings;
                this.clearUnsaved();
                utils.showAlert('All settings saved successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to save settings:', error);
            utils.showAlert('Failed to save settings', 'error');
        }
    }

    async exportSettings() {
        try {
            const settings = this.collectAllSettings();
            const blob = new Blob([JSON.stringify(settings, null, 2)], 
                { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `realtyscanner_settings_${utils.formatDate(new Date())}.json`;
            a.click();
            URL.revokeObjectURL(url);
            utils.showAlert('Settings exported successfully', 'success');
        } catch (error) {
            console.error('Failed to export settings:', error);
            utils.showAlert('Failed to export settings', 'error');
        }
    }

    importSettings() {
        const input = document.getElementById('import-file-input');
        if (input) {
            input.click();
        }
    }

    async handleImportFile(event) {
        const file = event.target.files[0];
        if (!file) return;

        try {
            const text = await file.text();
            const importedSettings = JSON.parse(text);
            
            // Validate settings structure
            if (!this.validateSettingsStructure(importedSettings)) {
                utils.showAlert('Invalid settings file format', 'error');
                return;
            }

            const confirmed = await utils.confirmDialog(
                'Import settings?',
                'This will replace all current settings. Current settings will be lost.'
            );

            if (!confirmed) return;

            // Apply imported settings
            this.settings = importedSettings;
            this.renderAllSettings();
            this.markUnsaved();
            
            utils.showAlert('Settings imported successfully. Click "Save All Settings" to apply.', 'success');
        } catch (error) {
            console.error('Failed to import settings:', error);
            utils.showAlert('Failed to import settings. Invalid file format.', 'error');
        }

        // Clear file input
        event.target.value = '';
    }

    validateSettingsStructure(settings) {
        const requiredSections = ['general', 'scanning', 'notifications', 'storage', 'security', 'advanced'];
        return requiredSections.every(section => settings.hasOwnProperty(section));
    }

    async resetSettings() {
        const confirmed = await utils.confirmDialog(
            'Reset all settings to defaults?',
            'This will restore all settings to their default values. Current settings will be lost.'
        );

        if (!confirmed) return;

        try {
            const response = await api.post('/settings/reset');
            
            if (response.success) {
                this.settings = this.getDefaultSettings();
                this.renderAllSettings();
                this.clearUnsaved();
                utils.showAlert('Settings reset to defaults', 'success');
            }
        } catch (error) {
            console.error('Failed to reset settings:', error);
            // Reset locally if API fails
            this.settings = this.getDefaultSettings();
            this.renderAllSettings();
            this.markUnsaved();
            utils.showAlert('Settings reset locally. Click "Save All Settings" to apply.', 'warning');
        }
    }

    async clearAllData() {
        const confirmed = await utils.confirmDialog(
            'Clear all application data?',
            'This will delete ALL data including properties, notifications, logs, and settings. This action CANNOT be undone!'
        );

        if (!confirmed) return;

        // Double confirmation for this destructive action
        const doubleConfirmed = await utils.confirmDialog(
            'Are you absolutely sure?',
            'Type "DELETE ALL DATA" to confirm this destructive action.',
            'DELETE ALL DATA'
        );

        if (!doubleConfirmed) return;

        try {
            utils.showAlert('Clearing all data...', 'info');
            const response = await api.post('/settings/clear-all-data');
            
            if (response.success) {
                utils.showAlert('All data cleared successfully. Page will reload.', 'success');
                // Reload page after a delay
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            }
        } catch (error) {
            console.error('Failed to clear data:', error);
            utils.showAlert('Failed to clear data', 'error');
        }
    }

    async createBackup() {
        try {
            utils.showAlert('Creating backup...', 'info');
            const response = await api.post('/settings/backup');
            
            if (response.success) {
                if (response.downloadUrl) {
                    // Direct download
                    const a = document.createElement('a');
                    a.href = response.downloadUrl;
                    a.download = response.filename || `backup_${utils.formatDate(new Date())}.zip`;
                    a.click();
                } else if (response.data) {
                    // Download as blob
                    const blob = new Blob([response.data], { type: 'application/zip' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `backup_${utils.formatDate(new Date())}.zip`;
                    a.click();
                    URL.revokeObjectURL(url);
                }
                utils.showAlert('Backup created successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to create backup:', error);
            utils.showAlert('Failed to create backup', 'error');
        }
    }

    // Helper method for testing individual setting sections
    async saveSectionSettings(sectionName) {
        const allSettings = this.collectAllSettings();
        const sectionSettings = allSettings[sectionName];
        
        if (!sectionSettings) {
            utils.showAlert('Invalid section name', 'error');
            return;
        }

        try {
            const response = await api.put(`/settings/${sectionName}`, sectionSettings);
            
            if (response.success) {
                this.settings[sectionName] = sectionSettings;
                utils.showAlert(`${sectionName.charAt(0).toUpperCase() + sectionName.slice(1)} settings saved`, 'success');
                
                // Update save button if no other unsaved changes
                const otherSectionsChanged = this.checkOtherSectionsChanged(sectionName);
                if (!otherSectionsChanged) {
                    this.clearUnsaved();
                }
            }
        } catch (error) {
            console.error(`Failed to save ${sectionName} settings:`, error);
            utils.showAlert(`Failed to save ${sectionName} settings`, 'error');
        }
    }

    checkOtherSectionsChanged(excludeSection) {
        const currentSettings = this.collectAllSettings();
        const sections = Object.keys(currentSettings);
        
        return sections.some(section => {
            if (section === excludeSection) return false;
            return JSON.stringify(currentSettings[section]) !== JSON.stringify(this.settings[section]);
        });
    }

    // Keyboard shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + S to save
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.saveAllSettings();
            }
            
            // Ctrl/Cmd + E to export
            if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
                e.preventDefault();
                this.exportSettings();
            }
            
            // Ctrl/Cmd + I to import
            if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
                e.preventDefault();
                this.importSettings();
            }
        });
    }
}

// Initialize Settings manager when the page loads
let settingsManager;
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.settings-container')) {
        settingsManager = new SettingsManager();
        settingsManager.setupKeyboardShortcuts();
    }
});
