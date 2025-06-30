"""
API routes for the web dashboard
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Create a mock router for when FastAPI is not available
api_router = None

def create_api_router():
    """Create API router"""
    global api_router
    
    if api_router is not None:
        return api_router
    
    try:
        from fastapi import APIRouter, Depends, HTTPException, Query
        from fastapi.responses import JSONResponse
        from .auth import require_auth
        
        api_router = APIRouter()
        
        # Profile Management Routes
        
        @api_router.get("/profiles")
        async def get_profiles(user: Dict[str, Any] = Depends(require_auth)):
            """Get all user profiles"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')  # Default for demo
            profiles = data_store.get_profiles(user_id)
            
            return {"profiles": profiles, "total": len(profiles)}
        
        @api_router.post("/profiles")
        async def create_profile(profile_data: Dict[str, Any], user: Dict[str, Any] = Depends(require_auth)):
            """Create new profile"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')  # Default for demo
            
            # Validate required fields
            if not profile_data.get('name'):
                raise HTTPException(status_code=400, detail="Profile name is required")
            
            new_profile = data_store.create_profile(user_id, profile_data)
            return {"profile": new_profile, "message": "Profile created successfully"}
        
        @api_router.put("/profiles/{profile_id}")
        async def update_profile(profile_id: str, profile_data: Dict[str, Any], user: Dict[str, Any] = Depends(require_auth)):
            """Update existing profile"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            updated_profile = data_store.update_profile(profile_id, profile_data)
            
            if not updated_profile:
                raise HTTPException(status_code=404, detail="Profile not found")
            
            return {"profile": updated_profile, "message": "Profile updated successfully"}
        
        @api_router.delete("/profiles/{profile_id}")
        async def delete_profile(profile_id: str, user: Dict[str, Any] = Depends(require_auth)):
            """Delete profile"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            success = data_store.delete_profile(profile_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Profile not found")
            
            return {"message": f"Profile {profile_id} deleted successfully"}
        
        # Notification Management Routes
        
        @api_router.get("/notifications")
        async def get_notifications(
            limit: int = Query(50, le=100),
            offset: int = Query(0, ge=0),
            profile_id: Optional[str] = Query(None),
            user: Dict[str, Any] = Depends(require_auth)
        ):
            """Get notifications with pagination"""
            # TODO: Integrate with database
            mock_notifications = [
                {
                    'id': 'notif_1',
                    'profile_id': 'profile_1',
                    'property': {
                        'listing_id': 'yad2_12345',
                        'title': 'Beautiful 2-room in Florentin',
                        'price': 4800,
                        'rooms': 2,
                        'location': 'Florentin, Tel Aviv',
                        'url': 'https://yad2.co.il/item/12345'
                    },
                    'channels': ['telegram', 'email'],
                    'status': 'sent',
                    'match_score': 89.5,
                    'sent_at': '2025-06-28T14:30:00Z'
                },
                {
                    'id': 'notif_2',
                    'profile_id': 'profile_1',
                    'property': {
                        'listing_id': 'yad2_12346',
                        'title': 'Modern studio near Rothschild',
                        'price': 5200,
                        'rooms': 1,
                        'location': 'City Center, Tel Aviv',
                        'url': 'https://yad2.co.il/item/12346'
                    },
                    'channels': ['telegram'],
                    'status': 'sent',
                    'match_score': 76.2,
                    'sent_at': '2025-06-28T12:15:00Z'
                }
            ]
            
            # Filter by profile_id if provided
            if profile_id:
                mock_notifications = [n for n in mock_notifications if n['profile_id'] == profile_id]
            
            # Apply pagination
            total = len(mock_notifications)
            notifications = mock_notifications[offset:offset + limit]
            
            return {
                "notifications": notifications,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        
        @api_router.get("/notifications/stats")
        async def get_notification_stats(user: Dict[str, Any] = Depends(require_auth)):
            """Get notification statistics"""
            # TODO: Calculate from database
            stats = {
                'total_notifications': 156,
                'last_24h': 12,
                'last_7d': 89,
                'success_rate': 98.7,
                'channels': {
                    'telegram': {'sent': 134, 'failed': 2},
                    'email': {'sent': 89, 'failed': 1},
                    'whatsapp': {'sent': 45, 'failed': 0}
                },
                'top_sources': [
                    {'source': 'Yad2', 'count': 112},
                    {'source': 'Facebook', 'count': 44}
                ]
            }
            
            return stats
        
        # Property Management Routes
        
        @api_router.get("/properties/recent")
        async def get_recent_properties(
            limit: int = Query(20, le=50),
            user: Dict[str, Any] = Depends(require_auth)
        ):
            """Get recently found properties"""
            # TODO: Integrate with database
            mock_properties = [
                {
                    'listing_id': 'yad2_12345',
                    'title': 'Beautiful 2-room in Florentin',
                    'price': 4800,
                    'rooms': 2,
                    'location': 'Florentin, Tel Aviv',
                    'description': 'Modern apartment with balcony...',
                    'url': 'https://yad2.co.il/item/12345',
                    'image_url': 'https://example.com/img1.jpg',
                    'source': 'Yad2',
                    'found_at': '2025-06-28T14:30:00Z',
                    'match_score': 89.5
                }
            ]
            
            return {"properties": mock_properties[:limit]}
        
        # Settings Routes
        
        @api_router.get("/settings")
        async def get_settings(user: Dict[str, Any] = Depends(require_auth)):
            """Get user settings"""
            # TODO: Get from database
            settings = {
                'notification_channels': {
                    'telegram': {'enabled': True, 'chat_id': '123456789'},
                    'email': {'enabled': True, 'address': 'user@example.com'},
                    'whatsapp': {'enabled': False, 'phone': '+972501234567'}
                },
                'preferences': {
                    'scan_frequency': 5,  # minutes
                    'notification_quiet_hours': {'start': '23:00', 'end': '07:00'},
                    'max_daily_notifications': 10
                }
            }
            
            return settings
        
        @api_router.put("/settings")
        async def update_settings(settings_data: Dict[str, Any], user: Dict[str, Any] = Depends(require_auth)):
            """Update user settings"""
            # TODO: Validate and save to database
            return {"message": "Settings updated successfully", "settings": settings_data}
        
        # System Status Routes
        
        @api_router.get("/system/status")
        async def get_system_status():
            """Get system status"""
            status = {
                'status': 'healthy',
                'services': {
                    'database': 'connected',
                    'telegram_bot': 'running',
                    'scrapers': 'active',
                    'notifications': 'operational'
                },
                'last_scan': '2025-06-28T14:35:00Z',
                'active_profiles': 42,
                'pending_notifications': 3
            }
            
            return status
        
        # Telegram Bot Management Routes
        
        @api_router.get("/telegram/status")
        async def get_telegram_status(user: Dict[str, Any] = Depends(require_auth)):
            """Get Telegram bot connection status"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            settings = data_store.get_telegram_settings(user_id)
            
            return {
                "connected": settings.get('enabled', False),
                "chat_id": settings.get('chat_id', ''),
                "bot_username": "@RealtyScanner_bot",
                "last_test": settings.get('last_test'),
                "connection_status": settings.get('connection_status', 'not_configured')
            }
        
        @api_router.post("/telegram/setup")
        async def setup_telegram(setup_data: Dict[str, Any], user: Dict[str, Any] = Depends(require_auth)):
            """Setup Telegram chat ID for user"""
            from .data_store import get_data_store
            
            chat_id = setup_data.get('chat_id')
            if not chat_id:
                raise HTTPException(status_code=400, detail="Chat ID is required")
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            
            # Update telegram settings
            updated_settings = data_store.update_telegram_settings(user_id, {
                'chat_id': chat_id,
                'enabled': True,
                'connection_status': 'configured'
            })
            
            return {
                "message": "Telegram setup completed successfully",
                "chat_id": chat_id,
                "setup_completed": True,
                "settings": updated_settings
            }
        
        @api_router.post("/telegram/test")
        async def test_telegram_connection(user: Dict[str, Any] = Depends(require_auth)):
            """Send test message to user's Telegram"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            settings = data_store.get_telegram_settings(user_id)
            
            chat_id = settings.get('chat_id')
            if not chat_id:
                raise HTTPException(status_code=400, detail="Telegram not configured")
            
            try:
                # Try to send actual test message
                from ..telegram_bot.notification_bot import test_telegram_connection
                import asyncio
                
                success = await test_telegram_connection(chat_id)
                
                # Update last test time
                data_store.update_telegram_settings(user_id, {
                    'last_test': datetime.now().isoformat(),
                    'connection_status': 'connected' if success else 'error'
                })
                
                return {
                    "success": success,
                    "message": "Test message sent successfully!" if success else "Failed to send test message",
                    "chat_id": chat_id
                }
            except Exception as e:
                logger.error(f"Error testing Telegram connection: {e}")
                data_store.update_telegram_settings(user_id, {
                    'connection_status': 'error'
                })
                return {
                    "success": False,
                    "message": f"Error testing connection: {str(e)}"
                }
        
        # Facebook Integration Routes
        
        @api_router.get("/facebook/status")
        async def get_facebook_status(user: Dict[str, Any] = Depends(require_auth)):
            """Get Facebook integration status"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            settings = data_store.get_facebook_settings(user_id)
            
            return {
                "connected": settings.get('enabled', False),
                "session_valid": settings.get('session_valid', False),
                "groups_configured": len(settings.get('groups', [])),
                "last_login": settings.get('last_login'),
                "requires_reauth": settings.get('requires_reauth', True)
            }
        
        @api_router.post("/facebook/login")
        async def facebook_login(login_data: Dict[str, Any], user: Dict[str, Any] = Depends(require_auth)):
            """Handle Facebook login/authentication"""
            from .data_store import get_data_store
            
            # This is a simplified mock implementation
            # In reality, this would handle OAuth flow
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            
            # Simulate successful login
            updated_settings = data_store.update_facebook_settings(user_id, {
                'enabled': True,
                'session_valid': True,
                'last_login': datetime.now().isoformat(),
                'requires_reauth': False
            })
            
            return {
                "message": "Facebook login successful",
                "session_valid": True,
                "auth_url": None,  # No need for auth URL after successful login
                "settings": updated_settings
            }
        
        @api_router.post("/facebook/groups")
        async def configure_facebook_groups(groups_data: Dict[str, Any], user: Dict[str, Any] = Depends(require_auth)):
            """Configure Facebook groups to monitor"""
            from .data_store import get_data_store
            
            groups = groups_data.get('groups', [])
            
            # Validate groups data
            for group in groups:
                if not group.get('id') or not group.get('name'):
                    raise HTTPException(status_code=400, detail="Invalid group data")
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            
            updated_settings = data_store.update_facebook_settings(user_id, {
                'groups': groups
            })
            
            return {
                "message": f"Configured {len(groups)} Facebook groups successfully",
                "groups": groups,
                "total_groups": len(groups),
                "settings": updated_settings
            }
        
        @api_router.get("/facebook/groups")
        async def get_facebook_groups(user: Dict[str, Any] = Depends(require_auth)):
            """Get configured Facebook groups"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            settings = data_store.get_facebook_settings(user_id)
            
            groups = settings.get('groups', [])
            
            # Add some mock groups if none configured
            if not groups:
                groups = [
                    {
                        "id": "123456789",
                        "name": "דירות להשכרה תל אביב",
                        "url": "https://facebook.com/groups/123456789",
                        "members": 15420,
                        "last_scan": "2025-06-28T15:00:00Z",
                        "active": True
                    },
                    {
                        "id": "987654321",
                        "name": "השכרת דירות ירושלים",
                        "url": "https://facebook.com/groups/987654321",
                        "members": 8900,
                        "last_scan": "2025-06-28T14:30:00Z",
                        "active": True
                    }
                ]
            
            return {"groups": groups, "total": len(groups)}
        
        # Yad2 Configuration Routes
        
        @api_router.get("/yad2/config")
        async def get_yad2_config(user: Dict[str, Any] = Depends(require_auth)):
            """Get Yad2 search configuration"""
            # TODO: Load from user profile
            mock_config = {
                "search_urls": [
                    "https://www.yad2.co.il/realestate/rent?city=5000&rooms=2-3&price=3000-6000"
                ],
                "scan_frequency": 300,  # 5 minutes
                "last_scan": "2025-06-28T15:25:00Z",
                "active": True
            }
            
            return {"config": mock_config}
        
        @api_router.post("/yad2/config")
        async def update_yad2_config(config_data: Dict[str, Any], user: Dict[str, Any] = Depends(require_auth)):
            """Update Yad2 search configuration"""
            # TODO: Validate and save configuration
            return {
                "message": "Yad2 configuration updated",
                "config": config_data
            }
        
        # Notification Preferences Routes
        
        @api_router.get("/preferences/notifications")
        async def get_notification_preferences(user: Dict[str, Any] = Depends(require_auth)):
            """Get user notification preferences"""
            # TODO: Load from user profile
            mock_prefs = {
                "channels": {
                    "telegram": {
                        "enabled": True,
                        "chat_id": user.get('telegram_chat_id'),
                        "quiet_hours": {"start": "23:00", "end": "07:00"}
                    },
                    "email": {
                        "enabled": False,
                        "address": user.get('email')
                    }
                },
                "formatting": {
                    "include_images": True,
                    "include_description": True,
                    "max_description_length": 100
                },
                "delivery": {
                    "immediate": True,
                    "batch_notifications": False,
                    "max_per_hour": 10
                }
            }
            
            return {"preferences": mock_prefs}
        
        @api_router.post("/preferences/notifications")
        async def update_notification_preferences(prefs_data: Dict[str, Any], user: Dict[str, Any] = Depends(require_auth)):
            """Update notification preferences"""
            # TODO: Validate and save preferences
            return {
                "message": "Notification preferences updated",
                "preferences": prefs_data
            }
        
        # System Status and Analytics Routes
        
        @api_router.get("/system/status")
        async def get_system_status(user: Dict[str, Any] = Depends(require_auth)):
            """Get overall system status"""
            return {
                "scanner_status": {
                    "yad2": {"status": "active", "last_scan": "2025-06-28T15:25:00Z"},
                    "facebook": {"status": "requires_auth", "last_scan": None}
                },
                "notification_status": {
                    "telegram": {"status": "connected", "last_sent": "2025-06-28T14:30:00Z"},
                    "email": {"status": "disabled"}
                },
                "database_status": "connected",
                "uptime": "2 days, 5 hours"
            }
        
        @api_router.get("/analytics/summary")
        async def get_analytics_summary(
            days: int = Query(7, le=30),
            user: Dict[str, Any] = Depends(require_auth)
        ):
            """Get analytics summary for the specified period"""
            # TODO: Load real analytics data
            mock_analytics = {
                "period_days": days,
                "total_properties_found": 45,
                "notifications_sent": 12,
                "profiles_active": 2,
                "sources_breakdown": {
                    "yad2": {"properties": 32, "notifications": 8},
                    "facebook": {"properties": 13, "notifications": 4}
                },
                "daily_breakdown": [
                    {"date": "2025-06-28", "properties": 8, "notifications": 3},
                    {"date": "2025-06-27", "properties": 12, "notifications": 4},
                    {"date": "2025-06-26", "properties": 6, "notifications": 2}
                ]
            }
            
            return {"analytics": mock_analytics}
        
        # Import/Export Routes
        
        @api_router.post("/profiles/import")
        async def import_profiles(import_data: Dict[str, Any], user: Dict[str, Any] = Depends(require_auth)):
            """Import profiles from JSON/CSV"""
            # TODO: Implement profile import logic
            profiles = import_data.get('profiles', [])
            return {
                "message": f"Imported {len(profiles)} profiles",
                "imported_count": len(profiles),
                "skipped_count": 0
            }
        
        @api_router.get("/profiles/export")
        async def export_profiles(user: Dict[str, Any] = Depends(require_auth)):
            """Export user profiles"""
            # TODO: Get actual user profiles
            mock_export = {
                "export_timestamp": datetime.now().isoformat(),
                "profiles": [
                    {
                        "name": "Tel Aviv Search",
                        "price_range": {"min": 3000, "max": 6000},
                        "rooms_range": {"min": 2, "max": 3},
                        "location": {"city": "Tel Aviv", "neighborhoods": ["Florentin"]},
                        "created_at": "2025-06-25T10:00:00Z"
                    }
                ]
            }
            
            return mock_export
        
        # Yad2 URL Management Routes
        
        @api_router.get("/yad2/urls")
        async def get_yad2_urls(user: Dict[str, Any] = Depends(require_auth)):
            """Get Yad2 search URLs"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            settings = data_store.get_yad2_settings(user_id)
            
            return {"urls": settings.get('search_urls', []), "total": len(settings.get('search_urls', []))}
        
        @api_router.post("/yad2/urls")
        async def add_yad2_url(url_data: Dict[str, Any], user: Dict[str, Any] = Depends(require_auth)):
            """Add new Yad2 search URL"""
            from .data_store import get_data_store
            
            url = url_data.get('url')
            if not url:
                raise HTTPException(status_code=400, detail="URL is required")
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            
            # Create new URL entry
            new_url = {
                'id': f'url_{int(datetime.now().timestamp())}',
                'name': url_data.get('name', 'חיפוש ללא שם'),
                'url': url,
                'active': url_data.get('active', True),
                'created_at': datetime.now().isoformat(),
                'last_scan': None
            }
            
            # Update settings
            settings = data_store.get_yad2_settings(user_id)
            search_urls = settings.get('search_urls', [])
            search_urls.append(new_url)
            
            data_store.update_yad2_settings(user_id, {'search_urls': search_urls})
            
            return {"message": "URL added successfully", "url": new_url}
        
        @api_router.post("/yad2/urls/{url_id}/toggle")
        async def toggle_yad2_url(url_id: str, user: Dict[str, Any] = Depends(require_auth)):
            """Toggle Yad2 URL active status"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            settings = data_store.get_yad2_settings(user_id)
            
            search_urls = settings.get('search_urls', [])
            for url_config in search_urls:
                if url_config['id'] == url_id:
                    url_config['active'] = not url_config['active']
                    break
            else:
                raise HTTPException(status_code=404, detail="URL not found")
            
            data_store.update_yad2_settings(user_id, {'search_urls': search_urls})
            
            return {"message": "URL status updated successfully"}
        
        @api_router.delete("/yad2/urls/{url_id}")
        async def delete_yad2_url(url_id: str, user: Dict[str, Any] = Depends(require_auth)):
            """Delete Yad2 search URL"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            settings = data_store.get_yad2_settings(user_id)
            
            search_urls = settings.get('search_urls', [])
            original_length = len(search_urls)
            search_urls = [url for url in search_urls if url['id'] != url_id]
            
            if len(search_urls) == original_length:
                raise HTTPException(status_code=404, detail="URL not found")
            
            data_store.update_yad2_settings(user_id, {'search_urls': search_urls})
            
            return {"message": "URL deleted successfully"}

        return api_router
        
    except ImportError as e:
        logger.error(f"Failed to import FastAPI dependencies: {e}")
        # Return a mock router that won't break the application
        return None
