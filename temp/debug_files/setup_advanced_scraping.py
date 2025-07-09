#!/usr/bin/env python3
"""
Setup script for advanced web scraping with ShieldSquare bypass

This script helps configure:
1. Firecrawl API
2. Residential proxy services
3. CAPTCHA solving services
4. Environment variables
"""

import os
import sys
import subprocess
import requests
import json
from typing import Dict, Any, Optional
from pathlib import Path

def print_banner():
    """Print setup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                  Advanced Scraping Setup                     ║
    ║                  ShieldSquare Bypass Tool                    ║
    ╚══════════════════════════════════════════════════════════════╝
    
    This script will help you configure:
    • Firecrawl API for headless browsing
    • Residential proxy rotation
    • CAPTCHA solving services
    • Anti-detection settings
    """
    print(banner)

def check_firecrawl_api(api_key: str) -> bool:
    """Check if Firecrawl API key is valid"""
    try:
        response = requests.get(
            "https://api.firecrawl.dev/v0/test",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error checking Firecrawl API: {e}")
        return False

def check_captcha_solver(solver: str, api_key: str) -> bool:
    """Check if CAPTCHA solver API key is valid"""
    try:
        if solver == "2captcha":
            response = requests.get(
                "http://2captcha.com/res.php",
                params={"key": api_key, "action": "getbalance"},
                timeout=10
            )
            return "ERROR" not in response.text
        elif solver == "anticaptcha":
            response = requests.post(
                "https://api.anti-captcha.com/getBalance",
                json={"clientKey": api_key},
                timeout=10
            )
            result = response.json()
            return result.get("errorId") == 0
        else:
            print(f"Unsupported CAPTCHA solver: {solver}")
            return False
    except Exception as e:
        print(f"Error checking CAPTCHA solver: {e}")
        return False

def install_requirements():
    """Install required Python packages"""
    print("Installing required packages...")
    
    packages = [
        "firecrawl-py",
        "requests",
        "beautifulsoup4",
        "selenium",
        "undetected-chromedriver",
        "python-dotenv",
        "pymongo",
        "pydantic",
        "python-telegram-bot"
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            return False
    
    return True

def configure_firecrawl():
    """Configure Firecrawl API"""
    print("\n🔥 Firecrawl Configuration")
    print("=" * 50)
    print("Firecrawl provides headless browser automation to bypass bot detection.")
    print("Get your API key from: https://firecrawl.dev/")
    
    api_key = input("Enter your Firecrawl API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Skipping Firecrawl configuration.")
        return None
    
    print("Testing Firecrawl API key...")
    if check_firecrawl_api(api_key):
        print("✅ Firecrawl API key is valid!")
        return api_key
    else:
        print("❌ Invalid Firecrawl API key. Please check and try again.")
        return None

def configure_proxy():
    """Configure residential proxy service"""
    print("\n🌐 Residential Proxy Configuration")
    print("=" * 50)
    print("Residential proxies help avoid detection by using real IP addresses.")
    print("\nSupported providers:")
    print("1. Bright Data (Luminati) - Most reliable")
    print("2. Oxylabs - Good performance")
    print("3. SmartProxy - Budget-friendly")
    print("4. WebShare - Affordable option")
    print("5. Skip proxy configuration")
    
    choice = input("Choose a proxy provider (1-5): ").strip()
    
    if choice == "5":
        print("Skipping proxy configuration.")
        return None
    
    proxy_configs = {
        "1": {
            "name": "Bright Data",
            "type": "residential",
            "endpoint_template": "brd-customer-{customer_id}-zone-{zone}:brd-customer-{customer_id}-zone-{zone}@brd.superproxy.io:22225",
            "fields": ["customer_id", "zone", "password"]
        },
        "2": {
            "name": "Oxylabs",
            "type": "residential",
            "endpoint_template": "pr.oxylabs.io:7777",
            "fields": ["username", "password"]
        },
        "3": {
            "name": "SmartProxy",
            "type": "residential",
            "endpoint_template": "gate.smartproxy.com:7000",
            "fields": ["username", "password"]
        },
        "4": {
            "name": "WebShare",
            "type": "residential",
            "endpoint_template": "rotating-residential.webshare.io:80",
            "fields": ["username", "password"]
        }
    }
    
    if choice not in proxy_configs:
        print("Invalid choice. Skipping proxy configuration.")
        return None
    
    config = proxy_configs[choice]
    print(f"\n{config['name']} Configuration:")
    
    proxy_data = {"provider": choice}
    for field in config["fields"]:
        value = input(f"Enter {field}: ").strip()
        if not value:
            print(f"❌ {field} is required. Skipping proxy configuration.")
            return None
        proxy_data[field] = value
    
    return proxy_data

def configure_captcha_solver():
    """Configure CAPTCHA solving service"""
    print("\n🤖 CAPTCHA Solver Configuration")
    print("=" * 50)
    print("CAPTCHA solvers help bypass human verification challenges.")
    print("\nSupported services:")
    print("1. 2Captcha - Most popular")
    print("2. Anti-Captcha - Fast solving")
    print("3. CapMonster - Good pricing")
    print("4. Skip CAPTCHA solver")
    
    choice = input("Choose a CAPTCHA solver (1-4): ").strip()
    
    if choice == "4":
        print("Skipping CAPTCHA solver configuration.")
        return None
    
    solvers = {
        "1": {"name": "2Captcha", "key": "2captcha", "url": "https://2captcha.com/"},
        "2": {"name": "Anti-Captcha", "key": "anticaptcha", "url": "https://anti-captcha.com/"},
        "3": {"name": "CapMonster", "key": "capmonster", "url": "https://capmonster.cloud/"}
    }
    
    if choice not in solvers:
        print("Invalid choice. Skipping CAPTCHA solver configuration.")
        return None
    
    solver = solvers[choice]
    print(f"\n{solver['name']} Configuration:")
    print(f"Get your API key from: {solver['url']}")
    
    api_key = input("Enter your API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Skipping CAPTCHA solver configuration.")
        return None
    
    print("Testing CAPTCHA solver API key...")
    if check_captcha_solver(solver["key"], api_key):
        print("✅ CAPTCHA solver API key is valid!")
        return {"solver": solver["key"], "api_key": api_key}
    else:
        print("❌ Invalid API key. Please check and try again.")
        return None

def create_env_file(configs: Dict[str, Any]):
    """Create environment configuration file"""
    print("\n📄 Creating Environment Configuration")
    print("=" * 50)
    
    env_content = []
    
    # Firecrawl configuration
    if configs.get("firecrawl"):
        env_content.extend([
            "# Firecrawl Configuration",
            f"FIRECRAWL_API_KEY={configs['firecrawl']}",
            ""
        ])
    
    # Proxy configuration
    if configs.get("proxy"):
        proxy = configs["proxy"]
        env_content.extend([
            "# Proxy Configuration",
            "PROXY_TYPE=residential"
        ])
        
        if proxy["provider"] == "1":  # Bright Data
            env_content.extend([
                f"PROXY_ENDPOINTS=brd-customer-{proxy['customer_id']}-zone-{proxy['zone']}:{proxy['password']}@brd.superproxy.io:22225",
                f"PROXY_USERNAME=brd-customer-{proxy['customer_id']}-zone-{proxy['zone']}",
                f"PROXY_PASSWORD={proxy['password']}"
            ])
        elif proxy["provider"] == "2":  # Oxylabs
            env_content.extend([
                "PROXY_ENDPOINTS=pr.oxylabs.io:7777",
                f"PROXY_USERNAME={proxy['username']}",
                f"PROXY_PASSWORD={proxy['password']}"
            ])
        elif proxy["provider"] == "3":  # SmartProxy
            env_content.extend([
                "PROXY_ENDPOINTS=gate.smartproxy.com:7000",
                f"PROXY_USERNAME={proxy['username']}",
                f"PROXY_PASSWORD={proxy['password']}"
            ])
        elif proxy["provider"] == "4":  # WebShare
            env_content.extend([
                "PROXY_ENDPOINTS=rotating-residential.webshare.io:80",
                f"PROXY_USERNAME={proxy['username']}",
                f"PROXY_PASSWORD={proxy['password']}"
            ])
        
        env_content.extend([
            "PROXY_ROTATE_INTERVAL=300",
            "PROXY_MAX_RETRIES=3",
            ""
        ])
    
    # CAPTCHA solver configuration
    if configs.get("captcha"):
        captcha = configs["captcha"]
        env_content.extend([
            "# CAPTCHA Solver Configuration",
            f"CAPTCHA_SOLVER={captcha['solver']}",
            f"CAPTCHA_API_KEY={captcha['api_key']}",
            "CAPTCHA_TIMEOUT=300",
            "CAPTCHA_RETRY_COUNT=3",
            ""
        ])
    
    # Default behavioral settings
    env_content.extend([
        "# Behavioral Settings",
        "MIN_REQUEST_INTERVAL=2.0",
        "MAX_REQUEST_INTERVAL=8.0",
        "PAGE_LOAD_WAIT_MIN=3000",
        "PAGE_LOAD_WAIT_MAX=8000",
        "SCROLL_BEHAVIOR=true",
        "MOUSE_MOVEMENTS=true",
        "TYPING_DELAYS=true",
        "",
        "# Anti-Detection Settings",
        "ROTATE_USER_AGENTS=true",
        "RANDOMIZE_HEADERS=true",
        "VARY_VIEWPORT_SIZE=true",
        "SIMULATE_HUMAN_BEHAVIOR=true",
        "AVOID_BOT_PATTERNS=true",
        "",
        "# Performance Settings",
        "MAX_CONCURRENT_REQUESTS=3",
        "REQUEST_TIMEOUT=60",
        "MAX_RETRIES=3",
        "RETRY_DELAY=5",
        "",
        "# Database Configuration",
        "MONGODB_URI=mongodb://localhost:27017",
        "MONGODB_DATABASE=realty_scanner",
        "",
        "# Logging",
        "LOG_LEVEL=INFO",
        "LOG_CAPTCHA_ATTEMPTS=true",
        "LOG_PROXY_ROTATION=true",
        "LOG_DETECTION_EVENTS=true"
    ])
    
    # Write to file
    env_file = Path(".env.scraping")
    env_file.write_text("\n".join(env_content))
    
    print(f"✅ Environment configuration saved to {env_file}")
    print("\n⚠️  IMPORTANT: Keep your API keys secure!")
    print("   - Don't commit .env.scraping to version control")
    print("   - Use environment variables in production")

def create_gitignore():
    """Create/update .gitignore file"""
    gitignore_file = Path(".gitignore")
    
    entries_to_add = [
        "# Scraping configuration",
        ".env.scraping",
        "sessions/",
        "debug/",
        "*.log",
        "captcha_images/",
        "proxy_test_results.txt"
    ]
    
    existing_content = ""
    if gitignore_file.exists():
        existing_content = gitignore_file.read_text()
    
    new_entries = []
    for entry in entries_to_add:
        if entry not in existing_content:
            new_entries.append(entry)
    
    if new_entries:
        with gitignore_file.open("a") as f:
            f.write("\n" + "\n".join(new_entries) + "\n")
        print(f"✅ Updated .gitignore with scraping-related entries")

def create_test_script():
    """Create a test script to verify setup"""
    test_script = """#!/usr/bin/env python3
\"\"\"
Test script to verify scraping setup
\"\"\"

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scrapers.firecrawl_yad2 import FirecrawlYad2Scraper
from src.scrapers.config import ScrapingConfig
from dotenv import load_dotenv

def test_configuration():
    \"\"\"Test the scraping configuration\"\"\"
    load_dotenv(".env.scraping")
    
    print("Testing scraping configuration...")
    
    # Test Firecrawl API
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    if firecrawl_key:
        print("✅ Firecrawl API key found")
    else:
        print("❌ Firecrawl API key not found")
    
    # Test proxy configuration
    proxy_endpoints = os.getenv("PROXY_ENDPOINTS")
    if proxy_endpoints:
        print("✅ Proxy configuration found")
    else:
        print("⚠️  No proxy configuration found")
    
    # Test CAPTCHA solver
    captcha_key = os.getenv("CAPTCHA_API_KEY")
    if captcha_key:
        print("✅ CAPTCHA solver API key found")
    else:
        print("⚠️  No CAPTCHA solver configured")
    
    # Test scraper initialization
    try:
        scraper = FirecrawlYad2Scraper()
        print("✅ Scraper initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing scraper: {e}")
    
    print("\\nSetup verification complete!")

if __name__ == "__main__":
    test_configuration()
"""
    
    test_file = Path("test_scraping_setup.py")
    test_file.write_text(test_script)
    test_file.chmod(0o755)
    
    print(f"✅ Created test script: {test_file}")
    print("   Run with: python test_scraping_setup.py")

def main():
    """Main setup function"""
    print_banner()
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements. Exiting.")
        return
    
    configs = {}
    
    # Configure Firecrawl
    firecrawl_key = configure_firecrawl()
    if firecrawl_key:
        configs["firecrawl"] = firecrawl_key
    
    # Configure proxy
    proxy_config = configure_proxy()
    if proxy_config:
        configs["proxy"] = proxy_config
    
    # Configure CAPTCHA solver
    captcha_config = configure_captcha_solver()
    if captcha_config:
        configs["captcha"] = captcha_config
    
    # Create configuration files
    if configs:
        create_env_file(configs)
        create_gitignore()
        create_test_script()
        
        print("\n🎉 Setup Complete!")
        print("=" * 50)
        print("Your advanced scraping setup is ready!")
        print("\nNext steps:")
        print("1. Run: python test_scraping_setup.py")
        print("2. Test scraping: python -m src.scrapers.firecrawl_yad2")
        print("3. Monitor logs for any issues")
        print("\n⚠️  Remember:")
        print("- Keep your API keys secure")
        print("- Monitor your usage and costs")
        print("- Respect target website terms of service")
        print("- Use rate limiting to avoid overloading sites")
    else:
        print("\n❌ No configurations were set up.")
        print("Please re-run the script and provide the required information.")

if __name__ == "__main__":
    main()
