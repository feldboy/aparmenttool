/**
 * Dashboard Component
 * Handles the main dashboard view with metrics and status
 */
class DashboardComponent {
    constructor(app) {
        this.app = app;
        this.data = {
            metrics: {},
            systemStatus: {},
            recentActivity: []
        };
    }

    async load() {
        try {
            await this.loadData();
            this.render();
        } catch (error) {
            console.error('Dashboard load error:', error);
            this.renderError(error);
        }
    }

    async loadData() {
        const [analytics, systemStatus, recentActivity] = await Promise.all([
            this.app.apiClient.call('/analytics/summary').catch(() => ({})),
            this.app.apiClient.call('/system/status').catch(() => ({})),
            this.app.apiClient.call('/analytics/recent-activity').catch(() => ({ activity: [] }))
        ]);

        this.data = {
            metrics: analytics,
            systemStatus,
            recentActivity: recentActivity.activity || []
        };
    }

    render() {
        this.renderMetrics();
        this.renderSystemStatus();
        this.renderRecentActivity();
    }

    renderMetrics() {
        const metrics = this.data.metrics;
        
        // Update metric cards
        this.updateMetricCard('total-properties', metrics.total_properties || 0);
        this.updateMetricCard('notifications-sent', metrics.notifications_sent || 0);
        this.updateMetricCard('active-profiles', metrics.active_profiles || 0);
        this.updateMetricCard('system-uptime', `${metrics.uptime_percentage || 98}%`);
    }

    updateMetricCard(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = this.app.utils.formatNumber(value);
        }
    }

    renderSystemStatus() {
        const status = this.data.systemStatus;
        
        // Update scraper status
        this.updateStatusIndicator('yad2-status', status.yad2_status || 'connected');
        this.updateStatusIndicator('facebook-status', status.facebook_status || 'warning');
        
        // Update notification status  
        this.updateStatusIndicator('telegram-status', status.telegram_status || 'connected');
        this.updateStatusIndicator('email-status', status.email_status || 'disconnected');
    }

    updateStatusIndicator(elementId, status) {
        const element = document.getElementById(elementId);
        if (element) {
            const indicator = element.querySelector('.status-indicator');
            const text = element.querySelector('.status-text');
            
            if (indicator) {
                indicator.className = `status-indicator status-${status}`;
            }
            
            if (text) {
                const statusTexts = {
                    connected: 'מחובר',
                    disconnected: 'מנותק',
                    warning: 'דורש תשומת לב',
                    error: 'שגיאה'
                };
                text.textContent = statusTexts[status] || 'לא ידוע';
            }
        }
    }

    renderRecentActivity() {
        const container = document.getElementById('recent-activity');
        if (!container) return;

        if (this.data.recentActivity.length === 0) {
            container.innerHTML = '<div class="text-center text-muted py-3">אין פעילות אחרונה</div>';
            return;
        }

        const activityHTML = this.data.recentActivity.map(activity => `
            <div class="activity-item border-bottom py-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <strong>${activity.title}</strong>
                        <div class="text-muted small">${activity.description}</div>
                    </div>
                    <small class="text-muted">${this.app.utils.formatDate(activity.timestamp)}</small>
                </div>
            </div>
        `).join('');

        container.innerHTML = activityHTML;
    }

    renderError(error) {
        const dashboardContainer = document.getElementById('dashboard');
        if (dashboardContainer) {
            dashboardContainer.innerHTML = `
                <div class="alert alert-danger">
                    <h5><i class="fas fa-exclamation-triangle me-2"></i>שגיאה בטעינת הדשבורד</h5>
                    <p>${error.message || 'שגיאה לא ידועה'}</p>
                    <button class="btn btn-outline-danger" onclick="window.realtyApp.components.dashboard.load()">
                        נסה שוב
                    </button>
                </div>
            `;
        }
    }

    async refresh() {
        const refreshButton = document.querySelector('[data-refresh="dashboard"]');
        if (refreshButton) {
            refreshButton.disabled = true;
            refreshButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>מרענן...';
        }

        try {
            await this.load();
            this.app.utils.showAlert('הדשבורד עודכן', 'success');
        } catch (error) {
            this.app.utils.showAlert('שגיאה בעדכון הדשבורד', 'danger');
        } finally {
            if (refreshButton) {
                refreshButton.disabled = false;
                refreshButton.innerHTML = '<i class="fas fa-sync-alt me-2"></i>רענן';
            }
        }
    }
}

/**
 * Profiles Component
 * Handles profile management functionality
 */
class ProfilesComponent {
    constructor(app) {
        this.app = app;
        this.profiles = [];
        this.editingProfile = null;
    }

    async load() {
        try {
            await this.loadProfiles();
            this.render();
        } catch (error) {
            console.error('Profiles load error:', error);
            this.renderError(error);
        }
    }

    async loadProfiles() {
        const response = await this.app.apiClient.call('/profiles');
        this.profiles = response.profiles || [];
        
        // Update app state
        this.app.updateState({
            data: {
                ...this.app.state.data,
                profiles: this.profiles
            }
        });
    }

    render() {
        const container = document.getElementById('profiles-list');
        if (!container) return;

        if (this.profiles.length === 0) {
            container.innerHTML = this.renderEmptyState();
            return;
        }

        const profilesHTML = this.profiles.map(profile => this.renderProfileCard(profile)).join('');
        container.innerHTML = profilesHTML;
    }

