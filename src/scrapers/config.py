"""
Configuration for advanced scraping with anti-detection features

This module provides configuration for:
- Residential proxy rotation
- CAPTCHA solving services
- Browser fingerprinting evasion
- Rate limiting and behavioral randomization
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class ProxyType(Enum):
    """Supported proxy types"""
    RESIDENTIAL = "residential"
    DATACENTER = "datacenter"
    MOBILE = "mobile"

class CaptchaSolver(Enum):
    """Supported CAPTCHA solving services"""
    TWOCAPTCHA = "2captcha"
    ANTICAPTCHA = "anticaptcha"
    CAPMONSTER = "capmonster"
    DEATHBYCAPTCHA = "deathbycaptcha"

@dataclass
class ProxyConfig:
    """Proxy configuration"""
    proxy_type: ProxyType
    endpoints: List[str]
    username: Optional[str] = None
    password: Optional[str] = None
    rotate_interval: int = 300  # Seconds between proxy rotation
    max_retries: int = 3
    
@dataclass
class CaptchaConfig:
    """CAPTCHA solver configuration"""
    solver: CaptchaSolver
    api_key: str
    timeout: int = 300  # Maximum wait time for solve
    retry_count: int = 3

class ScrapingConfig:
    """Main scraping configuration"""
    
    def __init__(self):
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        self.proxy_config = self._load_proxy_config()
        self.captcha_config = self._load_captcha_config()
        self.behavioral_config = self._load_behavioral_config()
        
    def _load_proxy_config(self) -> Optional[ProxyConfig]:
        """Load proxy configuration from environment"""
        proxy_type = os.getenv("PROXY_TYPE", "residential")
        proxy_endpoints = os.getenv("PROXY_ENDPOINTS", "").split(",")
        proxy_username = os.getenv("PROXY_USERNAME")
        proxy_password = os.getenv("PROXY_PASSWORD")
        
        if not proxy_endpoints or not proxy_endpoints[0]:
            return None
            
        return ProxyConfig(
            proxy_type=ProxyType(proxy_type),
            endpoints=[ep.strip() for ep in proxy_endpoints if ep.strip()],
            username=proxy_username,
            password=proxy_password,
            rotate_interval=int(os.getenv("PROXY_ROTATE_INTERVAL", "300")),
            max_retries=int(os.getenv("PROXY_MAX_RETRIES", "3"))
        )
    
    def _load_captcha_config(self) -> Optional[CaptchaConfig]:
        """Load CAPTCHA solver configuration from environment"""
        solver_name = os.getenv("CAPTCHA_SOLVER", "2captcha")
        api_key = os.getenv("CAPTCHA_API_KEY")
        
        if not api_key:
            return None
            
        return CaptchaConfig(
            solver=CaptchaSolver(solver_name),
            api_key=api_key,
            timeout=int(os.getenv("CAPTCHA_TIMEOUT", "300")),
            retry_count=int(os.getenv("CAPTCHA_RETRY_COUNT", "3"))
        )
    
    def _load_behavioral_config(self) -> Dict[str, Any]:
        """Load behavioral randomization configuration"""
        return {
            "min_request_interval": float(os.getenv("MIN_REQUEST_INTERVAL", "2.0")),
            "max_request_interval": float(os.getenv("MAX_REQUEST_INTERVAL", "8.0")),
            "page_load_wait_min": int(os.getenv("PAGE_LOAD_WAIT_MIN", "3000")),
            "page_load_wait_max": int(os.getenv("PAGE_LOAD_WAIT_MAX", "8000")),
            "scroll_behavior": os.getenv("SCROLL_BEHAVIOR", "random").lower() == "true",
            "mouse_movements": os.getenv("MOUSE_MOVEMENTS", "true").lower() == "true",
            "typing_delays": os.getenv("TYPING_DELAYS", "true").lower() == "true",
        }
    
    def get_random_user_agent(self) -> str:
        """Get a random realistic user agent"""
        user_agents = [
            # Chrome on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            
            # Chrome on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            
            # Chrome on Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            
            # Safari on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            
            # Firefox
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
            
            # Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        ]
        
        import random
        return random.choice(user_agents)
    
    def get_realistic_headers(self) -> Dict[str, str]:
        """Get realistic HTTP headers"""
        user_agent = self.get_random_user_agent()
        
        # Determine browser type from user agent
        if "Chrome" in user_agent:
            sec_ch_ua = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
        elif "Firefox" in user_agent:
            sec_ch_ua = None
        elif "Safari" in user_agent and "Chrome" not in user_agent:
            sec_ch_ua = '"Not_A Brand";v="8", "Safari";v="17"'
        else:
            sec_ch_ua = '"Not_A Brand";v="8", "Chromium";v="120"'
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        # Add Chrome-specific headers
        if sec_ch_ua:
            headers.update({
                'Sec-CH-UA': sec_ch_ua,
                'Sec-CH-UA-Mobile': '?0',
                'Sec-CH-UA-Platform': '"macOS"' if "Macintosh" in user_agent else '"Windows"',
            })
        
        return headers

# Residential proxy providers (examples)
PROXY_PROVIDERS = {
    "brightdata": {
        "endpoints": ["brd-customer-{customer_id}-zone-{zone}:brd-customer-{customer_id}-zone-{zone}@brd.superproxy.io:22225"],
        "requires_auth": True,
        "rotation": "sticky_session"
    },
    "oxylabs": {
        "endpoints": ["pr.oxylabs.io:7777"],
        "requires_auth": True,
        "rotation": "endpoint_based"
    },
    "smartproxy": {
        "endpoints": ["gate.smartproxy.com:7000"],
        "requires_auth": True,
        "rotation": "sticky_session"
    },
    "webshare": {
        "endpoints": ["rotating-residential.webshare.io:80"],
        "requires_auth": True,
        "rotation": "automatic"
    }
}

# CAPTCHA solver APIs
CAPTCHA_SOLVERS = {
    "2captcha": {
        "submit_url": "http://2captcha.com/in.php",
        "result_url": "http://2captcha.com/res.php",
        "supported_types": ["image", "recaptcha", "hcaptcha", "funcaptcha"]
    },
    "anticaptcha": {
        "submit_url": "https://api.anti-captcha.com/createTask",
        "result_url": "https://api.anti-captcha.com/getTaskResult",
        "supported_types": ["image", "recaptcha", "hcaptcha", "funcaptcha"]
    },
    "capmonster": {
        "submit_url": "https://api.capmonster.cloud/createTask",
        "result_url": "https://api.capmonster.cloud/getTaskResult",
        "supported_types": ["image", "recaptcha", "hcaptcha", "funcaptcha"]
    }
}

# Default configuration
DEFAULT_CONFIG = {
    "firecrawl": {
        "timeout": 60,
        "max_retries": 3,
        "wait_for_page_load": True,
        "include_raw_html": True,
        "screenshot": False,
        "full_page_screenshot": False
    },
    "behavioral": {
        "min_request_interval": 2.0,
        "max_request_interval": 8.0,
        "page_load_wait_min": 3000,
        "page_load_wait_max": 8000,
        "random_scroll": True,
        "mouse_movements": True,
        "typing_delays": True
    },
    "detection_evasion": {
        "rotate_user_agent": True,
        "randomize_headers": True,
        "vary_viewport": True,
        "simulate_human_behavior": True,
        "avoid_bot_patterns": True
    }
}
