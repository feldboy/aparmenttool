#!/usr/bin/env python3
"""
RealtyScanner Services Startup Script

This script starts all the essential services for the RealtyScanner Agent:
1. Web Dashboard (FastAPI)
2. Telegram Bot (for notifications)
3. Background Worker (for scanning)

Usage:
    python start_services.py [--web-only] [--bot-only] [--worker-only]
"""

import sys
import os
import asyncio
import argparse
import logging
import subprocess
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set"""
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    missing_vars = []
    
    # Check required variables
    required_vars = {
        'SECRET_KEY': 'Secret key for web dashboard',
        'MONGODB_URI': 'MongoDB connection string',
        'TELEGRAM_BOT_TOKEN': 'Telegram bot token from @BotFather'
    }
    
    for var, description in required_vars.items():
        if not os.getenv(var) or os.getenv(var) == f"your_{var.lower()}_here":
            missing_vars.append(f"  ❌ {var}: {description}")
    
    if missing_vars:
        print("🔧 Missing Environment Variables:")
        print("\n".join(missing_vars))
        print("\n📝 Please update your .env file with the required values.")
        return False
    
    return True

def start_web_server():
    """Start the web dashboard server"""
    print("🌐 Starting Web Dashboard Server...")
    python_exe = sys.executable
    cmd = [
        python_exe, 
        str(project_root / "src" / "web" / "run_server.py"),
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    return subprocess.Popen(cmd, cwd=str(project_root))

def start_telegram_bot():
    """Start the Telegram bot"""
    print("🤖 Starting Telegram Bot...")
    python_exe = sys.executable
    cmd = [
        python_exe, 
        str(project_root / "src" / "telegram_bot" / "run_bot.py"),
        "--mode", "polling"
    ]
    return subprocess.Popen(cmd, cwd=str(project_root))

def start_background_worker():
    """Start the background worker"""
    print("⚙️ Starting Background Worker...")
    python_exe = sys.executable
    cmd = [
        python_exe, 
        str(project_root / "scripts" / "run_worker.py")
    ]
    return subprocess.Popen(cmd, cwd=str(project_root))

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description="Start RealtyScanner services")
    parser.add_argument("--web-only", action="store_true", help="Start web server only")
    parser.add_argument("--bot-only", action="store_true", help="Start Telegram bot only")
    parser.add_argument("--worker-only", action="store_true", help="Start background worker only")
    args = parser.parse_args()
    
    print("🏠 RealtyScanner Agent - Starting Services")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        return
    
    print("✅ Environment check passed!")
    
    # Start services
    processes = []
    
    try:
        if args.web_only:
            processes.append(start_web_server())
        elif args.bot_only:
            processes.append(start_telegram_bot())
        elif args.worker_only:
            processes.append(start_background_worker())
        else:
            # Start all services
            processes.append(start_web_server())
            processes.append(start_telegram_bot())
            processes.append(start_background_worker())
        
        print("\n🚀 Services started successfully!")
        print("\n📊 Access Points:")
        print("   Web Dashboard: http://localhost:8000")
        print("   Telegram Bot: Search for your bot in Telegram")
        print("   Logs: Check console output above")
        
        print("\n📝 To stop services, press Ctrl+C")
        
        # Wait for all processes
        for process in processes:
            process.wait()
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        for process in processes:
            process.terminate()
        print("✅ All services stopped.")
    
    except Exception as e:
        logger.error(f"Error starting services: {e}")
        for process in processes:
            process.terminate()

if __name__ == "__main__":
    main()
