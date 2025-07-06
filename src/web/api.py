"""
API routes for the web dashboard
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

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
        from .auth import require_auth, SKIP_AUTH
        
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
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            
            # Get settings from data store or return defaults
            settings = data_store.get_user_settings(user_id) if hasattr(data_store, 'get_user_settings') else {}
            
            default_settings = {
                'scan_frequency': 5,  # minutes
                'max_notifications_per_day': 50,
                'notification_quiet_hours': {
                    'enabled': True,
                    'start': '22:00',
                    'end': '08:00'
                },
                'email_notifications': False,
                'telegram_notifications': True,
                'whatsapp_notifications': False,
                'notification_format': 'detailed',
                'language': 'he',
                'timezone': 'Asia/Jerusalem',
                'data_retention_days': 90,
                'auto_archive_old_listings': True
            }
            
            # Merge with defaults
            final_settings = {**default_settings, **settings}
            
            return final_settings
        
        @api_router.put("/settings")
        async def update_settings(settings_data: Dict[str, Any], user: Dict[str, Any] = Depends(require_auth)):
            """Update user settings"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            
            # Validate settings data
            valid_keys = {
                'scan_frequency', 'max_notifications_per_day', 'notification_quiet_hours',
                'email_notifications', 'telegram_notifications', 'whatsapp_notifications',
                'notification_format', 'language', 'timezone', 'data_retention_days',
                'auto_archive_old_listings'
            }
            
            # Filter to only valid keys
            filtered_settings = {k: v for k, v in settings_data.items() if k in valid_keys}
            
            # Update settings (mock implementation)
            if hasattr(data_store, 'update_user_settings'):
                data_store.update_user_settings(user_id, filtered_settings)
            
            return {"message": "Settings updated successfully", "settings": filtered_settings}
        
        # System Status Routes
        
        @api_router.get("/system/status")
        async def get_system_status(user: Dict[str, Any] = Depends(require_auth)):
            """Get system status information"""
            # TODO: Get real status from system monitors
            status = {
                'yad2_status': 'connected',
                'facebook_status': 'warning',
                'telegram_status': 'connected',
                'email_status': 'disconnected',
                'database_status': 'connected',
                'worker_status': 'running',
                'last_scan': datetime.now().isoformat(),
                'uptime': '2d 14h 32m',
                'scan_frequency': '5 minutes',
                'errors_last_24h': 2
            }
            
            return status
        
        # Analytics Routes
        
        @api_router.get("/analytics/summary")
        async def get_analytics_summary(user: Dict[str, Any] = Depends(require_auth)):
            """Get analytics summary data"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            
            # TODO: Calculate real metrics from database
            summary = {
                'total_properties': 2847,
                'notifications_sent': 156,
                'active_profiles': 3,
                'uptime_percentage': 98.7,
                'properties_last_24h': 47,
                'notifications_last_24h': 12,
                'avg_response_time': '2.3s',
                'successful_scans': 1247,
                'failed_scans': 15
            }
            
            return summary
        
        @api_router.get("/analytics/recent-activity")
        async def get_recent_activity(
            limit: int = Query(default=20, le=100),
            user: Dict[str, Any] = Depends(require_auth)
        ):
            """Get recent system activity"""
            # TODO: Get real activity from logs/database
            activities = [
                {
                    'id': 'activity_1',
                    'title': 'New property found',
                    'description': '2 room apartment in Florentin for ₪4,800',
                    'type': 'property_found',
                    'timestamp': datetime.now().isoformat(),
                    'profile_name': 'Tel Aviv Apartments'
                },
                {
                    'id': 'activity_2',
                    'title': 'Notification sent',
                    'description': 'Telegram message sent successfully',
                    'type': 'notification_sent',
                    'timestamp': (datetime.now()).isoformat(),
                    'profile_name': 'Tel Aviv Apartments'
                },
                {
                    'id': 'activity_3',
                    'title': 'Scan completed',
                    'description': 'Yad2 scan found 15 new listings',
                    'type': 'scan_completed',
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Yad2'
                },
                {
                    'id': 'activity_4',
                    'title': 'Profile activated',
                    'description': 'Profile "Budget Studios" has been activated',
                    'type': 'profile_activated',
                    'timestamp': datetime.now().isoformat(),
                    'profile_name': 'Budget Studios'
                }
            ]
            
            # Apply limit
            activities = activities[:limit]
            
            return {"activity": activities, "total": len(activities)}
        
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
        
        # Yad2 Configuration Routes
        
        @api_router.get("/yad2/config")
        async def get_yad2_config(user: Dict[str, Any] = Depends(require_auth)):
            """Get Yad2 configuration"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            settings = data_store.get_yad2_settings(user_id)
            
            # Return config in the format expected by frontend
            config = {
                'is_active': settings.get('enabled', True),
                'scan_interval': settings.get('scan_frequency', 300) // 60,  # Convert seconds to minutes
                'last_scan': settings.get('last_scan'),
                'search_urls': settings.get('search_urls', []),
                'status': 'connected' if settings.get('enabled', True) else 'disconnected',
                'total_urls': len(settings.get('search_urls', [])),
                'active_urls': len([url for url in settings.get('search_urls', []) if url.get('active', True)])
            }
            
            return config
        
        @api_router.post("/yad2/config")
        async def update_yad2_config(config_data: Dict[str, Any], user: Dict[str, Any] = Depends(require_auth)):
            """Update Yad2 configuration"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            
            # Extract and validate config data
            scan_interval = config_data.get('scan_interval', 5)  # minutes
            is_active = config_data.get('is_active', True)
            
            # Convert minutes to seconds for storage
            scan_frequency = scan_interval * 60
            
            # Update settings
            updated_settings = {
                'enabled': is_active,
                'scan_frequency': scan_frequency,
                'updated_at': datetime.now().isoformat()
            }
            
            data_store.update_yad2_settings(user_id, updated_settings)
            
            return {"message": "Yad2 configuration updated successfully", "config": updated_settings}
        
        # Telegram Configuration Routes
        
        @api_router.get("/telegram/config")
        async def get_telegram_config(user: Dict[str, Any] = Depends(require_auth)):
            """Get Telegram configuration"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            settings = data_store.get_telegram_settings(user_id)
            
            config = {
                'chat_id': settings.get('chat_id', ''),
                'is_connected': bool(settings.get('chat_id')),
                'bot_username': 'RealtyScanner_bot',
                'enabled': settings.get('enabled', True),
                'last_message_sent': settings.get('last_message_sent'),
                'total_messages_sent': settings.get('total_messages_sent', 0)
            }
            
            return config
        
        @api_router.post("/telegram/config")
        async def update_telegram_config(config_data: Dict[str, Any], user: Dict[str, Any] = Depends(require_auth)):
            """Update Telegram configuration"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            
            # Extract chat_id and validate
            chat_id = config_data.get('chat_id', '').strip()
            if not chat_id:
                raise HTTPException(status_code=400, detail="Chat ID is required")
            
            # Update settings
            updated_settings = {
                'chat_id': chat_id,
                'enabled': True,
                'updated_at': datetime.now().isoformat()
            }
            
            data_store.update_telegram_settings(user_id, updated_settings)
            
            return {"message": "Telegram configuration updated successfully", "config": updated_settings}
        
        @api_router.post("/telegram/find-chat-id")
        async def find_telegram_chat_id(user: Dict[str, Any] = Depends(require_auth)):
            """Find Telegram chat ID from recent messages"""
            # This would typically check recent messages from the bot
            # For demo purposes, return a mock response
            
            # In real implementation, this would:
            # 1. Get recent updates from Telegram API
            # 2. Find the most recent chat that sent /start
            # 3. Return the chat_id
            
            return {
                "chat_id": "123456789",
                "found": True,
                "message": "Chat ID found from recent messages"
            }
        
        @api_router.post("/telegram/test")
        async def test_telegram_connection(user: Dict[str, Any] = Depends(require_auth)):
            """Test Telegram connection by sending a test message"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            settings = data_store.get_telegram_settings(user_id)
            
            chat_id = settings.get('chat_id')
            if not chat_id:
                raise HTTPException(status_code=400, detail="No chat ID configured")
            
            # In real implementation, this would send a test message via Telegram API
            # For demo purposes, simulate success
            
            return {
                "success": True,
                "message": "Test message sent successfully",
                "chat_id": chat_id
            }
        
        # Facebook Configuration Routes
        
        @api_router.get("/facebook/status")
        async def get_facebook_status(user: Dict[str, Any] = Depends(require_auth)):
            """Get Facebook connection status"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            settings = data_store.get_facebook_settings(user_id)
            
            status = {
                'is_connected': settings.get('is_connected', False),
                'login_status': settings.get('login_status', 'disconnected'),
                'session_expires': settings.get('session_expires'),
                'groups': settings.get('groups', []),
                'total_groups': len(settings.get('groups', [])),
                'active_groups': len([g for g in settings.get('groups', []) if g.get('active', True)]),
                'last_scan': settings.get('last_scan'),
                'scan_enabled': settings.get('scan_enabled', False)
            }
            
            return status
        
        @api_router.post("/facebook/connect")
        async def connect_facebook(user: Dict[str, Any] = Depends(require_auth)):
            """Initiate Facebook connection"""
            # In real implementation, this would:
            # 1. Start a Playwright browser session
            # 2. Navigate to Facebook login
            # 3. Wait for user to login
            # 4. Save session cookies
            
            # For demo purposes, simulate connection process
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            
            # Update Facebook settings to show connected
            updated_settings = {
                'is_connected': True,
                'login_status': 'connected',
                'session_expires': (datetime.now() + timedelta(days=30)).isoformat(),
                'connected_at': datetime.now().isoformat()
            }
            
            data_store.update_facebook_settings(user_id, updated_settings)
            
            return {
                "success": True,
                "message": "Facebook connection established",
                "redirect_url": "https://facebook.com/login"  # In real implementation
            }
        
        @api_router.post("/facebook/groups")
        async def add_facebook_group(group_data: Dict[str, Any], user: Dict[str, Any] = Depends(require_auth)):
            """Add Facebook group for scanning"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            
            group_url = group_data.get('group_url', '').strip()
            if not group_url:
                raise HTTPException(status_code=400, detail="Group URL is required")
            
            # Extract group info from URL (simplified)
            group_id = group_url.split('/')[-1] if '/' in group_url else group_url
            
            new_group = {
                'id': f"group_{group_id}",
                'url': group_url,
                'name': group_data.get('name', f"Group {group_id}"),
                'active': True,
                'added_at': datetime.now().isoformat(),
                'last_scan': None,
                'total_posts_found': 0
            }
            
            # Update settings
            settings = data_store.get_facebook_settings(user_id)
            groups = settings.get('groups', [])
            groups.append(new_group)
            
            data_store.update_facebook_settings(user_id, {'groups': groups})
            
            return {"message": "Facebook group added successfully", "group": new_group}
        
        @api_router.delete("/facebook/groups/{group_id}")
        async def remove_facebook_group(group_id: str, user: Dict[str, Any] = Depends(require_auth)):
            """Remove Facebook group from scanning"""
            from .data_store import get_data_store
            
            data_store = get_data_store()
            user_id = user.get('id', 'user_1')
            
            settings = data_store.get_facebook_settings(user_id)
            groups = settings.get('groups', [])
            
            # Remove group with matching ID
            original_length = len(groups)
            groups = [g for g in groups if g['id'] != group_id]
            
            if len(groups) == original_length:
                raise HTTPException(status_code=404, detail="Group not found")
            
            data_store.update_facebook_settings(user_id, {'groups': groups})
            
            return {"message": "Facebook group removed successfully"}

        return api_router
        
    except ImportError as e:
        logger.error(f"Failed to import FastAPI dependencies: {e}")
        # Return a mock router that won't break the application
        return None
