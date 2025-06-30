// Telegram Management Module
class TelegramManager {
    constructor() {
        this.users = [];
        this.messages = [];
        this.templates = [];
        this.botStatus = 'offline';
        this.config = {};
        this.init();
    }

    async init() {
        await this.loadConfig();
        await this.loadUsers();
        await this.loadMessages();
        await this.loadTemplates();
        await this.checkBotStatus();
        this.updateStats();
        this.setupEventListeners();
        this.setupFilters();
    }

    setupEventListeners() {
        // Search and filter event listeners
        const userSearch = document.getElementById('user-search');
        const userStatusFilter = document.getElementById('user-status-filter');

        if (userSearch) {
            userSearch.addEventListener('input', () => this.filterUsers());
        }
        if (userStatusFilter) {
            userStatusFilter.addEventListener('change', () => this.filterUsers());
        }

        // Auto-refresh for real-time updates
        this.setupAutoRefresh();
    }

    setupFilters() {
        this.currentFilters = {
            userSearch: '',
            userStatus: ''
        };
    }

    setupAutoRefresh() {
        // Refresh status every 30 seconds
        setInterval(() => {
            this.checkBotStatus();
        }, 30000);

        // Refresh messages every 10 seconds when bot is active
        setInterval(() => {
            if (this.botStatus === 'online') {
                this.refreshMessages();
            }
        }, 10000);
    }

    async loadConfig() {
        try {
            const response = await api.get('/telegram/config');
            this.config = response.config || this.getDefaultConfig();
            this.renderConfig();
        } catch (error) {
            console.error('Failed to load Telegram config:', error);
            this.config = this.getDefaultConfig();
            this.renderConfig();
        }
    }

    async loadUsers() {
        try {
            const response = await api.get('/telegram/users');
            this.users = response.users || [];
            this.renderUsers();
        } catch (error) {
            console.error('Failed to load users:', error);
            this.users = this.getMockUsers();
            this.renderUsers();
        }
    }

    async loadMessages() {
        try {
            const response = await api.get('/telegram/messages');
            this.messages = response.messages || [];
            this.renderMessages();
        } catch (error) {
            console.error('Failed to load messages:', error);
            this.messages = this.getMockMessages();
            this.renderMessages();
        }
    }

    async loadTemplates() {
        try {
            const response = await api.get('/telegram/templates');
            this.templates = response.templates || [];
            this.renderTemplates();
        } catch (error) {
            console.error('Failed to load templates:', error);
            this.templates = this.getMockTemplates();
            this.renderTemplates();
        }
    }

    getDefaultConfig() {
        return {
            botToken: '',
            webhookUrl: '',
            adminChatId: '',
            enableNotifications: true
        };
    }

