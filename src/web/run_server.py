#!/usr/bin/env python3
"""
Web Server Runner for RealtyScanner Management Dashboard

This script starts the FastAPI web server for the property management dashboard.

Usage:
    python src/web/run_server.py [--host 0.0.0.0] [--port 8000] [--reload]

Environment Variables:
    SECRET_KEY - Required: Secret key for session management
    DATABASE_URL - Optional: MongoDB connection string
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def validate_environment():
    """Validate required environment variables"""
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        logger.warning("SECRET_KEY environment variable not set - using default (insecure)")
        os.environ["SECRET_KEY"] = "dev-secret-key-change-in-production"
    
    logger.info("✅ Environment validation passed")
    return True

def run_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Run the FastAPI server"""
    try:
        import uvicorn
        from web import get_app
        
        logger.info("🌐 Starting RealtyScanner Web Dashboard...")
        logger.info(f"🔗 Server URL: http://{host}:{port}")
        logger.info(f"📚 API Documentation: http://{host}:{port}/api/docs")
        
        # Get the FastAPI app
        app = get_app()
        
        # Run the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        
    except ImportError:
        logger.error("❌ FastAPI/Uvicorn not installed")
        logger.error("💡 Install required packages: pip install fastapi uvicorn[standard]")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="RealtyScanner Web Dashboard Server")
    parser.add_argument(
        "--host", 
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🐛 Debug logging enabled")
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    logger.info("🏠 RealtyScanner Web Dashboard")
    logger.info("=" * 50)
    
    try:
        success = run_server(args.host, args.port, args.reload)
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
