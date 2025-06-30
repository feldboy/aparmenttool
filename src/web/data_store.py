"""
In-memory data store for the web dashboard
This will simulate a database until we connect to a real one
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import uuid

class InMemoryDataStore:
    """Simple in-memory data store for dashboard functionality"""
    
    def __init__(self):
        self.users = {}
        self.profiles = {}
        self.notifications = {}
        self.system_settings = {}
        self.telegram_settings = {}
        self.facebook_settings = {}
        self.yad2_settings = {}
        
        # Initialize with some mock data
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize with mock data for testing"""
        
        # Mock user
        user_id = "user_1"
        self.users[user_id] = {
            'id': user_id,
            'username': 'demo_user',
            'email': 'demo@example.com',
            'created_at': datetime.now().isoformat()
        }
        
        # Mock profiles
        profile_1 = {
            'id': 'profile_1',
            'user_id': user_id,
            'name': 'דירה בתל אביב',
            'price_range': {'min': 4000, 'max': 7000},
            'rooms_range': {'min': 2, 'max': 3},
            'location': {
                'city': 'תל אביב - יפו',
                'neighborhoods': ['פלורנטין', 'נווה צדק', 'רוטשילד'],
                'streets': []
            },
            'property_types': ['דירה', 'דירת גן'],
            'is_active': True,
            'created_at': '2025-06-25T10:00:00Z',
            'last_match': '2025-06-28T14:30:00Z'
        }
        
        profile_2 = {
            'id': 'profile_2',
            'user_id': user_id,
            'name': 'בית בירושלים',
            'price_range': {'min': 3000, 'max': 5000},
            'rooms_range': {'min': 3, 'max': 5},
            'location': {
                'city': 'ירושלים',
                'neighborhoods': ['גבעת שאול', 'רמות'],
                'streets': []
            },
            'property_types': ['בית', 'דירה'],
            'is_active': False,
            'created_at': '2025-06-20T15:20:00Z',
            'last_match': None
        }
        
        self.profiles['profile_1'] = profile_1
        self.profiles['profile_2'] = profile_2
        
        # Mock notifications
        notifications = [
            {
                'id': 'notif_1',
                'user_id': user_id,
                'profile_id': 'profile_1',
                'title': 'דירה חדשה בפלורנטין',
                'message': '3 חדרים, 5,800 ₪, פלורנטין - דירה מקסימה עם מרפסת',
                'source': 'יד2',
                'property_url': 'https://www.yad2.co.il/item/123456',
                'image_url': 'https://example.com/image1.jpg',
                'timestamp': '2025-06-28T15:30:00Z',
                'sent': True,
                'channel': 'telegram'
            },
            {
                'id': 'notif_2',
                'user_id': user_id,
                'profile_id': 'profile_1',
                'title': 'דירה בנווה צדק',
                'message': '2.5 חדרים, 6,200 ₪, נווה צדק - דירה משופצת בבניין בוטיק',
                'source': 'פייסבוק',
                'property_url': 'https://facebook.com/groups/telaviv/posts/123',
                'image_url': 'https://example.com/image2.jpg',
                'timestamp': '2025-06-28T12:15:00Z',
                'sent': True,
                'channel': 'telegram'
            },
            {
                'id': 'notif_3',
                'user_id': user_id,
                'profile_id': 'profile_1',
                'title': 'דירה ברוטשילד',
                'message': '3 חדרים, 6,500 ₪, שדרות רוטשילד - דירה עם חניה',
                'source': 'יד2',
                'property_url': 'https://www.yad2.co.il/item/789012',
                'image_url': None,
                'timestamp': '2025-06-27T18:45:00Z',
                'sent': True,
                'channel': 'telegram'
            }
        ]
        
        for notif in notifications:
            self.notifications[notif['id']] = notif
        
        # Mock settings
        self.telegram_settings[user_id] = {
            'enabled': False,
            'chat_id': '',
            'last_test': None,
            'connection_status': 'not_configured'
        }
        
        self.facebook_settings[user_id] = {
            'enabled': False,
            'session_valid': False,
            'groups': [],
            'last_login': None,
            'requires_reauth': True
        }
        
        self.yad2_settings[user_id] = {
            'enabled': True,
            'scan_frequency': 300,  # 5 minutes
            'search_urls': [],
            'last_scan': '2025-06-28T15:25:00Z'
        }
        
        self.system_settings[user_id] = {
            'notification_preferences': {
                'quiet_hours': {'start': '23:00', 'end': '07:00'},
                'include_images': True,
                'include_description': True,
                'max_description_length': 100,
                'max_notifications_per_hour': 10
            },
            'general_settings': {
                'language': 'he',
                'timezone': 'Asia/Jerusalem'
            }
        }
    
    # User methods
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.users.get(user_id)
    
    # Profile methods
    def get_profiles(self, user_id: str) -> List[Dict[str, Any]]:
        return [profile for profile in self.profiles.values() 
                if profile.get('user_id') == user_id]
    
    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        return self.profiles.get(profile_id)
    
    def create_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        profile_id = str(uuid.uuid4())
        profile = {
            'id': profile_id,
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_match': None,
            'is_active': True,
            **profile_data
        }
        self.profiles[profile_id] = profile
        return profile
    
    def update_profile(self, profile_id: str, profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if profile_id in self.profiles:
            self.profiles[profile_id].update(profile_data)
            self.profiles[profile_id]['updated_at'] = datetime.now().isoformat()
            return self.profiles[profile_id]
        return None
    
    def delete_profile(self, profile_id: str) -> bool:
        if profile_id in self.profiles:
            del self.profiles[profile_id]
            return True
        return False
    
    # Notification methods
    def get_notifications(self, user_id: str, limit: int = 50, offset: int = 0, 
                         profile_id: Optional[str] = None) -> List[Dict[str, Any]]:
        user_notifications = [notif for notif in self.notifications.values() 
                            if notif.get('user_id') == user_id]
        
        if profile_id:
            user_notifications = [notif for notif in user_notifications 
                                if notif.get('profile_id') == profile_id]
        
        # Sort by timestamp descending
        user_notifications.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Apply pagination
        return user_notifications[offset:offset + limit]
    
    def add_notification(self, user_id: str, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        notif_id = str(uuid.uuid4())
        notification = {
            'id': notif_id,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'sent': False,
            **notification_data
        }
        self.notifications[notif_id] = notification
        return notification
    
    # Telegram settings methods
    def get_telegram_settings(self, user_id: str) -> Dict[str, Any]:
        return self.telegram_settings.get(user_id, {
            'enabled': False,
            'chat_id': '',
            'last_test': None,
            'connection_status': 'not_configured'
        })
    
    def update_telegram_settings(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        if user_id not in self.telegram_settings:
            self.telegram_settings[user_id] = {}
        
        self.telegram_settings[user_id].update(settings)
        self.telegram_settings[user_id]['updated_at'] = datetime.now().isoformat()
        return self.telegram_settings[user_id]
    
    # Facebook settings methods
    def get_facebook_settings(self, user_id: str) -> Dict[str, Any]:
        return self.facebook_settings.get(user_id, {
            'enabled': False,
            'session_valid': False,
            'groups': [],
            'last_login': None,
            'requires_reauth': True
        })
    
    def update_facebook_settings(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        if user_id not in self.facebook_settings:
            self.facebook_settings[user_id] = {}
        
        self.facebook_settings[user_id].update(settings)
        self.facebook_settings[user_id]['updated_at'] = datetime.now().isoformat()
        return self.facebook_settings[user_id]
    
    # Yad2 settings methods
    def get_yad2_settings(self, user_id: str) -> Dict[str, Any]:
        return self.yad2_settings.get(user_id, {
            'enabled': True,
            'scan_frequency': 300,
            'search_urls': [],
            'last_scan': None
        })
    
    def update_yad2_settings(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        if user_id not in self.yad2_settings:
            self.yad2_settings[user_id] = {}
        
        self.yad2_settings[user_id].update(settings)
        self.yad2_settings[user_id]['updated_at'] = datetime.now().isoformat()
        return self.yad2_settings[user_id]
    
    # System settings methods
    def get_system_settings(self, user_id: str) -> Dict[str, Any]:
        return self.system_settings.get(user_id, {
            'notification_preferences': {
                'quiet_hours': {'start': '23:00', 'end': '07:00'},
                'include_images': True,
                'include_description': True,
                'max_description_length': 100,
                'max_notifications_per_hour': 10
            },
            'general_settings': {
                'language': 'he',
                'timezone': 'Asia/Jerusalem'
            }
        })
    
    def update_system_settings(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        if user_id not in self.system_settings:
            self.system_settings[user_id] = {}
        
        self.system_settings[user_id].update(settings)
        self.system_settings[user_id]['updated_at'] = datetime.now().isoformat()
        return self.system_settings[user_id]

# Global data store instance
data_store = InMemoryDataStore()

def get_data_store() -> InMemoryDataStore:
    """Get the global data store instance"""
    return data_store