    getMockUsers() {
        return [
            {
                id: 1,
                userId: '123456789',
                username: 'john_doe',
                firstName: 'John',
                lastName: 'Doe',
                status: 'active',
                lastActivity: new Date(Date.now() - 15 * 60 * 1000),
                messageCount: 23,
                joined: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
            },
            {
                id: 2,
                userId: '987654321',
                username: 'jane_smith',
                firstName: 'Jane',
                lastName: 'Smith',
                status: 'active',
                lastActivity: new Date(Date.now() - 45 * 60 * 1000),
                messageCount: 15,
                joined: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000)
            },
            {
                id: 3,
                userId: '555666777',
                username: 'bob_wilson',
                firstName: 'Bob',
                lastName: 'Wilson',
                status: 'inactive',
                lastActivity: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
                messageCount: 8,
                joined: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000)
            }
        ];
    }

    getMockMessages() {
        return [
            {
                id: 1,
                userId: '123456789',
                username: 'john_doe',
                direction: 'incoming',
                text: '/start',
                timestamp: new Date(Date.now() - 15 * 60 * 1000),
                status: 'delivered'
            },
            {
                id: 2,
                userId: '123456789',
                username: 'john_doe',
                direction: 'outgoing',
                text: 'Welcome to RealtyScanner! Type /help to see available commands.',
                timestamp: new Date(Date.now() - 14 * 60 * 1000),
                status: 'delivered'
            },
            {
                id: 3,
                userId: '987654321',
                username: 'jane_smith',
                direction: 'incoming',
                text: '/search tel aviv 3 rooms',
                timestamp: new Date(Date.now() - 45 * 60 * 1000),
                status: 'delivered'
            }
        ];
    }

    getMockTemplates() {
        return [
            {
                id: 1,
                name: 'Welcome Message',
                content: 'Welcome to RealtyScanner! 🏠\n\nI can help you find apartments and notify you about new listings.\n\nType /help to see available commands.',
                type: 'welcome',
                active: true
            },
            {
                id: 2,
                name: 'New Property Alert',
                content: '🏠 New Property Found!\n\n📍 {location}\n💰 {price}\n🏠 {rooms} rooms\n📏 {size} sqm\n\n🔗 {link}',
                type: 'property_alert',
                active: true
            },
            {
                id: 3,
                name: 'Help Message',
                content: 'Available commands:\n\n/search - Search for properties\n/profile - Manage your search profile\n/notifications - Notification settings\n/help - Show this message',
                type: 'help',
                active: true
            }
        ];
    }

    async checkBotStatus() {
        try {
            const response = await api.get('/telegram/status');
            this.botStatus = response.status || 'offline';
            this.updateBotStatusUI();
        } catch (error) {
            console.error('Failed to check bot status:', error);
            this.botStatus = 'offline';
            this.updateBotStatusUI();
        }
    }

    updateBotStatusUI() {
        const statusElement = document.getElementById('bot-status');
        const startBtn = document.getElementById('start-bot-btn');
        const stopBtn = document.getElementById('stop-bot-btn');

        if (statusElement) {
            statusElement.textContent = this.botStatus === 'online' ? 'Online' : 'Offline';
            statusElement.className = this.botStatus === 'online' ? 'text-success' : 'text-danger';
        }

        if (startBtn && stopBtn) {
            if (this.botStatus === 'online') {
                startBtn.style.display = 'none';
                stopBtn.style.display = 'inline-block';
            } else {
                startBtn.style.display = 'inline-block';
                stopBtn.style.display = 'none';
            }
        }
    }

    updateStats() {
        const activeUsers = this.users.filter(user => user.status === 'active').length;
        const messagesSent = this.messages.filter(msg => msg.direction === 'outgoing').length;
        
        // Calculate uptime (mock data)
        const uptimeHours = this.botStatus === 'online' ? Math.floor(Math.random() * 24) : 0;
        const uptimeMinutes = this.botStatus === 'online' ? Math.floor(Math.random() * 60) : 0;

        utils.updateElement('bot-status', this.botStatus === 'online' ? 'Online' : 'Offline');
        utils.updateElement('active-users', activeUsers);
        utils.updateElement('messages-sent', messagesSent);
        utils.updateElement('uptime', `${uptimeHours}h ${uptimeMinutes}m`);
    }

    renderConfig() {
        utils.updateElement('bot-token', this.config.botToken || '', 'value');
        utils.updateElement('webhook-url', this.config.webhookUrl || '', 'value');
        utils.updateElement('admin-chat-id', this.config.adminChatId || '', 'value');
        utils.updateElement('enable-telegram-notifications', this.config.enableNotifications, 'checked');
    }

    renderUsers() {
        const tbody = document.getElementById('users-table-body');
        const noUsersMessage = document.getElementById('no-users-message');
        
        if (!tbody) return;

        const filteredUsers = this.getFilteredUsers();

        if (filteredUsers.length === 0) {
            tbody.innerHTML = '';
            if (noUsersMessage) noUsersMessage.style.display = 'block';
            return;
        }

        if (noUsersMessage) noUsersMessage.style.display = 'none';

        tbody.innerHTML = filteredUsers.map(user => `
            <tr>
                <td>
                    <div class="user-info">
                        <strong>${utils.escapeHtml(user.firstName || 'Unknown')} ${utils.escapeHtml(user.lastName || '')}</strong>
                        <small class="text-muted d-block">@${utils.escapeHtml(user.username || 'no_username')}</small>
                    </div>
                </td>
                <td>
                    <code>${utils.escapeHtml(user.userId)}</code>
                </td>
                <td>
                    <span class="status-badge status-${user.status}">
                        ${this.getStatusText(user.status)}
                    </span>
                </td>
                <td>
                    ${user.lastActivity ? utils.formatDateTime(user.lastActivity) : 'Never'}
                </td>
                <td>
                    <span class="badge badge-info">${user.messageCount || 0}</span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-outline-primary" 
                                onclick="telegramManager.sendMessage('${user.userId}')"
                                title="Send Message">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-warning" 
                                onclick="telegramManager.blockUser('${user.userId}')"
                                title="Block User">
                            <i class="fas fa-ban"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        this.updateStats();
    }

    getFilteredUsers() {
        let filtered = [...this.users];

        // Apply search filter
        if (this.currentFilters.userSearch) {
            const search = this.currentFilters.userSearch.toLowerCase();
            filtered = filtered.filter(user => 
                (user.firstName && user.firstName.toLowerCase().includes(search)) ||
                (user.lastName && user.lastName.toLowerCase().includes(search)) ||
                (user.username && user.username.toLowerCase().includes(search)) ||
                user.userId.includes(search)
            );
        }

        // Apply status filter
        if (this.currentFilters.userStatus) {
            filtered = filtered.filter(user => user.status === this.currentFilters.userStatus);
        }

        return filtered;
    }

    filterUsers() {
        const userSearch = document.getElementById('user-search');
        const userStatusFilter = document.getElementById('user-status-filter');

        this.currentFilters.userSearch = userSearch ? userSearch.value : '';
        this.currentFilters.userStatus = userStatusFilter ? userStatusFilter.value : '';

        this.renderUsers();
    }

    getStatusText(status) {
        const statusMap = {
            'active': 'Active',
            'inactive': 'Inactive',
            'blocked': 'Blocked'
        };
        return statusMap[status] || status;
    }

    renderTemplates() {
        const templatesGrid = document.getElementById('templates-grid');
        if (!templatesGrid) return;

        templatesGrid.innerHTML = this.templates.map(template => `
            <div class="template-card">
                <div class="template-header">
                    <h5>${utils.escapeHtml(template.name)}</h5>
                    <span class="template-type">${utils.escapeHtml(template.type)}</span>
                </div>
                <div class="template-content">
                    <p>${utils.escapeHtml(utils.truncateText(template.content, 100))}</p>
                </div>
                <div class="template-actions">
                    <button class="btn btn-sm btn-outline-primary" 
                            onclick="telegramManager.editTemplate(${template.id})">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" 
                            onclick="telegramManager.testTemplate(${template.id})">
                        <i class="fas fa-paper-plane"></i> Test
                    </button>
                    <button class="btn btn-sm btn-outline-danger" 
                            onclick="telegramManager.deleteTemplate(${template.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderMessages() {
        const messagesContainer = document.getElementById('messages-container');
        if (!messagesContainer) return;

        const recentMessages = this.messages.slice(-50).reverse(); // Show last 50 messages

        messagesContainer.innerHTML = recentMessages.map(message => `
            <div class="message-item ${message.direction}">
                <div class="message-header">
                    <span class="message-user">@${utils.escapeHtml(message.username)}</span>
                    <span class="message-time">${utils.formatDateTime(message.timestamp)}</span>
                    <span class="message-direction">
                        <i class="fas fa-${message.direction === 'incoming' ? 'arrow-down' : 'arrow-up'}"></i>
                    </span>
                </div>
                <div class="message-content">
                    ${utils.escapeHtml(message.text)}
                </div>
            </div>
        `).join('');
    }

    async startBot() {
        try {
            utils.showAlert('Starting bot...', 'info');
            const response = await api.post('/telegram/start');
            
            if (response.success) {
                this.botStatus = 'online';
                this.updateBotStatusUI();
                this.updateStats();
                utils.showAlert('Bot started successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to start bot:', error);
            utils.showAlert('Failed to start bot', 'error');
        }
    }

    async stopBot() {
        try {
            utils.showAlert('Stopping bot...', 'info');
            const response = await api.post('/telegram/stop');
            
            if (response.success) {
                this.botStatus = 'offline';
                this.updateBotStatusUI();
                this.updateStats();
                utils.showAlert('Bot stopped successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to stop bot:', error);
            utils.showAlert('Failed to stop bot', 'error');
        }
    }

    async restartBot() {
        try {
            utils.showAlert('Restarting bot...', 'info');
            const response = await api.post('/telegram/restart');
            
            if (response.success) {
                await this.checkBotStatus();
                this.updateStats();
                utils.showAlert('Bot restarted successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to restart bot:', error);
            utils.showAlert('Failed to restart bot', 'error');
        }
    }

    toggleTokenVisibility() {
        const tokenInput = document.getElementById('bot-token');
        const eyeIcon = document.getElementById('token-eye');
        
        if (tokenInput && eyeIcon) {
            if (tokenInput.type === 'password') {
                tokenInput.type = 'text';
                eyeIcon.className = 'fas fa-eye-slash';
            } else {
                tokenInput.type = 'password';
                eyeIcon.className = 'fas fa-eye';
            }
        }
    }

    async saveConfig() {
        const config = {
            botToken: document.getElementById('bot-token')?.value || '',
            webhookUrl: document.getElementById('webhook-url')?.value || '',
            adminChatId: document.getElementById('admin-chat-id')?.value || '',
            enableNotifications: document.getElementById('enable-telegram-notifications')?.checked || false
        };

        try {
            const response = await api.put('/telegram/config', config);
            
            if (response.success) {
                this.config = config;
                utils.showAlert('Configuration saved successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to save configuration:', error);
            utils.showAlert('Failed to save configuration', 'error');
        }
    }

    async testBot() {
        try {
            utils.showAlert('Testing bot...', 'info');
            const response = await api.post('/telegram/test');
            
            if (response.success) {
                utils.showAlert('Bot test successful', 'success');
            } else {
                utils.showAlert('Bot test failed', 'error');
            }
        } catch (error) {
            console.error('Bot test failed:', error);
            utils.showAlert('Bot test failed', 'error');
        }
    }

    async refreshUsers() {
        await this.loadUsers();
        utils.showAlert('Users refreshed', 'success');
    }

    async refreshMessages() {
        await this.loadMessages();
    }

    async clearMessages() {
        const confirmed = await utils.confirmDialog(
            'Clear message history?',
            'This will delete all message history. This action cannot be undone.'
        );

        if (!confirmed) return;

        try {
            const response = await api.delete('/telegram/messages');
            
            if (response.success) {
                this.messages = [];
                this.renderMessages();
                utils.showAlert('Message history cleared', 'success');
            }
        } catch (error) {
            console.error('Failed to clear messages:', error);
            utils.showAlert('Failed to clear message history', 'error');
        }
    }

    async sendMessage(userId) {
        await utils.showModal('send-message-modal', {
            title: 'Send Message',
            body: `
                <form id="send-message-form">
                    <div class="form-group">
                        <label for="message-text">Message</label>
                        <textarea id="message-text" class="form-control" rows="4" 
                                  placeholder="Enter your message..." required></textarea>
                    </div>
                </form>
            `,
            primaryButton: {
                text: 'Send Message',
                action: () => this.doSendMessage(userId)
            }
        });
    }

    async doSendMessage(userId) {
        const messageText = document.getElementById('message-text')?.value;

        if (!messageText) {
            utils.showAlert('Please enter a message', 'error');
            return;
        }

        try {
            const response = await api.post('/telegram/send-message', {
                userId,
                message: messageText
            });
            
            if (response.success) {
                utils.hideModal();
                utils.showAlert('Message sent successfully', 'success');
                // Add to local messages for immediate UI update
                this.messages.push({
                    id: Date.now(),
                    userId,
                    direction: 'outgoing',
                    text: messageText,
                    timestamp: new Date(),
                    status: 'delivered'
                });
                this.renderMessages();
            }
        } catch (error) {
            console.error('Failed to send message:', error);
            utils.showAlert('Failed to send message', 'error');
        }
    }

    async blockUser(userId) {
        const user = this.users.find(u => u.userId === userId);
        if (!user) return;

        const confirmed = await utils.confirmDialog(
            `Block user @${user.username}?`,
            'This user will no longer be able to interact with the bot.'
        );

        if (!confirmed) return;

        try {
            const response = await api.post(`/telegram/users/${userId}/block`);
            
            if (response.success) {
                user.status = 'blocked';
                this.renderUsers();
                utils.showAlert('User blocked successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to block user:', error);
            utils.showAlert('Failed to block user', 'error');
        }
    }

    async showAddTemplateModal() {
        await utils.showModal('add-template-modal', {
            title: 'Add Message Template',
            body: `
                <form id="add-template-form">
                    <div class="form-group">
                        <label for="template-name">Name</label>
                        <input type="text" id="template-name" class="form-control" required 
                               placeholder="Enter template name...">
                    </div>
                    <div class="form-group">
                        <label for="template-type">Type</label>
                        <select id="template-type" class="form-control">
                            <option value="welcome">Welcome</option>
                            <option value="help">Help</option>
                            <option value="property_alert">Property Alert</option>
                            <option value="custom">Custom</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="template-content">Content</label>
                        <textarea id="template-content" class="form-control" rows="6" 
                                  placeholder="Enter template content..." required></textarea>
                        <small class="form-text text-muted">
                            Use {variable} syntax for dynamic content
                        </small>
                    </div>
                </form>
            `,
            primaryButton: {
                text: 'Add Template',
                action: () => this.addTemplate()
            }
        });
    }

    async addTemplate() {
        const name = document.getElementById('template-name')?.value;
        const type = document.getElementById('template-type')?.value;
        const content = document.getElementById('template-content')?.value;

        if (!name || !content) {
            utils.showAlert('Please fill in all required fields', 'error');
            return;
        }

        try {
            const newTemplate = { name, type, content, active: true };
            const response = await api.post('/telegram/templates', newTemplate);
            
            if (response.success) {
                this.templates.push({ ...newTemplate, id: response.id || Date.now() });
                this.renderTemplates();
                utils.hideModal();
                utils.showAlert('Template added successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to add template:', error);
            utils.showAlert('Failed to add template', 'error');
        }
    }

    async editTemplate(templateId) {
        const template = this.templates.find(t => t.id === templateId);
        if (!template) return;

        await utils.showModal('edit-template-modal', {
            title: 'Edit Message Template',
            body: `
                <form id="edit-template-form">
                    <div class="form-group">
                        <label for="edit-template-name">Name</label>
                        <input type="text" id="edit-template-name" class="form-control" 
                               value="${utils.escapeHtml(template.name)}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-template-type">Type</label>
                        <select id="edit-template-type" class="form-control">
                            <option value="welcome" ${template.type === 'welcome' ? 'selected' : ''}>Welcome</option>
                            <option value="help" ${template.type === 'help' ? 'selected' : ''}>Help</option>
                            <option value="property_alert" ${template.type === 'property_alert' ? 'selected' : ''}>Property Alert</option>
                            <option value="custom" ${template.type === 'custom' ? 'selected' : ''}>Custom</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="edit-template-content">Content</label>
                        <textarea id="edit-template-content" class="form-control" rows="6" required>${utils.escapeHtml(template.content)}</textarea>
                    </div>
                </form>
            `,
            primaryButton: {
                text: 'Save Changes',
                action: () => this.updateTemplate(templateId)
            }
        });
    }

    async updateTemplate(templateId) {
        const name = document.getElementById('edit-template-name')?.value;
        const type = document.getElementById('edit-template-type')?.value;
        const content = document.getElementById('edit-template-content')?.value;

        if (!name || !content) {
            utils.showAlert('Please fill in all required fields', 'error');
            return;
        }

        try {
            const updates = { name, type, content };
            const response = await api.put(`/telegram/templates/${templateId}`, updates);
            
            if (response.success) {
                const templateIndex = this.templates.findIndex(t => t.id === templateId);
                if (templateIndex !== -1) {
                    this.templates[templateIndex] = { ...this.templates[templateIndex], ...updates };
                    this.renderTemplates();
                }
                utils.hideModal();
                utils.showAlert('Template updated successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to update template:', error);
            utils.showAlert('Failed to update template', 'error');
        }
    }

    async deleteTemplate(templateId) {
        const template = this.templates.find(t => t.id === templateId);
        if (!template) return;

        const confirmed = await utils.confirmDialog(
            `Delete template "${template.name}"?`,
            'This action cannot be undone.'
        );

        if (!confirmed) return;

        try {
            const response = await api.delete(`/telegram/templates/${templateId}`);
            
            if (response.success) {
                this.templates = this.templates.filter(t => t.id !== templateId);
                this.renderTemplates();
                utils.showAlert('Template deleted successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to delete template:', error);
            utils.showAlert('Failed to delete template', 'error');
        }
    }

    async testTemplate(templateId) {
        const template = this.templates.find(t => t.id === templateId);
        if (!template) return;

        await utils.showModal('test-template-modal', {
            title: 'Test Template',
            body: `
                <div class="template-preview">
                    <h6>Template Preview:</h6>
                    <div class="preview-content">${utils.escapeHtml(template.content)}</div>
                </div>
                <form id="test-template-form">
                    <div class="form-group">
                        <label for="test-chat-id">Test Chat ID</label>
                        <input type="text" id="test-chat-id" class="form-control" 
                               placeholder="Enter chat ID to send test message">
                        <small class="form-text text-muted">
                            Leave empty to send to admin chat
                        </small>
                    </div>
                </form>
            `,
            primaryButton: {
                text: 'Send Test',
                action: () => this.doTestTemplate(templateId)
            }
        });
    }

    async doTestTemplate(templateId) {
        const template = this.templates.find(t => t.id === templateId);
        if (!template) return;

        const chatId = document.getElementById('test-chat-id')?.value || this.config.adminChatId;

        if (!chatId) {
            utils.showAlert('Please enter a chat ID or configure admin chat ID', 'error');
            return;
        }

        try {
            const response = await api.post('/telegram/test-template', {
                templateId,
                chatId
            });
            
            if (response.success) {
                utils.hideModal();
                utils.showAlert('Test message sent successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to send test message:', error);
            utils.showAlert('Failed to send test message', 'error');
        }
    }
}

// Initialize Telegram manager when the page loads
let telegramManager;
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('bot-status')) {
        telegramManager = new TelegramManager();
    }
});
