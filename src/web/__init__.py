"""
FastAPI Web Application for RealtyScanner Management Dashboard

This module provides a web interface for managing user profiles,
viewing notifications, and monitoring the RealtyScanner system.
"""

from .app import create_app, get_app
from .auth import auth_router
from .api import api_router
from .websocket import websocket_manager

__all__ = [
    'create_app',
    'get_app', 
    'auth_router',
    'api_router',
    'websocket_manager'
]