    renderEmptyState() {
        return `
            <div class="col-12">
                <div class="card text-center py-5">
                    <div class="card-body">
                        <i class="fas fa-search fa-3x text-muted mb-3"></i>
                        <h5>אין פרופילי חיפוש</h5>
                        <p class="text-muted">צור פרופיל חיפוש ראשון כדי להתחיל לקבל התראות על דירות</p>
                        <button class="btn btn-primary" onclick="window.realtyApp.components.profiles.showAddModal()">
                            <i class="fas fa-plus me-2"></i>צור פרופיל ראשון
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    renderProfileCard(profile) {
        const statusClass = profile.is_active ? 'success' : 'secondary';
        const statusText = profile.is_active ? 'פעיל' : 'לא פעיל';
        
        return `
            <div class="col-lg-6 col-xl-4 mb-4">
                <div class="card profile-card h-100">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">${profile.name}</h6>
                        <span class="badge bg-${statusClass}">${statusText}</span>
                    </div>
                    <div class="card-body">
                        <div class="profile-details">
                            <div class="detail-row">
                                <i class="fas fa-map-marker-alt text-primary"></i>
                                <span>${profile.location?.city || 'לא צוין'}</span>
                            </div>
                            <div class="detail-row">
                                <i class="fas fa-shekel-sign text-primary"></i>
                                <span>${this.formatPriceRange(profile.price_range)}</span>
                            </div>
                            <div class="detail-row">
                                <i class="fas fa-bed text-primary"></i>
                                <span>${this.formatRoomsRange(profile.rooms_range)}</span>
                            </div>
                            <div class="detail-row">
                                <i class="fas fa-clock text-muted"></i>
                                <span>נוצר: ${this.app.utils.formatDate(profile.created_at)}</span>
                            </div>
                            ${profile.last_match ? `
                            <div class="detail-row">
                                <i class="fas fa-bell text-success"></i>
                                <span>התאמה אחרונה: ${this.app.utils.formatDate(profile.last_match)}</span>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                    <div class="card-footer">
                        <div class="btn-group w-100" role="group">
                            <button class="btn btn-outline-primary btn-sm" 
                                    onclick="window.realtyApp.components.profiles.editProfile('${profile.id}')">
                                <i class="fas fa-edit"></i> ערוך
                            </button>
                            <button class="btn btn-outline-${profile.is_active ? 'warning' : 'success'} btn-sm"
                                    onclick="window.realtyApp.components.profiles.toggleProfile('${profile.id}')">
                                <i class="fas fa-${profile.is_active ? 'pause' : 'play'}"></i> 
                                ${profile.is_active ? 'השבת' : 'הפעל'}
                            </button>
                            <button class="btn btn-outline-danger btn-sm"
                                    onclick="window.realtyApp.components.profiles.deleteProfile('${profile.id}')">
                                <i class="fas fa-trash"></i> מחק
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    formatPriceRange(range) {
        if (!range) return 'לא צוין';
        return `${this.app.utils.formatCurrency(range.min)} - ${this.app.utils.formatCurrency(range.max)}`;
    }

    formatRoomsRange(range) {
        if (!range) return 'לא צוין';
        if (range.min === range.max) return `${range.min} חדרים`;
        return `${range.min}-${range.max} חדרים`;
    }

    showAddModal() {
        this.editingProfile = null;
        this.showProfileModal();
    }

    editProfile(profileId) {
        this.editingProfile = this.profiles.find(p => p.id === profileId);
        this.showProfileModal();
    }

    showProfileModal() {
        // This would open a modal for creating/editing profiles
        // For now, show a simple prompt
        const name = prompt('שם הפרופיל:', this.editingProfile?.name || '');
        if (!name) return;

        if (this.editingProfile) {
            this.updateProfile(this.editingProfile.id, { name });
        } else {
            this.createProfile({ name });
        }
    }

    async createProfile(profileData) {
        try {
            await this.app.apiClient.call('/profiles', 'POST', profileData);
            await this.loadProfiles();
            this.render();
            this.app.utils.showAlert('פרופיל נוצר בהצלחה', 'success');
        } catch (error) {
            console.error('Error creating profile:', error);
            this.app.utils.showAlert('שגיאה ביצירת הפרופיל', 'danger');
        }
    }

    async updateProfile(profileId, profileData) {
        try {
            await this.app.apiClient.call(`/profiles/${profileId}`, 'PUT', profileData);
            await this.loadProfiles();
            this.render();
            this.app.utils.showAlert('פרופיל עודכן בהצלחה', 'success');
        } catch (error) {
            console.error('Error updating profile:', error);
            this.app.utils.showAlert('שגיאה בעדכון הפרופיל', 'danger');
        }
    }

    async toggleProfile(profileId) {
        const profile = this.profiles.find(p => p.id === profileId);
        if (!profile) return;

        try {
            await this.updateProfile(profileId, { is_active: !profile.is_active });
        } catch (error) {
            console.error('Error toggling profile:', error);
        }
    }

    async deleteProfile(profileId) {
        if (!confirm('האם אתה בטוח שברצונך למחוק את הפרופיל?')) return;

        try {
            await this.app.apiClient.call(`/profiles/${profileId}`, 'DELETE');
            await this.loadProfiles();
            this.render();
            this.app.utils.showAlert('פרופיל נמחק בהצלחה', 'success');
        } catch (error) {
            console.error('Error deleting profile:', error);
            this.app.utils.showAlert('שגיאה במחיקת הפרופיל', 'danger');
        }
    }

    renderError(error) {
        const container = document.getElementById('profiles-list');
        if (container) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger">
                        <h5><i class="fas fa-exclamation-triangle me-2"></i>שגיאה בטעינת הפרופילים</h5>
                        <p>${error.message || 'שגיאה לא ידועה'}</p>
                        <button class="btn btn-outline-danger" onclick="window.realtyApp.components.profiles.load()">
                            נסה שוב
                        </button>
                    </div>
                </div>
            `;
        }
    }
}

// Export components
window.DashboardComponent = DashboardComponent;
window.ProfilesComponent = ProfilesComponent;
