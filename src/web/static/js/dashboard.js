// Dashboard Main JavaScript
class Dashboard {
    constructor() {
        this.currentPage = 'dashboard';
        this.profiles = [];
        this.notifications = [];
        this.isLoading = false;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupRouter();
        this.loadInitialPage();
    }

    setupEventListeners() {
        // Navigation clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-page]')) {
                e.preventDefault();
                const page = e.target.getAttribute('data-page');
                this.navigateToPage(page);
            }
        });

        // Mobile sidebar toggle
        window.toggleSidebar = () => {
            document.getElementById('sidebar').classList.toggle('show');
        };

        // Global navigation function
        window.navigateToPage = (page) => {
            this.navigateToPage(page);
        };
    }

    setupRouter() {
        // Simple client-side routing
        window.addEventListener('popstate', (e) => {
            const page = e.state?.page || 'dashboard';
            this.loadPage(page, false);
        });
    }

    loadInitialPage() {
        const path = window.location.pathname;
        let page = 'dashboard';
        
        if (path.includes('/profiles')) page = 'profiles';
        else if (path.includes('/telegram')) page = 'telegram';
        else if (path.includes('/facebook')) page = 'facebook';
        else if (path.includes('/yad2')) page = 'yad2';
        else if (path.includes('/notifications')) page = 'notifications';
        else if (path.includes('/settings')) page = 'settings';

        this.loadPage(page, false);
    }

    navigateToPage(page) {
        // Update URL without reload
        const url = page === 'dashboard' ? '/' : `/${page}`;
        history.pushState({ page }, '', url);
        
        this.loadPage(page, true);
    }

    async loadPage(page, updateNav = true) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.currentPage = page;

        try {
            // Show loading
            this.showPageLoading();

            // Load page content
            const content = await this.fetchPageContent(page);
            document.getElementById('page-content').innerHTML = content;

            // Load modals if needed
            await this.loadModals();

            // Update navigation
            if (updateNav) {
                this.updateNavigation(page);
            }

            // Load page-specific data
            await this.loadPageData(page);

        } catch (error) {
            console.error('Error loading page:', error);
            this.showError('שגיאה בטעינת העמוד');
        } finally {
            this.isLoading = false;
        }
    }

    async fetchPageContent(page) {
        const response = await fetch(`/templates/dashboard/${page}.html`);
        if (!response.ok) {
            throw new Error(`Failed to load page: ${page}`);
        }
        return await response.text();
    }

    async loadModals() {
        const modalsContainer = document.getElementById('modals-container');
        if (modalsContainer && !modalsContainer.innerHTML.trim()) {
            try {
                const response = await fetch('/templates/components/modals.html');
                if (response.ok) {
                    modalsContainer.innerHTML = await response.text();
                }
            } catch (error) {
                console.warn('Could not load modals:', error);
            }
        }
    }

    updateNavigation(page) {
        // Remove active class from all nav links
        document.querySelectorAll('.sidebar .nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Add active class to current page
        const activeLink = document.querySelector(`[data-page="${page}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }

        // Hide sidebar on mobile
        if (window.innerWidth < 768) {
            document.getElementById('sidebar').classList.remove('show');
        }
    }

    async loadPageData(page) {
        switch (page) {
            case 'dashboard':
                await this.loadDashboardData();
                break;
            case 'profiles':
                await this.loadProfilesData();
                break;
            case 'facebook':
                await this.loadFacebookData();
                break;
            case 'yad2':
                await this.loadYad2Data();
                break;
            case 'telegram':
                await this.loadTelegramData();
                break;
            case 'notifications':
                await this.loadNotificationsData();
                break;
            case 'settings':
                await this.loadSettingsData();
                break;
            default:
                console.warn(`Unknown page: ${page}`);
                break;
        }
    }

    async loadDashboardData() {
        try {
            const [systemStatus, analytics] = await Promise.all([
                API.call('/system/status'),
                API.call('/analytics/summary?days=7')
            ]);

            // Update dashboard stats
            this.updateElement('total-properties', analytics.analytics?.total_properties_found || 0);
            this.updateElement('notifications-sent', analytics.analytics?.notifications_sent || 0);
            this.updateElement('active-profiles', analytics.analytics?.profiles_active || 0);
            this.updateElement('system-uptime', '98%');

            // Load recent activity
            await this.loadRecentActivity();

        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadRecentActivity() {
        try {
            const notifications = await API.call('/notifications?limit=5');
            const activityContainer = document.getElementById('recent-activity');
            
            if (activityContainer && notifications.notifications) {
                activityContainer.innerHTML = notifications.notifications.map(notification => `
                    <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                        <div>
                            <small class="fw-bold">${notification.title}</small><br>
                            <small class="text-muted">${notification.source} • ${Utils.formatDate(notification.timestamp)}</small>
                        </div>
                        <span class="badge bg-${notification.sent ? 'success' : 'warning'}">
                            ${notification.sent ? 'נשלח' : 'ממתין'}
                        </span>
                    </div>
                `).join('') || '<p class="text-muted">אין פעילות אחרונה</p>';
            }
        } catch (error) {
            console.error('Error loading recent activity:', error);
        }
    }

    async loadProfilesData() {
        try {
            const response = await API.call('/profiles');
            this.profiles = response.profiles || [];
            
            if (window.ProfilesManager) {
                window.ProfilesManager.render(this.profiles);
            }
        } catch (error) {
            console.error('Error loading profiles:', error);
        }
    }

    async loadFacebookData() {
        // Facebook data loading is handled by facebook.js
        console.log('Loading Facebook data...');
    }

    async loadYad2Data() {
        // Yad2 data loading is handled by yad2.js
        console.log('Loading Yad2 data...');
    }

    async loadTelegramData() {
        // Telegram data loading is handled by telegram.js
        console.log('Loading Telegram data...');
    }

    async loadNotificationsData() {
        // Notifications data loading is handled by notifications.js
        console.log('Loading Notifications data...');
    }

    async loadSettingsData() {
        // Settings data loading is handled by settings.js
        console.log('Loading Settings data...');
    }

    showPageLoading() {
        document.getElementById('page-content').innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">טוען...</span>
                </div>
                <p class="mt-3">טוען נתונים...</p>
            </div>
        `;
    }

    showError(message) {
        document.getElementById('page-content').innerHTML = `
            <div class="alert alert-danger text-center">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
                <br>
                <button class="btn btn-outline-danger mt-2" onclick="location.reload()">
                    <i class="fas fa-sync-alt me-2"></i>
                    נסה שוב
                </button>
            </div>
        `;
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
}

// Global functions for backward compatibility
window.refreshDashboard = () => {
    if (window.dashboardApp) {
        window.dashboardApp.loadDashboardData();
    }
};

window.showSystemStatus = () => {
    // Show system status modal
    const modal = new bootstrap.Modal(document.getElementById('systemStatusModal'));
    modal.show();
};

window.testAllConnections = async () => {
    Utils.showAlert('בודק את כל החיבורים...', 'info');
    
    try {
        // Test various connections
        const tests = [
            API.call('/telegram/test'),
            API.call('/facebook/status'),
            API.call('/yad2/config')
        ];
        
        await Promise.all(tests);
        Utils.showAlert('כל החיבורים תקינים!', 'success');
    } catch (error) {
        Utils.showAlert('נמצאו בעיות בחלק מהחיבורים', 'warning');
    }
};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardApp = new Dashboard();
});
