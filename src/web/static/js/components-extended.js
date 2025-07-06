/**
 * Telegram Component
 * Handles Telegram bot configuration and testing
 */
class TelegramComponent {
    constructor(app) {
        this.app = app;
        this.config = {};
    }

    async load() {
        try {
            await this.loadConfig();
            this.render();
        } catch (error) {
            console.error('Telegram load error:', error);
            this.renderError(error);
        }
    }

    async loadConfig() {
        const response = await this.app.apiClient.call('/telegram/config');
        this.config = response || {};
    }

    render() {
        const chatIdInput = document.getElementById('telegram-chat-id');
        if (chatIdInput && this.config.chat_id) {
            chatIdInput.value = this.config.chat_id;
        }
        
        this.updateConnectionStatus();
    }

    updateConnectionStatus() {
        const statusElement = document.getElementById('telegram-connection-status');
        if (statusElement) {
            const isConnected = this.config.is_connected;
            statusElement.className = `alert ${isConnected ? 'alert-success' : 'alert-warning'}`;
            statusElement.innerHTML = `
                <i class="fas fa-${isConnected ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                ${isConnected ? 'טלגרם מחובר בהצלחה' : 'טלגרם לא מוגדר או מנותק'}
            `;
        }
    }

    async findChatId() {
        const button = document.querySelector('[data-action="find-chat-id"]');
        if (button) {
            button.disabled = true;
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>מחפש...';
        }

        try {
            const response = await this.app.apiClient.call('/telegram/find-chat-id', 'POST');
            
            if (response.chat_id) {
                document.getElementById('telegram-chat-id').value = response.chat_id;
                this.app.utils.showAlert('Chat ID נמצא בהצלחה!', 'success');
            } else {
                this.app.utils.showAlert('לא נמצא Chat ID. ודא ששלחת הודעה לבוט', 'warning');
            }
        } catch (error) {
            console.error('Error finding chat ID:', error);
            this.app.utils.showAlert('שגיאה בחיפוש Chat ID', 'danger');
        } finally {
            if (button) {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-search"></i> חפש';
            }
        }
    }

    async saveConfig() {
        const chatId = document.getElementById('telegram-chat-id').value.trim();
        
        if (!chatId) {
            this.app.utils.showAlert('יש להזין Chat ID', 'warning');
            return;
        }

        const button = document.querySelector('[data-action="save-telegram"]');
        if (button) {
            button.disabled = true;
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>שומר...';
        }

        try {
            await this.app.apiClient.call('/telegram/config', 'POST', {
                chat_id: chatId
            });

            await this.loadConfig();
            this.render();
            this.app.utils.showAlert('הגדרות טלגרם נשמרו בהצלחה', 'success');
        } catch (error) {
            console.error('Error saving telegram config:', error);
            this.app.utils.showAlert('שגיאה בשמירת הגדרות טלגרם', 'danger');
        } finally {
            if (button) {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-save me-2"></i>שמור הגדרות';
            }
        }
    }

    async testConnection() {
        const button = document.querySelector('[data-action="test-telegram"]');
        if (button) {
            button.disabled = true;
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>שולח...';
        }

        try {
            await this.app.apiClient.call('/telegram/test', 'POST');
            this.app.utils.showAlert('הודעת בדיקה נשלחה בהצלחה!', 'success');
        } catch (error) {
            console.error('Error testing telegram:', error);
            this.app.utils.showAlert('שגיאה בשליחת הודעת בדיקה', 'danger');
        } finally {
            if (button) {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-paper-plane me-2"></i>שלח הודעת בדיקה';
            }
        }
    }

