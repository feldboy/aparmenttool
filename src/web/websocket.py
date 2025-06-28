"""
WebSocket connections and real-time updates
"""

import logging
import json
from typing import Dict, List, Any, Set
from datetime import datetime

logger = logging.getLogger(__name__)

# WebSocket connection manager
class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Set[Any] = set()
        self.user_connections: Dict[str, Set[Any]] = {}
    
    async def connect(self, websocket, user_id: str):
        """Accept new WebSocket connection"""
        try:
            await websocket.accept()
            self.active_connections.add(websocket)
            
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)
            
            logger.info(f"WebSocket connection established for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection: {e}")
    
    def disconnect(self, websocket, user_id: str):
        """Remove WebSocket connection"""
        self.active_connections.discard(websocket)
        
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"WebSocket connection closed for user {user_id}")
    
    async def send_personal_message(self, message: str, user_id: str):
        """Send message to specific user"""
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id].copy():
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id}: {e}")
                    self.user_connections[user_id].discard(connection)
                    self.active_connections.discard(connection)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.active_connections.discard(connection)
    
    async def send_notification_update(self, user_id: str, notification_data: Dict[str, Any]):
        """Send notification update to user"""
        message = {
            'type': 'notification_update',
            'data': notification_data,
            'timestamp': datetime.now().isoformat()
        }
        await self.send_personal_message(json.dumps(message), user_id)
    
    async def send_property_update(self, user_id: str, property_data: Dict[str, Any]):
        """Send new property match to user"""
        message = {
            'type': 'property_match',
            'data': property_data,
            'timestamp': datetime.now().isoformat()
        }
        await self.send_personal_message(json.dumps(message), user_id)
    
    async def send_system_status(self, status_data: Dict[str, Any]):
        """Broadcast system status update"""
        message = {
            'type': 'system_status',
            'data': status_data,
            'timestamp': datetime.now().isoformat()
        }
        await self.broadcast(json.dumps(message))

# Global connection manager
websocket_manager = ConnectionManager()

# WebSocket router
websocket_router = None

def create_websocket_router():
    """Create WebSocket router"""
    global websocket_router
    
    if websocket_router is not None:
        return websocket_router
    
    try:
        from fastapi import APIRouter, WebSocket, WebSocketDisconnect
        
        websocket_router = APIRouter()
        
        @websocket_router.websocket("/notifications/{user_id}")
        async def websocket_endpoint(websocket: WebSocket, user_id: str):
            """WebSocket endpoint for real-time notifications"""
            await websocket_manager.connect(websocket, user_id)
            
            try:
                # Send initial connection confirmation
                await websocket.send_text(json.dumps({
                    'type': 'connection_established',
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat()
                }))
                
                # Keep connection alive and handle incoming messages
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # Handle different message types
                    if message.get('type') == 'ping':
                        await websocket.send_text(json.dumps({
                            'type': 'pong',
                            'timestamp': datetime.now().isoformat()
                        }))
                    elif message.get('type') == 'subscribe':
                        # Handle subscription to specific updates
                        await websocket.send_text(json.dumps({
                            'type': 'subscribed',
                            'subscription': message.get('subscription'),
                            'timestamp': datetime.now().isoformat()
                        }))
                    
            except WebSocketDisconnect:
                websocket_manager.disconnect(websocket, user_id)
            except Exception as e:
                logger.error(f"WebSocket error for user {user_id}: {e}")
                websocket_manager.disconnect(websocket, user_id)
        
        return websocket_router
        
    except ImportError:
        logger.warning("FastAPI not available - WebSocket features disabled")
        
        # Create mock router
        class MockWebSocketRouter:
            def websocket(self, path): return lambda f: f
        
        return MockWebSocketRouter()
    except Exception as e:
        logger.error(f"Failed to create WebSocket router: {e}")
        return None

# Utility functions for sending real-time updates

async def notify_property_match(user_id: str, property_data: Dict[str, Any], match_data: Dict[str, Any]):
    """Send real-time property match notification"""
    notification_data = {
        'property': property_data,
        'match': match_data,
        'type': 'property_match'
    }
    await websocket_manager.send_property_update(user_id, notification_data)

async def notify_profile_update(user_id: str, profile_data: Dict[str, Any]):
    """Send real-time profile update notification"""
    notification_data = {
        'profile': profile_data,
        'type': 'profile_update'
    }
    await websocket_manager.send_notification_update(user_id, notification_data)

async def notify_system_alert(alert_type: str, message: str, severity: str = 'info'):
    """Send system-wide alert"""
    alert_data = {
        'alert_type': alert_type,
        'message': message,
        'severity': severity
    }
    await websocket_manager.send_system_status(alert_data)

async def send_live_stats_update(stats_data: Dict[str, Any]):
    """Send live statistics update"""
    stats_message = {
        'type': 'stats_update',
        'data': stats_data,
        'timestamp': datetime.now().isoformat()
    }
    await websocket_manager.broadcast(json.dumps(stats_message))

# Initialize router
websocket_router = create_websocket_router()
