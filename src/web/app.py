"""
FastAPI application factory and configuration
"""

import os
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path

logger = logging.getLogger(__name__)

# Global app instance
app_instance = None

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="RealtyScanner Management Dashboard",
        description="Web interface for managing property search profiles and notifications",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # Configure middleware
    setup_middleware(app)
    
    # Setup routes
    setup_routes(app)
    
    # Setup static files and templates
    setup_static_files(app)
    
    logger.info("✅ FastAPI application created and configured")
    return app

def setup_middleware(app: FastAPI):
    """Configure middleware"""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Session middleware for authentication
    secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    app.add_middleware(SessionMiddleware, secret_key=secret_key)
    
    logger.info("✅ Middleware configured")

def setup_routes(app: FastAPI):
    """Setup API routes"""
    
    from .auth import auth_router
    from .api import create_api_router
    from .websocket import websocket_router
    
    # Create API router
    api_router = create_api_router()
    
    # Include routers only if they exist
    if auth_router:
        app.include_router(auth_router, prefix="/auth", tags=["authentication"])
    
    if api_router:
        app.include_router(api_router, prefix="/api", tags=["api"])
    
    if websocket_router:
        app.include_router(websocket_router, prefix="/ws", tags=["websocket"])
    
    # Root route
    @app.get("/")
    async def root(request: Request):
        """Root route - redirect to dashboard"""
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/dashboard")
    
    # Dashboard route
    @app.get("/dashboard")
    async def dashboard(request: Request):
        """Main dashboard page"""
        templates = get_templates()
        return templates.TemplateResponse("dashboard_refactored.html", {"request": request})
    
    # Profile routes for SPA navigation
    @app.get("/profiles")
    async def profiles_page(request: Request):
        """Profiles page"""
        templates = get_templates()
        return templates.TemplateResponse("dashboard_refactored.html", {"request": request})
    
    @app.get("/telegram")
    async def telegram_page(request: Request):
        """Telegram settings page"""
        templates = get_templates()
        return templates.TemplateResponse("dashboard_refactored.html", {"request": request})
    
    @app.get("/facebook")
    async def facebook_page(request: Request):
        """Facebook settings page"""
        templates = get_templates()
        return templates.TemplateResponse("dashboard_refactored.html", {"request": request})
    
    @app.get("/yad2")
    async def yad2_page(request: Request):
        """Yad2 settings page"""
        templates = get_templates()
        return templates.TemplateResponse("dashboard_refactored.html", {"request": request})
    
    @app.get("/notifications")
    async def notifications_page(request: Request):
        """Notifications page"""
        templates = get_templates()
        return templates.TemplateResponse("dashboard_refactored.html", {"request": request})
    
    @app.get("/settings")
    async def settings_page(request: Request):
        """Settings page"""
        templates = get_templates()
        return templates.TemplateResponse("dashboard_refactored.html", {"request": request})
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "realtyscanner-web"}
    
    logger.info("✅ Routes configured")

def setup_static_files(app: FastAPI):
    """Setup static files and templates"""
    
    web_dir = Path(__file__).parent
    static_dir = web_dir / "static"
    templates_dir = web_dir / "templates"
    
    # Create directories if they don't exist
    static_dir.mkdir(exist_ok=True)
    templates_dir.mkdir(exist_ok=True)
    
    # Mount static files
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    logger.info("✅ Static files and templates configured")

def get_templates():
    """Get Jinja2 templates instance"""
    web_dir = Path(__file__).parent
    templates_dir = web_dir / "templates"
    return Jinja2Templates(directory=str(templates_dir))

def get_app() -> FastAPI:
    """Get or create the global app instance"""
    global app_instance
    if app_instance is None:
        app_instance = create_app()
    return app_instance