    renderError(error) {
        const container = document.getElementById('telegram');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <h5><i class="fas fa-exclamation-triangle me-2"></i>שגיאה בטעינת הגדרות טלגרם</h5>
                    <p>${error.message || 'שגיאה לא ידועה'}</p>
                    <button class="btn btn-outline-danger" onclick="window.realtyApp.components.telegram.load()">
                        נסה שוב
                    </button>
                </div>
            `;
        }
    }
}

/**
 * Facebook Component
 * Handles Facebook scraper configuration
 */
class FacebookComponent {
    constructor(app) {
        this.app = app;
        this.status = {};
    }

    async load() {
        try {
            await this.loadStatus();
            this.render();
        } catch (error) {
            console.error('Facebook load error:', error);
            this.renderError(error);
        }
    }

    async loadStatus() {
        const response = await this.app.apiClient.call('/facebook/status');
        this.status = response || {};
    }

    render() {
        this.updateConnectionStatus();
        this.updateGroupsList();
    }

    updateConnectionStatus() {
        const statusElement = document.getElementById('facebook-status');
        if (statusElement) {
            const isConnected = this.status.is_connected;
            const className = isConnected ? 'text-success' : 'text-warning';
            const icon = isConnected ? 'check-circle' : 'exclamation-triangle';
            const text = isConnected ? 'מחובר' : 'דורש התחברות';
            
            statusElement.innerHTML = `
                <i class="fas fa-${icon} ${className} me-2"></i>
                <span class="${className}">${text}</span>
            `;
        }
    }

    updateGroupsList() {
        const container = document.getElementById('facebook-groups-list');
        if (!container) return;

        const groups = this.status.groups || [];
        
        if (groups.length === 0) {
            container.innerHTML = '<div class="text-muted">אין קבוצות מוגדרות</div>';
            return;
        }

        const groupsHTML = groups.map(group => `
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <strong>${group.name}</strong>
                    <div class="text-muted small">${group.url}</div>
                </div>
                <div>
                    <span class="badge bg-${group.is_active ? 'success' : 'secondary'} me-2">
                        ${group.is_active ? 'פעיל' : 'לא פעיל'}
                    </span>
                    <button class="btn btn-outline-danger btn-sm" 
                            onclick="window.realtyApp.components.facebook.removeGroup('${group.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = groupsHTML;
    }

    async connectFacebook() {
        const button = document.querySelector('[data-action="connect-facebook"]');
        if (button) {
            button.disabled = true;
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>מתחבר...';
        }

        try {
            const response = await this.app.apiClient.call('/facebook/connect', 'POST');
            
            if (response.login_url) {
                window.open(response.login_url, '_blank');
                this.app.utils.showAlert('יש להתחבר בחלון החדש שנפתח', 'info');
            } else {
                await this.loadStatus();
                this.render();
                this.app.utils.showAlert('התחברות לפייסבוק הושלמה', 'success');
            }
        } catch (error) {
            console.error('Error connecting to Facebook:', error);
            this.app.utils.showAlert('שגיאה בהתחברות לפייסבוק', 'danger');
        } finally {
            if (button) {
                button.disabled = false;
                button.innerHTML = '<i class="fab fa-facebook me-2"></i>התחבר לפייסבוק';
            }
        }
    }

    async addGroup() {
        const groupUrl = prompt('הזן URL של קבוצת פייסבוק:');
        if (!groupUrl) return;

        try {
            await this.app.apiClient.call('/facebook/groups', 'POST', {
                url: groupUrl
            });

            await this.loadStatus();
            this.render();
            this.app.utils.showAlert('קבוצה נוספה בהצלחה', 'success');
        } catch (error) {
            console.error('Error adding Facebook group:', error);
            this.app.utils.showAlert('שגיאה בהוספת הקבוצה', 'danger');
        }
    }

    async removeGroup(groupId) {
        if (!confirm('האם אתה בטוח שברצונך להסיר את הקבוצה?')) return;

        try {
            await this.app.apiClient.call(`/facebook/groups/${groupId}`, 'DELETE');
            
            await this.loadStatus();
            this.render();
            this.app.utils.showAlert('קבוצה הוסרה בהצלחה', 'success');
        } catch (error) {
            console.error('Error removing Facebook group:', error);
            this.app.utils.showAlert('שגיאה בהסרת הקבוצה', 'danger');
        }
    }

