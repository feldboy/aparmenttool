// Facebook Management Module  
class FacebookManager {
    constructor() {
        this.groups = [];
        this.settings = {};
        this.isScanning = false;
        this.init();
    }

    async init() {
        await this.loadGroups();
        await this.loadSettings();
        this.updateStats();
        this.setupEventListeners();
        this.setupFilters();
    }

    setupEventListeners() {
        // Search and filter event listeners
        const searchInput = document.getElementById('group-search');
        const statusFilter = document.getElementById('group-status-filter');
        const sortSelect = document.getElementById('group-sort');

        if (searchInput) {
            searchInput.addEventListener('input', () => this.filterGroups());
        }
        if (statusFilter) {
            statusFilter.addEventListener('change', () => this.filterGroups());
        }
        if (sortSelect) {
            sortSelect.addEventListener('change', () => this.filterGroups());
        }

        // Settings event listeners
        const settingsInputs = [
            'scan-interval', 'max-posts', 
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

    async loadGroups() {
        try {
            const response = await api.get('/facebook/groups');
            this.groups = response.groups || [];
            this.renderGroups();
        } catch (error) {
            console.error('Failed to load Facebook groups:', error);
            this.groups = this.getMockGroups();
            this.renderGroups();
        }
    }

    async loadSettings() {
        try {
            const response = await api.get('/facebook/settings');
            this.settings = response.settings || this.getDefaultSettings();
            this.renderSettings();
        } catch (error) {
            console.error('Failed to load Facebook settings:', error);
            this.settings = this.getDefaultSettings();
            this.renderSettings();
        }
    }

    getDefaultSettings() {
        return {
            scanInterval: 60,
            maxPosts: 50,
            enableNotifications: true,
            autoScan: true
        };
    }

    getMockGroups() {
        return [
            {
                id: 1,
                name: 'Tel Aviv Rentals',
                groupId: 'telaviv.rentals.123',
                url: 'https://www.facebook.com/groups/telavivrentals',
                status: 'active',
                lastScan: new Date(Date.now() - 30 * 60 * 1000),
                postsFound: 23,
                created: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000)
            },
            {
                id: 2,
                name: 'Jerusalem Housing',
                groupId: 'jerusalem.housing.456',
                url: 'https://www.facebook.com/groups/jerusalemhousing',
                status: 'active',
                lastScan: new Date(Date.now() - 75 * 60 * 1000),
                postsFound: 18,
                created: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000)
            },
            {
                id: 3,
                name: 'Haifa Apartments',
                groupId: 'haifa.apartments.789',
                url: 'https://www.facebook.com/groups/haifaapartments',
                status: 'inactive',
                lastScan: new Date(Date.now() - 6 * 60 * 60 * 1000),
                postsFound: 7,
                created: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000)
            }
        ];
    }

    updateStats() {
        const totalGroups = this.groups.length;
        const activeGroups = this.groups.filter(group => group.status === 'active').length;
        const totalPosts = this.groups.reduce((sum, group) => sum + (group.postsFound || 0), 0);
        const lastScanTimes = this.groups
            .filter(group => group.lastScan)
            .map(group => new Date(group.lastScan));
        const lastScan = lastScanTimes.length > 0 
            ? Math.max(...lastScanTimes) 
            : null;

        utils.updateElement('total-groups', totalGroups);
        utils.updateElement('active-groups', activeGroups);
        utils.updateElement('posts-found', totalPosts);
        utils.updateElement('last-scan', lastScan ? utils.formatDateTime(lastScan) : 'Never');
    }

    renderGroups() {
        const tbody = document.getElementById('groups-table-body');
        const noGroupsMessage = document.getElementById('no-groups-message');
        
        if (!tbody) return;

        const filteredGroups = this.getFilteredGroups();

        if (filteredGroups.length === 0) {
            tbody.innerHTML = '';
            if (noGroupsMessage) noGroupsMessage.style.display = 'block';
            return;
        }

        if (noGroupsMessage) noGroupsMessage.style.display = 'none';

        tbody.innerHTML = filteredGroups.map(group => `
            <tr>
                <td>
                    <div class="group-info">
                        <strong>${utils.escapeHtml(group.name)}</strong>
                        <small class="text-muted d-block">ID: ${utils.escapeHtml(group.groupId)}</small>
                    </div>
                </td>
                <td>
                    <div class="group-link">
                        <a href="${utils.escapeHtml(group.url)}" target="_blank" class="text-truncate" 
                           title="${utils.escapeHtml(group.url)}">
                            <i class="fab fa-facebook"></i> View Group
                        </a>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${group.status}">
                        ${this.getStatusText(group.status)}
                    </span>
                </td>
                <td>
                    ${group.lastScan ? utils.formatDateTime(group.lastScan) : 'Never'}
                </td>
                <td>
                    <span class="badge badge-info">${group.postsFound || 0}</span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-outline-primary" 
                                onclick="facebookManager.scanGroup(${group.id})"
                                title="Scan Now">
                            <i class="fas fa-search"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" 
                                onclick="facebookManager.editGroup(${group.id})"
                                title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" 
                                onclick="facebookManager.deleteGroup(${group.id})"
                                title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        this.updateStats();
    }

    getFilteredGroups() {
        let filtered = [...this.groups];

        // Apply search filter
        if (this.currentFilters.search) {
            const search = this.currentFilters.search.toLowerCase();
            filtered = filtered.filter(group => 
                group.name.toLowerCase().includes(search) ||
                group.groupId.toLowerCase().includes(search) ||
                group.url.toLowerCase().includes(search)
            );
        }

        // Apply status filter
        if (this.currentFilters.status) {
            filtered = filtered.filter(group => group.status === this.currentFilters.status);
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

    filterGroups() {
        const searchInput = document.getElementById('group-search');
        const statusFilter = document.getElementById('group-status-filter');
        const sortSelect = document.getElementById('group-sort');

        this.currentFilters.search = searchInput ? searchInput.value : '';
        this.currentFilters.status = statusFilter ? statusFilter.value : '';
        this.currentFilters.sort = sortSelect ? sortSelect.value : 'created_desc';

        this.renderGroups();
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
        utils.updateElement('max-posts', this.settings.maxPosts, 'value');
        utils.updateElement('enable-notifications', this.settings.enableNotifications, 'checked');
        utils.updateElement('auto-scan', this.settings.autoScan, 'checked');
    }

    markSettingsChanged() {
        // Visual feedback for unsaved changes
        const saveBtn = document.querySelector('[onclick="facebookManager.saveSettings()"]');
        if (saveBtn) {
            saveBtn.classList.add('btn-warning');
            saveBtn.innerHTML = '<i class="fas fa-save"></i> Save Changes*';
        }
    }

    async showAddGroupModal() {
        await utils.showModal('add-facebook-group-modal', {
            title: 'Add Facebook Group',
            body: `
                <form id="add-group-form">
                    <div class="form-group">
                        <label for="group-name">Group Name</label>
                        <input type="text" id="group-name" class="form-control" required 
                               placeholder="Enter a descriptive name...">
                    </div>
                    <div class="form-group">
                        <label for="group-url">Facebook Group URL</label>
                        <input type="url" id="group-url" class="form-control" required 
                               placeholder="https://www.facebook.com/groups/...">
                        <small class="form-text text-muted">
                            Copy the group URL from Facebook
                        </small>
                    </div>
                    <div class="form-group">
                        <label for="group-id">Group ID (Optional)</label>
                        <input type="text" id="group-id" class="form-control" 
                               placeholder="Will be extracted from URL if not provided">
                    </div>
                    <div class="form-group">
                        <label for="group-status">Status</label>
                        <select id="group-status" class="form-control">
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                        </select>
                    </div>
                </form>
            `,
            primaryButton: {
                text: 'Add Group',
                action: () => this.addGroup()
            }
        });
    }

    async addGroup() {
        const name = document.getElementById('group-name')?.value;
        const url = document.getElementById('group-url')?.value;
        const groupId = document.getElementById('group-id')?.value || this.extractGroupIdFromUrl(url);
        const status = document.getElementById('group-status')?.value || 'active';

        if (!name || !url) {
            utils.showAlert('Please fill in all required fields', 'error');
            return;
        }

        if (!groupId) {
            utils.showAlert('Could not extract Group ID from URL. Please provide it manually.', 'error');
            return;
        }

        try {
            const newGroup = {
                name,
                url,
                groupId,
                status,
                created: new Date(),
                lastScan: null,
                postsFound: 0
            };

            const response = await api.post('/facebook/groups', newGroup);
            
            if (response.success) {
                this.groups.push({ ...newGroup, id: response.id || Date.now() });
                this.renderGroups();
                utils.hideModal();
                utils.showAlert('Group added successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to add group:', error);
            utils.showAlert('Failed to add group', 'error');
        }
    }

    extractGroupIdFromUrl(url) {
        // Extract group ID from Facebook URL
        const match = url.match(/groups\/([^\/\?]+)/);
        return match ? match[1] : null;
    }

    async editGroup(groupId) {
        const group = this.groups.find(g => g.id === groupId);
        if (!group) return;

        await utils.showModal('edit-facebook-group-modal', {
            title: 'Edit Facebook Group',
            body: `
                <form id="edit-group-form">
                    <div class="form-group">
                        <label for="edit-group-name">Group Name</label>
                        <input type="text" id="edit-group-name" class="form-control" 
                               value="${utils.escapeHtml(group.name)}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-group-url">Facebook Group URL</label>
                        <input type="url" id="edit-group-url" class="form-control" 
                               value="${utils.escapeHtml(group.url)}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-group-id">Group ID</label>
                        <input type="text" id="edit-group-id" class="form-control" 
                               value="${utils.escapeHtml(group.groupId)}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-group-status">Status</label>
                        <select id="edit-group-status" class="form-control">
                            <option value="active" ${group.status === 'active' ? 'selected' : ''}>Active</option>
                            <option value="inactive" ${group.status === 'inactive' ? 'selected' : ''}>Inactive</option>
                        </select>
                    </div>
                </form>
            `,
            primaryButton: {
                text: 'Save Changes',
                action: () => this.updateGroup(groupId)
            }
        });
    }

    async updateGroup(groupId) {
        const name = document.getElementById('edit-group-name')?.value;
        const url = document.getElementById('edit-group-url')?.value;
        const groupIdValue = document.getElementById('edit-group-id')?.value;
        const status = document.getElementById('edit-group-status')?.value;

        if (!name || !url || !groupIdValue) {
            utils.showAlert('Please fill in all required fields', 'error');
            return;
        }

        try {
            const updates = { name, url, groupId: groupIdValue, status };
            const response = await api.put(`/facebook/groups/${groupId}`, updates);
            
            if (response.success) {
                const groupIndex = this.groups.findIndex(g => g.id === groupId);
                if (groupIndex !== -1) {
                    this.groups[groupIndex] = { ...this.groups[groupIndex], ...updates };
                    this.renderGroups();
                }
                utils.hideModal();
                utils.showAlert('Group updated successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to update group:', error);
            utils.showAlert('Failed to update group', 'error');
        }
    }

    async deleteGroup(groupId) {
        const group = this.groups.find(g => g.id === groupId);
        if (!group) return;

        const confirmed = await utils.confirmDialog(
            `Are you sure you want to delete "${group.name}"?`,
            'This action cannot be undone.'
        );

        if (!confirmed) return;

        try {
            const response = await api.delete(`/facebook/groups/${groupId}`);
            
            if (response.success) {
                this.groups = this.groups.filter(g => g.id !== groupId);
                this.renderGroups();
                utils.showAlert('Group deleted successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to delete group:', error);
            utils.showAlert('Failed to delete group', 'error');
        }
    }

    async scanGroup(groupId) {
        const group = this.groups.find(g => g.id === groupId);
        if (!group) return;

        try {
            utils.showAlert('Starting scan...', 'info');
            const response = await api.post(`/facebook/groups/${groupId}/scan`);
            
            if (response.success) {
                // Update last scan time
                group.lastScan = new Date();
                group.postsFound = response.postsFound || group.postsFound;
                this.renderGroups();
                utils.showAlert(`Scan completed. Found ${response.postsFound || 0} posts.`, 'success');
            }
        } catch (error) {
            console.error('Failed to scan group:', error);
            utils.showAlert('Failed to scan group', 'error');
        }
    }

    async scanAllGroups() {
        if (this.isScanning) {
            utils.showAlert('Scan already in progress', 'warning');
            return;
        }

        const activeGroups = this.groups.filter(group => group.status === 'active');
        if (activeGroups.length === 0) {
            utils.showAlert('No active groups to scan', 'warning');
            return;
        }

        this.isScanning = true;
        try {
            utils.showAlert(`Scanning ${activeGroups.length} groups...`, 'info');
            const response = await api.post('/facebook/scan-all');
            
            if (response.success) {
                // Update scan times and post counts
                activeGroups.forEach(group => {
                    group.lastScan = new Date();
                    const result = response.results?.find(r => r.groupId === group.id);
                    if (result) {
                        group.postsFound = result.postsFound;
                    }
                });
                this.renderGroups();
                utils.showAlert(
                    `Scan completed. Total posts found: ${response.totalPosts || 0}`, 
                    'success'
                );
            }
        } catch (error) {
            console.error('Failed to scan groups:', error);
            utils.showAlert('Failed to scan groups', 'error');
        } finally {
            this.isScanning = false;
        }
    }

    async saveSettings() {
        const settings = {
            scanInterval: parseInt(document.getElementById('scan-interval')?.value) || 60,
            maxPosts: parseInt(document.getElementById('max-posts')?.value) || 50,
            enableNotifications: document.getElementById('enable-notifications')?.checked || false,
            autoScan: document.getElementById('auto-scan')?.checked || false
        };

        try {
            const response = await api.put('/facebook/settings', settings);
            
            if (response.success) {
                this.settings = settings;
                utils.showAlert('Settings saved successfully', 'success');
                
                // Reset save button appearance
                const saveBtn = document.querySelector('[onclick="facebookManager.saveSettings()"]');
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
            const response = await api.get('/facebook/test-connection');
            
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

// Initialize Facebook manager when the page loads
let facebookManager;
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('total-groups')) {
        facebookManager = new FacebookManager();
    }
});
