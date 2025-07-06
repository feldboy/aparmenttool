/**
 * Main Application Controller
 * Handles initialization, routing, and global state management
 */
class RealtyApp {
    constructor() {
        this.state = {
            currentUser: null,
            currentPage: 'dashboard',
            isLoading: false,
            data: {
                profiles: [],
                notifications: [],
                systemStatus: {},
                analytics: {}
            }
        };
        
        this.components = {};
        this.apiClient = new APIClient();
        this.utils = new UtilityFunctions();
        
        this.init();
    }

    async init() {
        try {
            // Show initial loading
            this.showGlobalLoading('מאתחל את האפליקציה...');
            
            // Initialize components
            await this.initializeComponents();
            
            // Setup routing
            this.setupRouting();
            
            // Setup global event listeners
            this.setupGlobalEvents();
            
            // Load initial data
            await this.loadInitialData();
            
            // Navigate to initial page
            this.navigateToInitialPage();
            
            // Hide loading
            this.hideGlobalLoading();
            
            console.log('RealtyApp initialized successfully');
        } catch (error) {
            console.error('Failed to initialize app:', error);
            this.utils.showAlert('שגיאה באתחול האפליקציה', 'danger');
            this.hideGlobalLoading();
        }
    }

    async initializeComponents() {
        // Initialize all page components
        this.components.dashboard = new DashboardComponent(this);
        this.components.profiles = new ProfilesComponent(this);
        this.components.telegram = new TelegramComponent(this);
        this.components.facebook = new FacebookComponent(this);
        this.components.yad2 = new Yad2Component(this);
        this.components.notifications = new NotificationsComponent(this);
        this.components.settings = new SettingsComponent(this);
    }

    setupRouting() {
        // Handle browser back/forward
        window.addEventListener('popstate', (event) => {
            const page = event.state?.page || this.getPageFromURL();
            this.navigateTo(page, false);
        });

        // Handle navigation clicks
        document.addEventListener('click', (event) => {
            const navLink = event.target.closest('[data-nav]');
            if (navLink) {
                event.preventDefault();
                const page = navLink.getAttribute('data-nav');
                this.navigateTo(page);
            }
        });
    }