    renderError(error) {
        const container = document.getElementById('facebook');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <h5><i class="fas fa-exclamation-triangle me-2"></i>שגיאה בטעינת הגדרות פייסבוק</h5>
                    <p>${error.message || 'שגיאה לא ידועה'}</p>
                    <button class="btn btn-outline-danger" onclick="window.realtyApp.components.facebook.load()">
                        נסה שוב
                    </button>
                </div>
            `;
        }
    }
}

/**
 * Yad2 Component
 * Handles Yad2 scraper configuration
 */
class Yad2Component {
    constructor(app) {
        this.app = app;
        this.config = {};
    }

    async load() {
        try {
            await this.loadConfig();
            this.render();
        } catch (error) {
            console.error('Yad2 load error:', error);
            this.renderError(error);
        }
    }

    async loadConfig() {
        const response = await this.app.apiClient.call('/yad2/config');
        this.config = response || {};
    }

    render() {
        this.updateStatus();
        this.updateSettings();
    }

    updateStatus() {
        const statusElement = document.getElementById('yad2-status');
        if (statusElement) {
            const isActive = this.config.is_active;
            statusElement.innerHTML = `
                <span class="badge bg-${isActive ? 'success' : 'secondary'}">
                    ${isActive ? 'פעיל' : 'לא פעיל'}
                </span>
            `;
        }
    }

    updateSettings() {
        const intervalInput = document.getElementById('yad2-scan-interval');
        if (intervalInput && this.config.scan_interval) {
            intervalInput.value = this.config.scan_interval;
        }
    }

    async saveConfig() {
        const scanInterval = document.getElementById('yad2-scan-interval').value;
        
        const button = document.querySelector('[data-action="save-yad2"]');
        if (button) {
            button.disabled = true;
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>שומר...';
        }

        try {
            await this.app.apiClient.call('/yad2/config', 'POST', {
                scan_interval: parseInt(scanInterval) || 5,
                is_active: true
            });

            await this.loadConfig();
            this.render();
            this.app.utils.showAlert('הגדרות יד2 נשמרו בהצלחה', 'success');
        } catch (error) {
            console.error('Error saving Yad2 config:', error);
            this.app.utils.showAlert('שגיאה בשמירת הגדרות יד2', 'danger');
        } finally {
            if (button) {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-save me-2"></i>שמור הגדרות';
            }
        }
    }

    renderError(error) {
        const container = document.getElementById('yad2');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <h5><i class="fas fa-exclamation-triangle me-2"></i>שגיאה בטעינת הגדרות יד2</h5>
                    <p>${error.message || 'שגיאה לא ידועה'}</p>
                    <button class="btn btn-outline-danger" onclick="window.realtyApp.components.yad2.load()">
                        נסה שוב
                    </button>
                </div>
            `;
        }
    }
}

/**
 * Notifications Component
 * Handles notifications management
 */
class NotificationsComponent {
    constructor(app) {
        this.app = app;
        this.notifications = [];
        this.currentPage = 0;
        this.pageSize = 20;
    }

    async load() {
        try {
            await this.loadNotifications();
            this.render();
        } catch (error) {
            console.error('Notifications load error:', error);
            this.renderError(error);
        }
    }

    async loadNotifications(page = 0) {
        const response = await this.app.apiClient.call(
            `/notifications?limit=${this.pageSize}&offset=${page * this.pageSize}`
        );
        
        if (page === 0) {
            this.notifications = response.notifications || [];
        } else {
            this.notifications.push(...(response.notifications || []));
        }
        
        this.currentPage = page;
    }

    render() {
        const container = document.getElementById('notifications-list');
        if (!container) return;

        if (this.notifications.length === 0) {
            container.innerHTML = this.renderEmptyState();
            return;
        }

        const notificationsHTML = this.notifications.map(notification => 
            this.renderNotificationItem(notification)
        ).join('');

        container.innerHTML = notificationsHTML;
    }

