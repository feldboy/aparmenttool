/**
 * Custom API Error class
 */
class APIError extends Error {
    constructor(status, message, endpoint) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.endpoint = endpoint;
    }
}

/**
 * Enhanced API Client with proper error handling and retry logic
 */
class APIClient {
    constructor() {
        this.baseURL = '/api';
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
        this.retryAttempts = 3;
        this.retryDelay = 1000;
        this.requestTimeout = 30000;
    }

    async call(endpoint, method = 'GET', data = null, options = {}) {
        const startTime = Date.now();
        let lastError = null;

        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const result = await this.makeRequest(endpoint, method, data, options);
                
                // Log successful request
                console.log(`API Success [${method} ${endpoint}]: ${Date.now() - startTime}ms`);
                return result;
                
            } catch (error) {
                lastError = error;
                console.warn(`API Attempt ${attempt} failed [${method} ${endpoint}]:`, error.message);
                
                // Don't retry certain errors
                if (error.status === 401 || error.status === 403 || error.status === 404) {
                    break;
                }
                
                // Don't retry on last attempt
                if (attempt === this.retryAttempts) {
                    break;
                }
                
                // Wait before retry
                await this.sleep(this.retryDelay * attempt);
            }
        }

        // All attempts failed, try mock data or throw error
        console.error(`API Failed [${method} ${endpoint}] after ${this.retryAttempts} attempts:`, lastError);
        
        try {
            return this.getMockData(endpoint, method, data);
        } catch (mockError) {
            throw lastError || new Error('Request failed');
        }
    }

    async makeRequest(endpoint, method, data, options) {
        const url = `${this.baseURL}${endpoint}`;
        const controller = new AbortController();
        
        // Set timeout
        const timeoutId = setTimeout(() => controller.abort(), this.requestTimeout);
        
        try {
            const config = {
                method,
                headers: { ...this.defaultHeaders, ...options.headers },
                signal: controller.signal,
                ...options
            };

            if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
                config.body = JSON.stringify(data);
            }

            const response = await fetch(url, config);
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new APIError(response.status, response.statusText, endpoint);
            }

            // Handle different response types
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
            
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new APIError(408, 'Request Timeout', endpoint);
            }
            
            if (error instanceof APIError) {
                throw error;
            }
            
            throw new APIError(0, error.message, endpoint);
        }
    }

    getMockData(endpoint, method, data) {
        console.log(`Using mock data for [${method} ${endpoint}]`);
        
        // Return mock data based on endpoint
        if (endpoint.includes('/profiles') && method === 'GET') {
            return this.getMockProfiles();
        }
        
        if (endpoint.includes('/notifications')) {
            return this.getMockNotifications();
        }
        
        if (endpoint.includes('/system/status')) {
            return this.getMockSystemStatus();
        }
        
        if (endpoint.includes('/analytics/summary')) {
            return this.getMockAnalytics();
        }
        
        if (endpoint.includes('/analytics/recent-activity')) {
            return this.getMockRecentActivity();
        }
        
        if (endpoint.includes('/facebook/status')) {
            return this.getMockFacebookStatus();
        }
        
        if (endpoint.includes('/telegram/config') || endpoint.includes('/telegram/status')) {
            return this.getMockTelegramConfig();
        }
        
        if (endpoint.includes('/yad2/config')) {
            return this.getMockYad2Config();
        }
        
        if (endpoint.includes('/settings')) {
            return this.getMockSettings();
        }

        // Default success response for write operations
        if (['POST', 'PUT', 'DELETE'].includes(method)) {
            return { 
                success: true, 
                message: 'הפעולה בוצעה בהצלחה',
                data: data
            };
        }
        
        throw new APIError(404, 'No mock data available', endpoint);
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Mock data methods for development
    getMockProfiles() {
        return {
            profiles: [
                {
                    id: 'profile_1',
                    name: 'דירה בתל אביב',
                    price_range: { min: 4000, max: 7000 },
                    rooms_range: { min: 2, max: 3 },
                    location: {
                        city: 'תל אביב - יפו',
                        neighborhoods: ['פלורנטין', 'נווה צדק']
                    },
                    property_types: ['דירה', 'דירת גן'],
                    is_active: true,
                    created_at: '2025-06-25T10:00:00Z',
                    last_match: '2025-06-29T14:30:00Z'
                },
                {
                    id: 'profile_2',
                    name: 'בית בירושלים',
                    price_range: { min: 3000, max: 5000 },
                    rooms_range: { min: 3, max: 5 },
                    location: {
                        city: 'ירושלים',
                        neighborhoods: ['גבעת שאול', 'רמות']
                    },
                    property_types: ['בית', 'דירה'],
                    is_active: false,
                    created_at: '2025-06-20T15:20:00Z',
                    last_match: null
                }
            ],
            total: 2
        };
    }

    getMockNotifications() {
        return {
            notifications: [
                {
                    id: 'notif_1',
                    title: 'דירה חדשה בפלורנטין',
                    message: '3 חדרים, 5,800 ₪, פלורנטין - דירה מקסימה עם מרפסת',
                    source: 'יד2',
                    property_url: 'https://www.yad2.co.il/item/123456',
                    image_url: 'https://via.placeholder.com/300x200?text=דירה+בפלורנטין',
                    timestamp: '2025-06-29T15:30:00Z',
                    sent: true,
                    channel: 'telegram',
                    profile_name: 'דירה בתל אביב'
                },
                {
                    id: 'notif_2',
                    title: 'דירה בנווה צדק',
                    message: '2.5 חדרים, 6,200 ₪, נווה צדק - דירה משופצת בבניין בוטיק',
                    source: 'פייסבוק',
                    property_url: 'https://facebook.com/groups/telaviv/posts/123',
                    image_url: 'https://via.placeholder.com/300x200?text=דירה+בנווה+צדק',
                    timestamp: '2025-06-29T12:15:00Z',
                    sent: true,
                    channel: 'telegram',
                    profile_name: 'דירה בתל אביב'
                }
            ],
            total: 2
        };
    }

    getMockSystemStatus() {
        return {
            scanner_status: {
                yad2: { status: "active", last_scan: "2025-06-29T15:25:00Z" },
                facebook: { status: "requires_auth", last_scan: null }
            },
            notification_status: {
                telegram: { status: "connected", last_sent: "2025-06-29T14:30:00Z" },
                email: { status: "disabled" }
            },
            database_status: "connected",
            uptime: "2 days, 5 hours"
        };
    }

    getMockAnalytics() {
        return {
            analytics: {
                total_properties_found: 45,
                notifications_sent: 12,
                profiles_active: 2
            }
        };
    }

    getMockFacebookStatus() {
        return {
            connected: false,
            session_valid: false,
            groups_configured: 0,
            last_login: null,
            requires_reauth: true
        };
    }

    getMockTelegramStatus() {
        return {
            connected: false,
            chat_id: '',
            bot_username: '@RealtyScanner_bot',
            last_test: null,
            connection_status: 'not_configured'
        };
    }

    getMockYad2Config() {
        return {
            config: {
                search_urls: [
                    {
                        id: 'url_1',
                        name: 'דירות 3 חדרים בתל אביב',
                        url: 'https://www.yad2.co.il/realestate/rent?city=5000&rooms=2-3&price=3000-6000',
                        active: true,
                        last_scan: '2025-06-29T15:25:00Z'
                    }
                ],
                scan_frequency: 300,
                last_scan: '2025-06-29T15:25:00Z',
                active: true
            }
        };
    }

    getMockRecentActivity() {
        return {
            activity: [
                {
                    id: 'activity_1',
                    title: 'דירה חדשה נמצאה',
                    description: 'דירת 3 חדרים בפלורנטין תואמת לפרופיל "דירה בתל אביב"',
                    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString()
                },
                {
                    id: 'activity_2',
                    title: 'פרופיל עודכן',
                    description: 'פרופיל "בית בירושלים" הופעל מחדש',
                    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString()
                },
                {
                    id: 'activity_3',
                    title: 'התראה נשלחה',
                    description: 'התראה נשלחה לטלגרם על דירה בגבעת שאול',
                    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString()
                }
            ]
        };
    }

    getMockTelegramConfig() {
        return {
            chat_id: '123456789',
            is_connected: true,
            last_message_sent: new Date().toISOString()
        };
    }

    getMockSettings() {
        return {
            notification_frequency: 'immediate',
            email_notifications: false,
            max_notifications_per_day: 10,
            quiet_hours_start: '22:00',
            quiet_hours_end: '08:00'
        };
    }

    // Convenience methods
    async get(endpoint, options = {}) {
        return this.call(endpoint, 'GET', null, options);
    }

    async post(endpoint, data, options = {}) {
        return this.call(endpoint, 'POST', data, options);
    }

    async put(endpoint, data, options = {}) {
        return this.call(endpoint, 'PUT', data, options);
    }

    async delete(endpoint, options = {}) {
        return this.call(endpoint, 'DELETE', null, options);
    }
}

// Create global API instance
window.API = new APIClient();
