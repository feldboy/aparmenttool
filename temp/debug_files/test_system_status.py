#!/usr/bin/env python3
"""
Comprehensive System Status Test
Tests all components of the RealtyScanner system
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test if all critical modules can be imported"""
    print("🔍 Testing imports...")
    results = {}
    
    # Database
    try:
        from db import get_db
        results['database'] = True
        print("✅ Database module imported successfully")
    except Exception as e:
        results['database'] = False
        print(f"❌ Database import failed: {e}")
    
    # Scrapers
    try:
        from scrapers.yad2 import Yad2Scraper
        from scrapers.facebook import FacebookScraper
        results['scrapers'] = True
        print("✅ Scrapers imported successfully")
    except Exception as e:
        results['scrapers'] = False
        print(f"❌ Scrapers import failed: {e}")
    
    # Notifications
    try:
        from notifications.dispatcher import NotificationDispatcher
        results['notifications'] = True
        print("✅ Notifications imported successfully")
    except Exception as e:
        results['notifications'] = False
        print(f"❌ Notifications import failed: {e}")
    
    # AI Agents
    try:
        from ai_agents.agent_manager import AIAgentManager
        results['ai_agents'] = True
        print("✅ AI Agents imported successfully")
    except Exception as e:
        results['ai_agents'] = False
        print(f"❌ AI Agents import failed: {e}")
    
    # Web App
    try:
        from web.app import get_app
        results['web_app'] = True
        print("✅ Web App imported successfully")
    except Exception as e:
        results['web_app'] = False
        print(f"❌ Web App import failed: {e}")
    
    return results

def test_database_connection():
    """Test database connectivity"""
    print("\n🗄️ Testing database connection...")
    
    try:
        from db import get_db
        db = get_db()
        
        # Test basic connection
        if hasattr(db, 'client'):
            db.client.admin.command('ping')
            print("✅ Database connection successful")
            
            # Test collections
            collections = db.client.list_database_names()
            print(f"📊 Available databases: {collections}")
            
            # Test specific collections
            if hasattr(db, 'search_profiles'):
                profiles = list(db.search_profiles.find().limit(3))
                print(f"🔍 Found {len(profiles)} search profiles")
                
            if hasattr(db, 'user_profiles'):
                user_profiles = list(db.user_profiles.find().limit(3))
                print(f"👤 Found {len(user_profiles)} user profiles")
                
            return True
        else:
            print("❌ Database client not available")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_scrapers():
    """Test scraper initialization and basic functionality"""
    print("\n🕷️ Testing scrapers...")
    
    try:
        from scrapers.yad2 import Yad2Scraper
        from scrapers.facebook import FacebookScraper
        
        # Test Yad2 scraper
        yad2 = Yad2Scraper()
        test_profile = {
            'price_range': {'min': 5000, 'max': 8000},
            'rooms_range': {'min': 2, 'max': 4},
            'location': {'city': 'Tel Aviv'}
        }
        
        search_url = yad2.construct_search_url(test_profile)
        print(f"✅ Yad2 scraper initialized, test URL: {search_url}")
        
        # Test Facebook scraper  
        facebook = FacebookScraper()
        print("✅ Facebook scraper initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        return False

async def test_worker_process():
    """Test if worker process is running correctly"""
    print("\n⚙️ Testing worker process...")
    
    try:
        # Check if worker log shows recent activity
        log_file = Path("logs/worker.log")
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    print(f"📝 Latest worker log: {last_line}")
                    
                    # Check if worker is actively scanning
                    recent_lines = lines[-10:]
                    scan_count = sum(1 for line in recent_lines if 'Scanning cycle completed' in line)
                    print(f"🔄 Recent scan cycles: {scan_count}")
                    
                    if scan_count > 0:
                        print("✅ Worker process is actively scanning")
                        return True
                    else:
                        print("⚠️ Worker process may not be scanning regularly")
                        return False
        else:
            print("❌ Worker log file not found")
            return False
            
    except Exception as e:
        print(f"❌ Worker process test failed: {e}")
        return False

def test_web_server():
    """Test web server functionality"""
    print("\n🌐 Testing web server...")
    
    try:
        import requests
        
        # Test health endpoint
        health_response = requests.get('http://localhost:8000/health', timeout=5)
        if health_response.status_code == 200:
            print("✅ Web server health check passed")
            
            # Test main page
            main_response = requests.get('http://localhost:8000/', timeout=5)
            if main_response.status_code == 200:
                print("✅ Main page accessible")
                return True
            else:
                print(f"⚠️ Main page returned status {main_response.status_code}")
                return False
        else:
            print(f"❌ Health check failed with status {health_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Web server test failed: {e}")
        return False

def test_notifications():
    """Test notification system"""
    print("\n📢 Testing notification system...")
    
    try:
        from notifications.dispatcher import NotificationDispatcher
        
        dispatcher = NotificationDispatcher()
        print("✅ Notification dispatcher initialized")
        
        # Test notification channels setup
        print("📱 Available notification channels:")
        # Add specific channel tests here
        
        return True
        
    except Exception as e:
        print(f"❌ Notification system test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 RealtyScanner System Status Test")
    print("=" * 50)
    
    results = {}
    
    # Run all tests
    results['imports'] = test_imports()
    results['database'] = test_database_connection()
    results['scrapers'] = test_scrapers()
    results['worker'] = await test_worker_process()
    results['web_server'] = test_web_server()
    results['notifications'] = test_notifications()
    
    # Summary
    print("\n📊 SYSTEM STATUS SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component.replace('_', ' ').title()}: {'PASS' if status else 'FAIL'}")
    
    print(f"\n🎯 Overall Status: {passed}/{total} components working")
    
    if passed == total:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
    elif passed >= total * 0.8:
        print("✅ MOSTLY OPERATIONAL - minor issues detected")
    elif passed >= total * 0.5:
        print("⚠️ PARTIALLY OPERATIONAL - significant issues detected")
    else:
        print("❌ CRITICAL ISSUES - system not functional")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