    setupGlobalEvents() {
        // Mobile sidebar toggle
        const sidebarToggle = document.querySelector('[data-sidebar-toggle]');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                this.toggleSidebar();
            });
        }

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (event) => {
            const sidebar = document.getElementById('sidebar');
            const sidebarToggle = document.querySelector('[data-sidebar-toggle]');
            
            if (window.innerWidth <= 768 && 
                sidebar && 
                !sidebar.contains(event.target) && 
                !sidebarToggle.contains(event.target)) {
                sidebar.classList.remove('show');
            }
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });

        // Global error handler
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.utils.showAlert('אירעה שגיאה בלתי צפויה', 'danger');
        });

        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.utils.showAlert('שגיאה בטעינת נתונים', 'warning');
        });
    }

    async loadInitialData() {
        try {
            // Load critical data needed for all pages
            const [systemStatus, analytics] = await Promise.all([
                this.apiClient.call('/system/status').catch(() => ({})),
                this.apiClient.call('/analytics/summary').catch(() => ({}))
            ]);

            this.updateState({
                data: {
                    ...this.state.data,
                    systemStatus,
                    analytics
                }
            });
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }

    navigateToInitialPage() {
        const page = this.getPageFromURL();
        this.navigateTo(page, false);
    }

    getPageFromURL() {
        const path = window.location.pathname;
        if (path === '/' || path === '/dashboard') return 'dashboard';
        if (path.startsWith('/profiles')) return 'profiles';
        if (path.startsWith('/telegram')) return 'telegram';
        if (path.startsWith('/facebook')) return 'facebook';
        if (path.startsWith('/yad2')) return 'yad2';
        if (path.startsWith('/notifications')) return 'notifications';
        if (path.startsWith('/settings')) return 'settings';
        return 'dashboard';
    }

    async navigateTo(page, updateHistory = true) {
        if (this.state.isLoading) {
            console.log('Navigation blocked: app is loading');
            return;
        }

        if (page === this.state.currentPage) {
            console.log(`Already on page: ${page}`);
            return;
        }

        try {
            this.updateState({ isLoading: true });

            // Update URL
            if (updateHistory) {
                const url = page === 'dashboard' ? '/' : `/${page}`;
                history.pushState({ page }, '', url);
            }

            // Update navigation UI
            this.updateNavigation(page);

            // Hide current page
            this.hideAllPages();

            // Show loading for the new page
            this.showPageLoading(page);

            // Load page data if component exists
            const component = this.components[page];
            if (component) {
                await component.load();
            } else {
                console.warn(`No component found for page: ${page}`);
            }

            // Update current page
            this.updateState({ 
                currentPage: page,
                isLoading: false 
            });

            // Show the page
            this.showPage(page);

            // Close mobile sidebar
            this.closeSidebar();

            console.log(`Navigated to: ${page}`);
        } catch (error) {
            console.error(`Navigation error for page ${page}:`, error);
            this.utils.showAlert(`שגיאה בטעינת עמוד ${page}`, 'danger');
            this.updateState({ isLoading: false });
        }
    }

    updateNavigation(page) {
        // Update active nav link
        document.querySelectorAll('[data-nav]').forEach(link => {
            const linkPage = link.getAttribute('data-nav');
            link.classList.toggle('active', linkPage === page);
        });
    }

    hideAllPages() {
        document.querySelectorAll('.content-section').forEach(section => {
            section.style.display = 'none';
        });
    }

    showPage(page) {
        const pageElement = document.getElementById(page);
        if (pageElement) {
            pageElement.style.display = 'block';
        }
    }

    showPageLoading(page) {
        const pageElement = document.getElementById(page);
        if (pageElement) {
            const loadingDiv = pageElement.querySelector('.page-loading');
            if (loadingDiv) {
                loadingDiv.style.display = 'block';
            }
        }
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.toggle('show');
        }
    }

    closeSidebar() {
        if (window.innerWidth <= 768) {
            const sidebar = document.getElementById('sidebar');
            if (sidebar) {
                sidebar.classList.remove('show');
            }
        }
    }

    handleResize() {
        // Close sidebar on desktop
        if (window.innerWidth > 768) {
            this.closeSidebar();
        }
    }

    showGlobalLoading(message = 'טוען...') {
        const loadingDiv = document.getElementById('global-loading');
        if (loadingDiv) {
            loadingDiv.querySelector('.loading-message').textContent = message;
            loadingDiv.style.display = 'flex';
        }
    }

    hideGlobalLoading() {
        const loadingDiv = document.getElementById('global-loading');
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }
    }

    updateState(newState) {
        this.state = { ...this.state, ...newState };
        
        // Emit state change event
        document.dispatchEvent(new CustomEvent('stateChange', {
            detail: { state: this.state }
        }));
    }

    getState() {
        return { ...this.state };
    }

    // Data management methods
    async refreshData(dataType) {
        try {
            switch (dataType) {
                case 'profiles':
                    const profilesData = await this.apiClient.call('/profiles');
                    this.updateState({
                        data: {
                            ...this.state.data,
                            profiles: profilesData.profiles || []
                        }
                    });
                    break;
                
                case 'notifications':
                    const notificationsData = await this.apiClient.call('/notifications');
                    this.updateState({
                        data: {
                            ...this.state.data,
                            notifications: notificationsData.notifications || []
                        }
                    });
                    break;
                
                case 'systemStatus':
                    const statusData = await this.apiClient.call('/system/status');
                    this.updateState({
                        data: {
                            ...this.state.data,
                            systemStatus: statusData
                        }
                    });
                    break;
                
                default:
                    console.warn(`Unknown data type: ${dataType}`);
            }
        } catch (error) {
            console.error(`Failed to refresh ${dataType}:`, error);
            throw error;
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.realtyApp = new RealtyApp();
});

// Export for use in other modules
window.RealtyApp = RealtyApp;
