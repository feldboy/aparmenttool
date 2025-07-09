"""
Configuration settings for Yad2 bypass testing
"""

# User agents to test (mobile agents often work better)
USER_AGENTS = [
    # Mobile user agents (often less blocked)
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Android 14; Mobile; rv:109.0) Gecko/118.0 Firefox/118.0',
    'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    
    # Older browser versions (sometimes bypass detection)
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    
    # Real browser headers from automation tools
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/120.0.0.0 Safari/537.36',
]

# URLs to test for simple search strategy
TEST_URLS = [
    "https://www.yad2.co.il/realestate/rent",
    "https://www.yad2.co.il/realestate/rent?city=5000",  # Tel Aviv
    "https://www.yad2.co.il/realestate/rent?priceMin=3000",
    "https://m.yad2.co.il/realestate/rent",  # Mobile version
    "https://www.yad2.co.il/realestate/rent?rooms=3-4",
]

# API endpoints to test
API_ENDPOINTS = [
    "https://www.yad2.co.il/api/pre-load/getFeed/realestate/rent",
    "https://www.yad2.co.il/api/search/realestate/rent",
    "https://api.yad2.co.il/search/realestate/rent",
    "https://www.yad2.co.il/api/feed/realestate/rent",
    "https://www.yad2.co.il/api/v1/realestate/search",
]

# Request settings
REQUEST_SETTINGS = {
    'timeout': 15,
    'delay_min': 2,
    'delay_max': 5,
    'max_retries': 3,
}

# Content detection patterns
HEBREW_INDICATORS = ['דירות', 'להשכרה', 'חדרים', 'ש"ח', '₪', 'חדר', 'מ"ר']

# CSS selectors to look for listing containers
LISTING_SELECTORS = [
    'div[data-testid="feed-item"]',
    '.feeditem',
    '.feed_item', 
    '[data-item-id]',
    '.feed-list-item',
    '.result-item',
    'div[class*="feed"]',
    'div[class*="item"]',
    'div[class*="listing"]',
    '.listing-card',
    '.property-card',
    '.apartment-item',
]

# Headers for different strategies
STANDARD_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

API_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
    'X-Requested-With': 'XMLHttpRequest',
}

# Output configuration
OUTPUT_CONFIG = {
    'save_html': True,
    'save_json': True,
    'max_content_preview': 100,
    'max_divs_to_analyze': 10,
}
