// Yad2 Management Module
class Yad2Manager {
    constructor() {
        this.urls = [];
        this.settings = {};
        this.isScanning = false;
        this.init();
    }

    async init() {
        await this.loadUrls();
        await this.loadSettings();
        this.updateStats();
        this.setupEventListeners();
        this.setupFilters();
    }

    setupEventListeners() {
        // Search and filter event listeners
        const searchInput = document.getElementById('url-search');
        const statusFilter = document.getElementById('url-status-filter');
        const sortSelect = document.getElementById('url-sort');

        if (searchInput) {
            searchInput.addEventListener('input', () => this.filterUrls());
        }
        if (statusFilter) {
            statusFilter.addEventListener('change', () => this.filterUrls());
        }
        if (sortSelect) {
            sortSelect.addEventListener('change', () => this.filterUrls());
        }

        // Settings event listeners
        const settingsInputs = [
            'scan-interval', 'max-properties', 
            'enable-notifications', 'auto-scan'
        ];
        settingsInputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('change', () => this.markSettingsChanged());
            }
        });
    }

    setupFilters() {
        this.currentFilters = {
            search: '',
            status: '',
            sort: 'created_desc'
        };
    }

    async loadUrls() {
        try {
            const response = await api.get('/yad2/urls');
            this.urls = response.urls || [];
            this.renderUrls();
        } catch (error) {
            console.error('Failed to load Yad2 URLs:', error);
            this.urls = this.getMockUrls();
            this.renderUrls();
        }
    }

    async loadSettings() {
        try {
            const response = await api.get('/yad2/settings');
            this.settings = response.settings || this.getDefaultSettings();
            this.renderSettings();
        } catch (error) {
            console.error('Failed to load Yad2 settings:', error);
            this.settings = this.getDefaultSettings();
            this.renderSettings();
        }
    }

    getDefaultSettings() {
        return {
            scanInterval: 30,
            maxProperties: 100,
            enableNotifications: true,
            autoScan: true
        };
    }

    getMockUrls() {
        return [
            {
                id: 1,
                name: 'Tel Aviv 3 Rooms',
                url: 'https://www.yad2.co.il/realestate/rent?city=5000&rooms=3-3',
                status: 'active',
                lastScan: new Date(Date.now() - 15 * 60 * 1000),
                propertiesFound: 45,
                created: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
            },
            {
                id: 2,
                name: 'Ramat Gan 2-3 Rooms',
                url: 'https://www.yad2.co.il/realestate/rent?city=8600&rooms=2-3',
                status: 'active',
                lastScan: new Date(Date.now() - 45 * 60 * 1000),
                propertiesFound: 23,
                created: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000)
            },
            {
                id: 3,
                name: 'Herzliya Luxury',
                url: 'https://www.yad2.co.il/realestate/rent?city=3500&priceFrom=8000',
                status: 'inactive',
                lastScan: new Date(Date.now() - 4 * 60 * 60 * 1000),
                propertiesFound: 12,
                created: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000)
            }
        ];
    }

    updateStats() {
        const totalUrls = this.urls.length;
        const activeUrls = this.urls.filter(url => url.status === 'active').length;
        const totalProperties = this.urls.reduce((sum, url) => sum + (url.propertiesFound || 0), 0);
        const lastScanTimes = this.urls
            .filter(url => url.lastScan)
            .map(url => new Date(url.lastScan));
        const lastScan = lastScanTimes.length > 0 
            ? Math.max(...lastScanTimes) 
            : null;

        utils.updateElement('total-urls', totalUrls);
        utils.updateElement('active-urls', activeUrls);
        utils.updateElement('properties-found', totalProperties);
        utils.updateElement('last-scan', lastScan ? utils.formatDateTime(lastScan) : 'Never');
    }

    renderUrls() {
        const tbody = document.getElementById('urls-table-body');
        const noUrlsMessage = document.getElementById('no-urls-message');
        
        if (!tbody) return;

        const filteredUrls = this.getFilteredUrls();

        if (filteredUrls.length === 0) {
            tbody.innerHTML = '';
            if (noUrlsMessage) noUrlsMessage.style.display = 'block';
            return;
        }

        if (noUrlsMessage) noUrlsMessage.style.display = 'none';

        tbody.innerHTML = filteredUrls.map(url => `
            <tr>
                <td>
                    <div class="url-info">
                        <strong>${utils.escapeHtml(url.name)}</strong>
                    </div>
                </td>
                <td>
                    <div class="url-link">
                        <a href="${utils.escapeHtml(url.url)}" target="_blank" class="text-truncate" 
                           title="${utils.escapeHtml(url.url)}">
                            ${utils.truncateText(url.url, 50)}
                        </a>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${url.status}">
                        ${this.getStatusText(url.status)}
                    </span>
                </td>
                <td>
                    ${url.lastScan ? utils.formatDateTime(url.lastScan) : 'Never'}
                </td>
                <td>
                    <span class="badge badge-info">${url.propertiesFound || 0}</span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-outline-primary" 
                                onclick="yad2Manager.scanUrl(${url.id})"
                                title="Scan Now">
                            <i class="fas fa-search"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" 
                                onclick="yad2Manager.editUrl(${url.id})"
                                title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" 
                                onclick="yad2Manager.deleteUrl(${url.id})"
                                title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        this.updateStats();
    }

    getFilteredUrls() {
        let filtered = [...this.urls];

        // Apply search filter
        if (this.currentFilters.search) {
            const search = this.currentFilters.search.toLowerCase();
            filtered = filtered.filter(url => 
                url.name.toLowerCase().includes(search) ||
                url.url.toLowerCase().includes(search)
            );
        }

        // Apply status filter
        if (this.currentFilters.status) {
            filtered = filtered.filter(url => url.status === this.currentFilters.status);
        }

        // Apply sorting
        filtered.sort((a, b) => {
            switch (this.currentFilters.sort) {
                case 'created_asc':
                    return new Date(a.created) - new Date(b.created);
                case 'created_desc':
                    return new Date(b.created) - new Date(a.created);
                case 'name_asc':
                    return a.name.localeCompare(b.name);
                case 'name_desc':
                    return b.name.localeCompare(a.name);
                case 'last_scan':
                    return new Date(b.lastScan || 0) - new Date(a.lastScan || 0);
                default:
                    return 0;
            }
        });

        return filtered;
    }

    filterUrls() {
        const searchInput = document.getElementById('url-search');
        const statusFilter = document.getElementById('url-status-filter');
        const sortSelect = document.getElementById('url-sort');

        this.currentFilters.search = searchInput ? searchInput.value : '';
        this.currentFilters.status = statusFilter ? statusFilter.value : '';
        this.currentFilters.sort = sortSelect ? sortSelect.value : 'created_desc';

        this.renderUrls();
    }

    getStatusText(status) {
        const statusMap = {
            'active': 'Active',
            'inactive': 'Inactive',
            'error': 'Error'
        };
        return statusMap[status] || status;
    }

    renderSettings() {
        utils.updateElement('scan-interval', this.settings.scanInterval, 'value');
        utils.updateElement('max-properties', this.settings.maxProperties, 'value');
        utils.updateElement('enable-notifications', this.settings.enableNotifications, 'checked');
        utils.updateElement('auto-scan', this.settings.autoScan, 'checked');
    }

    markSettingsChanged() {
        // Visual feedback for unsaved changes
        const saveBtn = document.querySelector('[onclick="yad2Manager.saveSettings()"]');
        if (saveBtn) {
            saveBtn.classList.add('btn-warning');
            saveBtn.innerHTML = '<i class="fas fa-save"></i> Save Changes*';
        }
    }

    async showAddUrlModal() {
        await utils.showModal('add-yad2-url-modal', {
            title: 'Add Yad2 URL',
            body: `
                <form id="add-url-form">
                    <div class="form-group">
                        <label for="url-name">Name</label>
                        <input type="text" id="url-name" class="form-control" required 
                               placeholder="Enter a descriptive name...">
                    </div>
                    <div class="form-group">
                        <label for="url-value">Yad2 URL</label>
                        <input type="url" id="url-value" class="form-control" required 
                               placeholder="https://www.yad2.co.il/realestate/rent?...">
                        <small class="form-text text-muted">
                            Copy the search URL from Yad2 website
                        </small>
                    </div>
                    <div class="form-group">
                        <label for="url-status">Status</label>
                        <select id="url-status" class="form-control">
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                        </select>
                    </div>
                </form>
            `,
            primaryButton: {
                text: 'Add URL',
                action: () => this.addUrl()
            }
        });
    }

    async addUrl() {
        const name = document.getElementById('url-name')?.value;
        const url = document.getElementById('url-value')?.value;
        const status = document.getElementById('url-status')?.value || 'active';

        if (!name || !url) {
            utils.showAlert('Please fill in all required fields', 'error');
            return;
        }

        try {
            const newUrl = {
                name,
                url,
                status,
                created: new Date(),
                lastScan: null,
                propertiesFound: 0
            };

            const response = await api.post('/yad2/urls', newUrl);
            
            if (response.success) {
                this.urls.push({ ...newUrl, id: response.id || Date.now() });
                this.renderUrls();
                utils.hideModal();
                utils.showAlert('URL added successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to add URL:', error);
            utils.showAlert('Failed to add URL', 'error');
        }
    }

    async editUrl(urlId) {
        const url = this.urls.find(u => u.id === urlId);
        if (!url) return;

        await utils.showModal('edit-yad2-url-modal', {
            title: 'Edit Yad2 URL',
            body: `
                <form id="edit-url-form">
                    <div class="form-group">
                        <label for="edit-url-name">Name</label>
                        <input type="text" id="edit-url-name" class="form-control" 
                               value="${utils.escapeHtml(url.name)}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-url-value">Yad2 URL</label>
                        <input type="url" id="edit-url-value" class="form-control" 
                               value="${utils.escapeHtml(url.url)}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-url-status">Status</label>
                        <select id="edit-url-status" class="form-control">
                            <option value="active" ${url.status === 'active' ? 'selected' : ''}>Active</option>
                            <option value="inactive" ${url.status === 'inactive' ? 'selected' : ''}>Inactive</option>
                        </select>
                    </div>
                </form>
            `,
            primaryButton: {
                text: 'Save Changes',
                action: () => this.updateUrl(urlId)
            }
        });
    }

    async updateUrl(urlId) {
        const name = document.getElementById('edit-url-name')?.value;
        const url = document.getElementById('edit-url-value')?.value;
        const status = document.getElementById('edit-url-status')?.value;

        if (!name || !url) {
            utils.showAlert('Please fill in all required fields', 'error');
            return;
        }

        try {
            const updates = { name, url, status };
            const response = await api.put(`/yad2/urls/${urlId}`, updates);
            
            if (response.success) {
                const urlIndex = this.urls.findIndex(u => u.id === urlId);
                if (urlIndex !== -1) {
                    this.urls[urlIndex] = { ...this.urls[urlIndex], ...updates };
                    this.renderUrls();
                }
                utils.hideModal();
                utils.showAlert('URL updated successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to update URL:', error);
            utils.showAlert('Failed to update URL', 'error');
        }
    }

    async deleteUrl(urlId) {
        const url = this.urls.find(u => u.id === urlId);
        if (!url) return;

        const confirmed = await utils.confirmDialog(
            `Are you sure you want to delete "${url.name}"?`,
            'This action cannot be undone.'
        );

        if (!confirmed) return;

        try {
            const response = await api.delete(`/yad2/urls/${urlId}`);
            
            if (response.success) {
                this.urls = this.urls.filter(u => u.id !== urlId);
                this.renderUrls();
                utils.showAlert('URL deleted successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to delete URL:', error);
            utils.showAlert('Failed to delete URL', 'error');
        }
    }

    async scanUrl(urlId) {
        const url = this.urls.find(u => u.id === urlId);
        if (!url) return;

        try {
            utils.showAlert('Starting scan...', 'info');
            const response = await api.post(`/yad2/urls/${urlId}/scan`);
            
            if (response.success) {
                // Update last scan time
                url.lastScan = new Date();
                url.propertiesFound = response.propertiesFound || url.propertiesFound;
                this.renderUrls();
                utils.showAlert(`Scan completed. Found ${response.propertiesFound || 0} properties.`, 'success');
            }
        } catch (error) {
            console.error('Failed to scan URL:', error);
            utils.showAlert('Failed to scan URL', 'error');
        }
    }

    async scanAllUrls() {
        if (this.isScanning) {
            utils.showAlert('Scan already in progress', 'warning');
            return;
        }

        const activeUrls = this.urls.filter(url => url.status === 'active');
        if (activeUrls.length === 0) {
            utils.showAlert('No active URLs to scan', 'warning');
            return;
        }

        this.isScanning = true;
        try {
            utils.showAlert(`Scanning ${activeUrls.length} URLs...`, 'info');
            const response = await api.post('/yad2/scan-all');
            
            if (response.success) {
                // Update scan times and property counts
                activeUrls.forEach(url => {
                    url.lastScan = new Date();
                    const result = response.results?.find(r => r.urlId === url.id);
                    if (result) {
                        url.propertiesFound = result.propertiesFound;
                    }
                });
                this.renderUrls();
                utils.showAlert(
                    `Scan completed. Total properties found: ${response.totalProperties || 0}`, 
                    'success'
                );
            }
        } catch (error) {
            console.error('Failed to scan URLs:', error);
            utils.showAlert('Failed to scan URLs', 'error');
        } finally {
            this.isScanning = false;
        }
    }

    async saveSettings() {
        const settings = {
            scanInterval: parseInt(document.getElementById('scan-interval')?.value) || 30,
            maxProperties: parseInt(document.getElementById('max-properties')?.value) || 100,
            enableNotifications: document.getElementById('enable-notifications')?.checked || false,
            autoScan: document.getElementById('auto-scan')?.checked || false
        };

        try {
            const response = await api.put('/yad2/settings', settings);
            
            if (response.success) {
                this.settings = settings;
                utils.showAlert('Settings saved successfully', 'success');
                
                // Reset save button appearance
                const saveBtn = document.querySelector('[onclick="yad2Manager.saveSettings()"]');
                if (saveBtn) {
                    saveBtn.classList.remove('btn-warning');
                    saveBtn.innerHTML = '<i class="fas fa-save"></i> Save Settings';
                }
            }
        } catch (error) {
            console.error('Failed to save settings:', error);
            utils.showAlert('Failed to save settings', 'error');
        }
    }

    async testConnection() {
        try {
            utils.showAlert('Testing connection...', 'info');
            const response = await api.get('/yad2/test-connection');
            
            if (response.success) {
                utils.showAlert('Connection test successful', 'success');
            } else {
                utils.showAlert('Connection test failed', 'error');
            }
        } catch (error) {
            console.error('Connection test failed:', error);
            utils.showAlert('Connection test failed', 'error');
        }
    }
}

// Initialize Yad2 manager when the page loads
let yad2Manager;
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('total-urls')) {
        yad2Manager = new Yad2Manager();
    }
});
