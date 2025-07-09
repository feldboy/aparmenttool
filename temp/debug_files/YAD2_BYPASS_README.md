# Yad2 Bypass Testing Project

This project contains tools and strategies for testing different approaches to access Yad2 real estate listings while dealing with ShieldSquare anti-bot protection.

## Project Structure

```
src/
├── scrapers/
│   ├── yad2_bypass.py      # Main bypass testing class
│   └── ...                 # Other scraping modules
└── ...

test_yad2_simple.py         # Simple test runner
run_yad2_bypass.py         # Advanced CLI runner
yad2_bypass_results/       # Output directory for test results
```

## Quick Start

1. Make sure your Python environment is activated:
   ```bash
   source .venv/bin/activate  # On macOS/Linux
   ```

2. Install dependencies (if not already installed):
   ```bash
   pip install requests beautifulsoup4
   ```

3. Run the simple test:
   ```bash
   python test_yad2_simple.py
   ```

4. Or use the advanced CLI runner:
   ```bash
   python run_yad2_bypass.py --help
   ```

## Testing Strategies

The project tests three main strategies:

### Strategy 1: Different User Agents
- Tests various mobile and desktop user agents
- Uses human-like delays and headers
- Often successful for bypassing basic bot detection

### Strategy 2: Simple Search URLs
- Tests different URL patterns
- Includes mobile versions
- Looks for specific selectors in HTML response

### Strategy 3: API Endpoints
- Tests potential JSON API endpoints
- Bypasses HTML parsing entirely
- May provide direct access to listing data

## Output

The tool saves successful responses to the `yad2_bypass_results/` directory:
- `successful_ua_response_X.html` - HTML responses from successful user agent tests
- `successful_simple_search.html` - HTML from successful URL tests
- `successful_api_response.json` - JSON data from successful API tests
- `test_results.json` - Complete test results summary

## Configuration

You can customize the testing by:
- Modifying user agent lists in `src/scrapers/yad2_bypass.py`
- Adding new URL patterns to test
- Adjusting delays and headers
- Adding new API endpoints to test

## Legal Notice

This tool is for educational and testing purposes only. Make sure to:
- Respect robots.txt and terms of service
- Use reasonable delays between requests
- Not overload the target servers
- Comply with applicable laws and regulations

## Success Indicators

The tool looks for:
- Absence of "shieldsquare" or "captcha" text
- Presence of Hebrew apartment-related text (דירות, להשכרה, etc.)
- Price symbols (₪)
- Room count indicators (חדר, חד)
- Proper HTML structure with listing containers