    renderEmptyState() {
        return `
            <div class="text-center py-5">
                <i class="fas fa-bell-slash fa-3x text-muted mb-3"></i>
                <h5>אין התראות</h5>
                <p class="text-muted">כאשר יימצאו דירות שמתאימות לפרופילים שלך, תופענה כאן התראות</p>
            </div>
        `;
    }

    renderNotificationItem(notification) {
        return `
            <div class="notification-item border rounded p-3 mb-3">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${notification.property?.title || 'דירה חדשה'}</h6>
                        <p class="text-muted mb-2">${notification.property?.description || ''}</p>
                        <div class="notification-details">
                            <span class="badge bg-primary me-2">${this.app.utils.formatCurrency(notification.property?.price)}</span>
                            <span class="badge bg-secondary me-2">${notification.property?.rooms} חדרים</span>
                            <span class="badge bg-info">${notification.property?.location}</span>
                        </div>
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>
                            ${this.app.utils.formatDate(notification.sent_at)}
                        </small>
                    </div>
                    <div class="notification-actions">
                        ${notification.property?.url ? `
                        <a href="${notification.property.url}" target="_blank" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-external-link-alt"></i> צפה
                        </a>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    renderError(error) {
        const container = document.getElementById('notifications-list');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <h5><i class="fas fa-exclamation-triangle me-2"></i>שגיאה בטעינת התראות</h5>
                    <p>${error.message || 'שגיאה לא ידועה'}</p>
                    <button class="btn btn-outline-danger" onclick="window.realtyApp.components.notifications.load()">
                        נסה שוב
                    </button>
                </div>
            `;
        }
    }
}

/**
 * Settings Component
 * Handles general settings
 */
class SettingsComponent {
    constructor(app) {
        this.app = app;
        this.settings = {};
    }

    async load() {
        try {
            await this.loadSettings();
            this.render();
        } catch (error) {
            console.error('Settings load error:', error);
            this.renderError(error);
        }
    }

    async loadSettings() {
        const response = await this.app.apiClient.call('/settings');
        this.settings = response || {};
    }

    render() {
        // Update form fields with current settings
        Object.keys(this.settings).forEach(key => {
            const input = document.getElementById(`setting-${key}`);
            if (input) {
                input.value = this.settings[key];
            }
        });
    }

    async saveSettings() {
        const button = document.querySelector('[data-action="save-settings"]');
        if (button) {
            button.disabled = true;
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>שומר...';
        }

        try {
            // Collect all setting inputs
            const settingsData = {};
            document.querySelectorAll('[id^="setting-"]').forEach(input => {
                const key = input.id.replace('setting-', '');
                settingsData[key] = input.value;
            });

            await this.app.apiClient.call('/settings', 'POST', settingsData);
            this.app.utils.showAlert('הגדרות נשמרו בהצלחה', 'success');
        } catch (error) {
            console.error('Error saving settings:', error);
            this.app.utils.showAlert('שגיאה בשמירת הגדרות', 'danger');
        } finally {
            if (button) {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-save me-2"></i>שמור הגדרות';
            }
        }
    }

    renderError(error) {
        const container = document.getElementById('settings');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <h5><i class="fas fa-exclamation-triangle me-2"></i>שגיאה בטעינת הגדרות</h5>
                    <p>${error.message || 'שגיאה לא ידועה'}</p>
                    <button class="btn btn-outline-danger" onclick="window.realtyApp.components.settings.load()">
                        נסה שוב
                    </button>
                </div>
            `;
        }
    }
}

// Export all components
window.TelegramComponent = TelegramComponent;
window.FacebookComponent = FacebookComponent;
window.Yad2Component = Yad2Component;
window.NotificationsComponent = NotificationsComponent;
window.SettingsComponent = SettingsComponent;
