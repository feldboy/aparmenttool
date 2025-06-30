// Notifications Management Module
class NotificationsManager {
    constructor() {
        this.notifications = [];
        this.rules = [];
        this.channels = {};
        this.settings = {};
        this.init();
    }

    async init() {
        await this.loadNotifications();
        await this.loadRules();
        await this.loadChannels();
        await this.loadSettings();
        this.updateStats();
        this.setupEventListeners();
        this.setupFilters();
    }

    setupEventListeners() {
        // Search and filter event listeners
        const searchInput = document.getElementById('notification-search');
        const typeFilter = document.getElementById('notification-type-filter');
        const statusFilter = document.getElementById('notification-status-filter');
        const dateFilter = document.getElementById('notification-date-filter');

        if (searchInput) {
            searchInput.addEventListener('input', () => this.filterNotifications());
        }
        if (typeFilter) {
            typeFilter.addEventListener('change', () => this.filterNotifications());
        }
        if (statusFilter) {
            statusFilter.addEventListener('change', () => this.filterNotifications());
        }
        if (dateFilter) {
            dateFilter.addEventListener('change', () => this.filterNotifications());
        }

        // Channel settings event listeners
        this.setupChannelEventListeners();
    }

    setupChannelEventListeners() {
        const channelInputs = [
            'telegram-enabled', 'telegram-new-properties', 'telegram-price-changes', 'telegram-system-alerts',
            'email-enabled', 'email-address', 'email-new-properties', 'email-daily-summary', 'email-system-alerts',
            'webpush-enabled', 'webpush-new-properties', 'webpush-urgent-alerts'
        ];

        channelInputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('change', () => this.markSettingsChanged());
            }
        });
    }

    setupFilters() {
        this.currentFilters = {
            search: '',
            type: '',
            status: '',
            date: ''
        };
    }

    async loadNotifications() {
        try {
            const response = await api.get('/notifications');
            this.notifications = response.notifications || [];
            this.renderNotifications();
        } catch (error) {
            console.error('Failed to load notifications:', error);
            this.notifications = this.getMockNotifications();
            this.renderNotifications();
        }
    }

    async loadRules() {
        try {
            const response = await api.get('/notifications/rules');
            this.rules = response.rules || [];
            this.renderRules();
        } catch (error) {
            console.error('Failed to load notification rules:', error);
            this.rules = this.getMockRules();
            this.renderRules();
        }
    }

    async loadChannels() {
        try {
            const response = await api.get('/notifications/channels');
            this.channels = response.channels || this.getDefaultChannels();
            this.renderChannels();
        } catch (error) {
            console.error('Failed to load notification channels:', error);
            this.channels = this.getDefaultChannels();
            this.renderChannels();
        }
    }

    async loadSettings() {
        try {
            const response = await api.get('/notifications/settings');
            this.settings = response.settings || this.getDefaultSettings();
            this.renderSettings();
        } catch (error) {
            console.error('Failed to load notification settings:', error);
            this.settings = this.getDefaultSettings();
            this.renderSettings();
        }
    }

    getDefaultChannels() {
        return {
            telegram: {
                enabled: true,
                status: 'active',
                types: ['new_properties', 'price_changes']
            },
            email: {
                enabled: false,
                status: 'inactive',
                address: '',
                types: []
            },
            webpush: {
                enabled: false,
                status: 'inactive',
                types: []
            }
        };
    }

    getDefaultSettings() {
        return {
            globalEnabled: true,
            quietStart: '23:00',
            quietEnd: '07:00',
            maxPerHour: 10,
            urgentThreshold: 10,
            newPropertyPriority: 'normal'
        };
    }

    getMockNotifications() {
        return [
            {
                id: 1,
                type: 'new_property',
                channel: 'telegram',
                recipient: '@john_doe',
                message: 'New property found in Tel Aviv - 3 rooms, 5,500₪',
                status: 'delivered',
                timestamp: new Date(Date.now() - 30 * 60 * 1000),
                propertyId: 'prop_123'
            },
            {
                id: 2,
                type: 'price_change',
                channel: 'telegram',
                recipient: '@jane_smith',
                message: 'Price dropped for apartment in Ramat Gan - now 4,800₪ (was 5,200₪)',
                status: 'delivered',
                timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
                propertyId: 'prop_456'
            },
            {
                id: 3,
                type: 'system_alert',
                channel: 'email',
                recipient: 'admin@example.com',
                message: 'Yad2 scanning error - rate limit exceeded',
                status: 'failed',
                timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
                error: 'SMTP connection failed'
            }
        ];
    }

    getMockRules() {
        return [
            {
                id: 1,
                name: 'High Priority Properties',
                condition: 'price < 4000 AND rooms >= 3 AND location = "Tel Aviv"',
                actions: ['telegram', 'email'],
                priority: 'high',
                enabled: true
            },
            {
                id: 2,
                name: 'Price Drop Alert',
                condition: 'price_change < -10%',
                actions: ['telegram'],
                priority: 'urgent',
                enabled: true
            },
            {
                id: 3,
                name: 'System Errors',
                condition: 'type = "error"',
                actions: ['email'],
                priority: 'normal',
                enabled: true
            }
        ];
    }

    updateStats() {
        const totalNotifications = this.notifications.length;
        const deliveredNotifications = this.notifications.filter(n => n.status === 'delivered').length;
        const failedNotifications = this.notifications.filter(n => n.status === 'failed').length;
        const pendingNotifications = this.notifications.filter(n => n.status === 'pending').length;

        utils.updateElement('total-notifications', totalNotifications);
        utils.updateElement('delivered-notifications', deliveredNotifications);
        utils.updateElement('failed-notifications', failedNotifications);
        utils.updateElement('pending-notifications', pendingNotifications);
    }

    renderChannels() {
        // Update channel status indicators
        this.updateChannelStatus('telegram', this.channels.telegram);
        this.updateChannelStatus('email', this.channels.email);
        this.updateChannelStatus('webpush', this.channels.webpush);

        // Update channel settings
        utils.updateElement('telegram-enabled', this.channels.telegram.enabled, 'checked');
        utils.updateElement('telegram-new-properties', 
            this.channels.telegram.types.includes('new_properties'), 'checked');
        utils.updateElement('telegram-price-changes', 
            this.channels.telegram.types.includes('price_changes'), 'checked');
        utils.updateElement('telegram-system-alerts', 
            this.channels.telegram.types.includes('system_alerts'), 'checked');

        utils.updateElement('email-enabled', this.channels.email.enabled, 'checked');
        utils.updateElement('email-address', this.channels.email.address || '', 'value');
        utils.updateElement('email-new-properties', 
            this.channels.email.types.includes('new_properties'), 'checked');
        utils.updateElement('email-daily-summary', 
            this.channels.email.types.includes('daily_summary'), 'checked');
        utils.updateElement('email-system-alerts', 
            this.channels.email.types.includes('system_alerts'), 'checked');

        utils.updateElement('webpush-enabled', this.channels.webpush.enabled, 'checked');
        utils.updateElement('webpush-new-properties', 
            this.channels.webpush.types.includes('new_properties'), 'checked');
        utils.updateElement('webpush-urgent-alerts', 
            this.channels.webpush.types.includes('urgent_alerts'), 'checked');
    }

    updateChannelStatus(channelName, channelData) {
        const statusElement = document.getElementById(`${channelName}-status`);
        if (statusElement) {
            const indicator = statusElement.querySelector('.status-indicator');
            const text = statusElement.childNodes[statusElement.childNodes.length - 1];
            
            if (indicator) {
                indicator.className = `status-indicator status-${channelData.status}`;
            }
            if (text) {
                text.textContent = channelData.status === 'active' ? ' Active' : ' Inactive';
            }
        }
    }

    renderSettings() {
        utils.updateElement('global-notifications', this.settings.globalEnabled, 'checked');
        utils.updateElement('quiet-start', this.settings.quietStart, 'value');
        utils.updateElement('quiet-end', this.settings.quietEnd, 'value');
        utils.updateElement('max-notifications-per-hour', this.settings.maxPerHour, 'value');
        utils.updateElement('urgent-price-threshold', this.settings.urgentThreshold, 'value');
        utils.updateElement('new-property-priority', this.settings.newPropertyPriority, 'value');
    }

    renderRules() {
        const rulesContainer = document.getElementById('rules-container');
        if (!rulesContainer) return;

        rulesContainer.innerHTML = this.rules.map(rule => `
            <div class="rule-card">
                <div class="rule-header">
                    <h5>${utils.escapeHtml(rule.name)}</h5>
                    <div class="rule-controls">
                        <span class="priority-badge priority-${rule.priority}">${rule.priority}</span>
                        <div class="toggle-switch">
                            <input type="checkbox" id="rule-${rule.id}" ${rule.enabled ? 'checked' : ''} 
                                   onchange="notificationsManager.toggleRule(${rule.id})">
                            <label for="rule-${rule.id}"></label>
                        </div>
                    </div>
                </div>
                <div class="rule-condition">
                    <strong>Condition:</strong> ${utils.escapeHtml(rule.condition)}
                </div>
                <div class="rule-actions">
                    <strong>Actions:</strong> 
                    ${rule.actions.map(action => `<span class="action-badge">${action}</span>`).join(' ')}
                </div>
                <div class="rule-controls">
                    <button class="btn btn-sm btn-outline-secondary" 
                            onclick="notificationsManager.editRule(${rule.id})">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-outline-danger" 
                            onclick="notificationsManager.deleteRule(${rule.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderNotifications() {
        const tbody = document.getElementById('notifications-table-body');
        const noNotificationsMessage = document.getElementById('no-notifications-message');
        
        if (!tbody) return;

        const filteredNotifications = this.getFilteredNotifications();

        if (filteredNotifications.length === 0) {
            tbody.innerHTML = '';
            if (noNotificationsMessage) noNotificationsMessage.style.display = 'block';
            return;
        }

        if (noNotificationsMessage) noNotificationsMessage.style.display = 'none';

        tbody.innerHTML = filteredNotifications.map(notification => `
            <tr>
                <td>${utils.formatDateTime(notification.timestamp)}</td>
                <td>
                    <span class="type-badge type-${notification.type.replace('_', '-')}">
                        ${this.getTypeText(notification.type)}
                    </span>
                </td>
                <td>
                    <span class="channel-badge channel-${notification.channel}">
                        <i class="fas fa-${this.getChannelIcon(notification.channel)}"></i>
                        ${notification.channel}
                    </span>
                </td>
                <td>${utils.escapeHtml(notification.recipient)}</td>
                <td>
                    <span class="status-badge status-${notification.status}">
                        ${this.getStatusText(notification.status)}
                    </span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-outline-primary" 
                                onclick="notificationsManager.viewNotification(${notification.id})"
                                title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${notification.status === 'failed' ? `
                            <button class="btn btn-sm btn-outline-warning" 
                                    onclick="notificationsManager.retryNotification(${notification.id})"
                                    title="Retry">
                                <i class="fas fa-redo"></i>
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `).join('');

        this.updateStats();
    }

    getFilteredNotifications() {
        let filtered = [...this.notifications];

        // Apply search filter
        if (this.currentFilters.search) {
            const search = this.currentFilters.search.toLowerCase();
            filtered = filtered.filter(notification => 
                notification.message.toLowerCase().includes(search) ||
                notification.recipient.toLowerCase().includes(search)
            );
        }

        // Apply type filter
        if (this.currentFilters.type) {
            filtered = filtered.filter(notification => notification.type === this.currentFilters.type);
        }

        // Apply status filter
        if (this.currentFilters.status) {
            filtered = filtered.filter(notification => notification.status === this.currentFilters.status);
        }

        // Apply date filter
        if (this.currentFilters.date) {
            const filterDate = new Date(this.currentFilters.date);
            filtered = filtered.filter(notification => {
                const notificationDate = new Date(notification.timestamp);
                return notificationDate.toDateString() === filterDate.toDateString();
            });
        }

        return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    }

    filterNotifications() {
        const searchInput = document.getElementById('notification-search');
        const typeFilter = document.getElementById('notification-type-filter');
        const statusFilter = document.getElementById('notification-status-filter');
        const dateFilter = document.getElementById('notification-date-filter');

        this.currentFilters.search = searchInput ? searchInput.value : '';
        this.currentFilters.type = typeFilter ? typeFilter.value : '';
        this.currentFilters.status = statusFilter ? statusFilter.value : '';
        this.currentFilters.date = dateFilter ? dateFilter.value : '';

        this.renderNotifications();
    }

    getTypeText(type) {
        const typeMap = {
            'new_property': 'New Property',
            'price_change': 'Price Change',
            'system_alert': 'System Alert',
            'daily_summary': 'Daily Summary'
        };
        return typeMap[type] || type;
    }

    getChannelIcon(channel) {
        const iconMap = {
            'telegram': 'paper-plane',
            'email': 'envelope',
            'webpush': 'desktop'
        };
        return iconMap[channel] || 'bell';
    }

    getStatusText(status) {
        const statusMap = {
            'delivered': 'Delivered',
            'failed': 'Failed',
            'pending': 'Pending'
        };
        return statusMap[status] || status;
    }

    markSettingsChanged() {
        // Visual feedback for unsaved changes
        const saveBtn = document.querySelector('[onclick="notificationsManager.saveSettings()"]');
        if (saveBtn) {
            saveBtn.classList.add('btn-warning');
            saveBtn.innerHTML = '<i class="fas fa-save"></i> Save Changes*';
        }
    }

    async requestPermission() {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                utils.showAlert('Web push notifications enabled', 'success');
                this.channels.webpush.status = 'active';
                this.updateChannelStatus('webpush', this.channels.webpush);
            } else {
                utils.showAlert('Notification permission denied', 'error');
            }
        } else {
            utils.showAlert('Web notifications not supported', 'error');
        }
    }

    async saveSettings() {
        // Collect channel settings
        const channels = {
            telegram: {
                enabled: document.getElementById('telegram-enabled')?.checked || false,
                types: this.getSelectedTypes('telegram')
            },
            email: {
                enabled: document.getElementById('email-enabled')?.checked || false,
                address: document.getElementById('email-address')?.value || '',
                types: this.getSelectedTypes('email')
            },
            webpush: {
                enabled: document.getElementById('webpush-enabled')?.checked || false,
                types: this.getSelectedTypes('webpush')
            }
        };

        // Update channel status based on enabled state
        Object.keys(channels).forEach(channelName => {
            channels[channelName].status = channels[channelName].enabled ? 'active' : 'inactive';
        });

        try {
            const response = await api.put('/notifications/channels', channels);
            
            if (response.success) {
                this.channels = channels;
                this.renderChannels();
                utils.showAlert('Settings saved successfully', 'success');
                
                // Reset save button appearance
                const saveBtn = document.querySelector('[onclick="notificationsManager.saveSettings()"]');
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

    getSelectedTypes(channelPrefix) {
        const types = [];
        const checkboxes = document.querySelectorAll(`[id^="${channelPrefix}-"]:checked`);
        
        checkboxes.forEach(checkbox => {
            const type = checkbox.id.replace(`${channelPrefix}-`, '').replace('-', '_');
            if (type !== 'enabled') {
                types.push(type);
            }
        });
        
        return types;
    }

    async testNotifications() {
        try {
            utils.showAlert('Sending test notifications...', 'info');
            const response = await api.post('/notifications/test');
            
            if (response.success) {
                utils.showAlert('Test notifications sent successfully', 'success');
                // Refresh notifications to show test messages
                await this.loadNotifications();
            }
        } catch (error) {
            console.error('Failed to send test notifications:', error);
            utils.showAlert('Failed to send test notifications', 'error');
        }
    }

    async showAddRuleModal() {
        await utils.showModal('add-rule-modal', {
            title: 'Add Notification Rule',
            body: `
                <form id="add-rule-form">
                    <div class="form-group">
                        <label for="rule-name">Rule Name</label>
                        <input type="text" id="rule-name" class="form-control" required 
                               placeholder="Enter rule name...">
                    </div>
                    <div class="form-group">
                        <label for="rule-condition">Condition</label>
                        <textarea id="rule-condition" class="form-control" rows="3" required 
                                  placeholder="price < 4000 AND rooms >= 3"></textarea>
                        <small class="form-text text-muted">
                            Use property fields: price, rooms, location, size, etc.
                        </small>
                    </div>
                    <div class="form-group">
                        <label>Actions</label>
                        <div class="checkbox-group">
                            <label class="checkbox-item">
                                <input type="checkbox" value="telegram" checked>
                                <span>Telegram</span>
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" value="email">
                                <span>Email</span>
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" value="webpush">
                                <span>Web Push</span>
                            </label>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="rule-priority">Priority</label>
                        <select id="rule-priority" class="form-control">
                            <option value="low">Low</option>
                            <option value="normal" selected>Normal</option>
                            <option value="high">High</option>
                            <option value="urgent">Urgent</option>
                        </select>
                    </div>
                </form>
            `,
            primaryButton: {
                text: 'Add Rule',
                action: () => this.addRule()
            }
        });
    }

    async addRule() {
        const name = document.getElementById('rule-name')?.value;
        const condition = document.getElementById('rule-condition')?.value;
        const priority = document.getElementById('rule-priority')?.value || 'normal';
        
        const actionCheckboxes = document.querySelectorAll('#add-rule-form input[type="checkbox"]:checked');
        const actions = Array.from(actionCheckboxes).map(cb => cb.value);

        if (!name || !condition || actions.length === 0) {
            utils.showAlert('Please fill in all required fields', 'error');
            return;
        }

        try {
            const newRule = { name, condition, actions, priority, enabled: true };
            const response = await api.post('/notifications/rules', newRule);
            
            if (response.success) {
                this.rules.push({ ...newRule, id: response.id || Date.now() });
                this.renderRules();
                utils.hideModal();
                utils.showAlert('Rule added successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to add rule:', error);
            utils.showAlert('Failed to add rule', 'error');
        }
    }

    async editRule(ruleId) {
        const rule = this.rules.find(r => r.id === ruleId);
        if (!rule) return;

        await utils.showModal('edit-rule-modal', {
            title: 'Edit Notification Rule',
            body: `
                <form id="edit-rule-form">
                    <div class="form-group">
                        <label for="edit-rule-name">Rule Name</label>
                        <input type="text" id="edit-rule-name" class="form-control" 
                               value="${utils.escapeHtml(rule.name)}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-rule-condition">Condition</label>
                        <textarea id="edit-rule-condition" class="form-control" rows="3" required>${utils.escapeHtml(rule.condition)}</textarea>
                    </div>
                    <div class="form-group">
                        <label>Actions</label>
                        <div class="checkbox-group">
                            <label class="checkbox-item">
                                <input type="checkbox" value="telegram" ${rule.actions.includes('telegram') ? 'checked' : ''}>
                                <span>Telegram</span>
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" value="email" ${rule.actions.includes('email') ? 'checked' : ''}>
                                <span>Email</span>
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" value="webpush" ${rule.actions.includes('webpush') ? 'checked' : ''}>
                                <span>Web Push</span>
                            </label>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="edit-rule-priority">Priority</label>
                        <select id="edit-rule-priority" class="form-control">
                            <option value="low" ${rule.priority === 'low' ? 'selected' : ''}>Low</option>
                            <option value="normal" ${rule.priority === 'normal' ? 'selected' : ''}>Normal</option>
                            <option value="high" ${rule.priority === 'high' ? 'selected' : ''}>High</option>
                            <option value="urgent" ${rule.priority === 'urgent' ? 'selected' : ''}>Urgent</option>
                        </select>
                    </div>
                </form>
            `,
            primaryButton: {
                text: 'Save Changes',
                action: () => this.updateRule(ruleId)
            }
        });
    }

    async updateRule(ruleId) {
        const name = document.getElementById('edit-rule-name')?.value;
        const condition = document.getElementById('edit-rule-condition')?.value;
        const priority = document.getElementById('edit-rule-priority')?.value;
        
        const actionCheckboxes = document.querySelectorAll('#edit-rule-form input[type="checkbox"]:checked');
        const actions = Array.from(actionCheckboxes).map(cb => cb.value);

        if (!name || !condition || actions.length === 0) {
            utils.showAlert('Please fill in all required fields', 'error');
            return;
        }

        try {
            const updates = { name, condition, actions, priority };
            const response = await api.put(`/notifications/rules/${ruleId}`, updates);
            
            if (response.success) {
                const ruleIndex = this.rules.findIndex(r => r.id === ruleId);
                if (ruleIndex !== -1) {
                    this.rules[ruleIndex] = { ...this.rules[ruleIndex], ...updates };
                    this.renderRules();
                }
                utils.hideModal();
                utils.showAlert('Rule updated successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to update rule:', error);
            utils.showAlert('Failed to update rule', 'error');
        }
    }

    async deleteRule(ruleId) {
        const rule = this.rules.find(r => r.id === ruleId);
        if (!rule) return;

        const confirmed = await utils.confirmDialog(
            `Delete rule "${rule.name}"?`,
            'This action cannot be undone.'
        );

        if (!confirmed) return;

        try {
            const response = await api.delete(`/notifications/rules/${ruleId}`);
            
            if (response.success) {
                this.rules = this.rules.filter(r => r.id !== ruleId);
                this.renderRules();
                utils.showAlert('Rule deleted successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to delete rule:', error);
            utils.showAlert('Failed to delete rule', 'error');
        }
    }

    async toggleRule(ruleId) {
        const rule = this.rules.find(r => r.id === ruleId);
        if (!rule) return;

        const enabled = document.getElementById(`rule-${ruleId}`)?.checked || false;

        try {
            const response = await api.put(`/notifications/rules/${ruleId}`, { enabled });
            
            if (response.success) {
                rule.enabled = enabled;
                utils.showAlert(`Rule ${enabled ? 'enabled' : 'disabled'}`, 'success');
            }
        } catch (error) {
            console.error('Failed to toggle rule:', error);
            utils.showAlert('Failed to update rule', 'error');
            // Revert checkbox state
            document.getElementById(`rule-${ruleId}`).checked = rule.enabled;
        }
    }

    async viewNotification(notificationId) {
        const notification = this.notifications.find(n => n.id === notificationId);
        if (!notification) return;

        await utils.showModal('view-notification-modal', {
            title: 'Notification Details',
            body: `
                <div class="notification-details">
                    <div class="detail-row">
                        <strong>Type:</strong> ${this.getTypeText(notification.type)}
                    </div>
                    <div class="detail-row">
                        <strong>Channel:</strong> ${notification.channel}
                    </div>
                    <div class="detail-row">
                        <strong>Recipient:</strong> ${utils.escapeHtml(notification.recipient)}
                    </div>
                    <div class="detail-row">
                        <strong>Status:</strong> 
                        <span class="status-badge status-${notification.status}">
                            ${this.getStatusText(notification.status)}
                        </span>
                    </div>
                    <div class="detail-row">
                        <strong>Timestamp:</strong> ${utils.formatDateTime(notification.timestamp)}
                    </div>
                    <div class="detail-row">
                        <strong>Message:</strong>
                        <div class="message-content">${utils.escapeHtml(notification.message)}</div>
                    </div>
                    ${notification.error ? `
                        <div class="detail-row">
                            <strong>Error:</strong>
                            <div class="error-content">${utils.escapeHtml(notification.error)}</div>
                        </div>
                    ` : ''}
                </div>
            `,
            primaryButton: {
                text: 'Close',
                action: () => utils.hideModal()
            }
        });
    }

    async retryNotification(notificationId) {
        const notification = this.notifications.find(n => n.id === notificationId);
        if (!notification) return;

        try {
            utils.showAlert('Retrying notification...', 'info');
            const response = await api.post(`/notifications/${notificationId}/retry`);
            
            if (response.success) {
                notification.status = 'delivered';
                delete notification.error;
                this.renderNotifications();
                utils.showAlert('Notification sent successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to retry notification:', error);
            utils.showAlert('Failed to retry notification', 'error');
        }
    }

    async refreshHistory() {
        await this.loadNotifications();
        utils.showAlert('Notification history refreshed', 'success');
    }

    async exportHistory() {
        try {
            const response = await api.get('/notifications/export');
            
            if (response.success && response.data) {
                const blob = new Blob([JSON.stringify(response.data, null, 2)], 
                    { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `notifications_${utils.formatDate(new Date())}.json`;
                a.click();
                URL.revokeObjectURL(url);
                utils.showAlert('Notification history exported', 'success');
            }
        } catch (error) {
            console.error('Failed to export history:', error);
            utils.showAlert('Failed to export history', 'error');
        }
    }

    async clearHistory() {
        const confirmed = await utils.confirmDialog(
            'Clear notification history?',
            'This will delete all notification history. This action cannot be undone.'
        );

        if (!confirmed) return;

        try {
            const response = await api.delete('/notifications/history');
            
            if (response.success) {
                this.notifications = [];
                this.renderNotifications();
                utils.showAlert('Notification history cleared', 'success');
            }
        } catch (error) {
            console.error('Failed to clear history:', error);
            utils.showAlert('Failed to clear history', 'error');
        }
    }
}

// Initialize Notifications manager when the page loads
let notificationsManager;
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('total-notifications')) {
        notificationsManager = new NotificationsManager();
    }
});
