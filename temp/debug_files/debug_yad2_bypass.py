#!/usr/bin/env python3
"""
Debug version of Yad2 bypass test with more detailed logging
"""

import requests
import time
import random
from bs4 import BeautifulSoup
import os


def debug_strategy_1():
    """Debug version of strategy 1 with detailed logging"""
    print("=== DEBUG: Testing Different User Agents ===")
    
    user_agents = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Android 14; Mobile; rv:109.0) Gecko/118.0 Firefox/118.0',
        'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    ]
    
    base_url = "https://www.yad2.co.il/realestate/rent"
    
    for i, ua in enumerate(user_agents[:1]):  # Test only first one for debugging
        print(f"\nTrying User Agent {i+1}: {ua[:50]}...")
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        try:
            print("Making request...")
            time.sleep(random.uniform(2, 5))
            
            response = session.get(base_url, timeout=15)
            print(f"Status: {response.status_code}, Length: {len(response.content)}")
            
            # Debug: Show first 500 characters
            print(f"First 500 chars of response:")
            print("=" * 50)
            print(response.text[:500])
            print("=" * 50)
            
            # Check for ShieldSquare
            if 'shieldsquare' in response.text.lower() or 'captcha' in response.text.lower():
                print("❌ ShieldSquare detected")
            else:
                print("✅ No ShieldSquare detected")
                
                # Look for listings
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Debug: Check what Hebrew indicators we find
                hebrew_indicators = ['דירות', 'להשכרה', 'חדרים', 'אפריל', 'מאי']
                found_indicators = []
                for indicator in hebrew_indicators:
                    if indicator in response.text:
                        found_indicators.append(indicator)
                        print(f"✅ Found Hebrew indicator: {indicator}")
                
                if found_indicators:
                    print(f"✅ Found Hebrew apartment content: {found_indicators}")
                    
                    # Debug: Check file writing
                    filename = f'debug_response_{i+1}.html'
                    print(f"Attempting to write to: {filename}")
                    
                    try:
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        
                        # Verify file was written
                        if os.path.exists(filename):
                            file_size = os.path.getsize(filename)
                            print(f"✅ File written successfully: {filename} ({file_size} bytes)")
                            
                            # Read back and verify
                            with open(filename, 'r', encoding='utf-8') as f:
                                content = f.read()
                            print(f"✅ File read back successfully: {len(content)} characters")
                            
                            # Check if content matches
                            if content == response.text:
                                print("✅ File content matches response")
                            else:
                                print("❌ File content does not match response")
                        else:
                            print("❌ File was not created")
                            
                    except Exception as write_error:
                        print(f"❌ Error writing file: {write_error}")
                    
                    return response.text
                else:
                    print("❌ No Hebrew apartment content found")
                    
                    # Debug: Look for any Hebrew text at all
                    hebrew_chars = [chr(i) for i in range(0x0590, 0x05FF)]  # Hebrew Unicode range
                    has_hebrew = any(char in response.text for char in hebrew_chars)
                    print(f"Has any Hebrew text: {has_hebrew}")
                    
                    # Save the response anyway for debugging
                    debug_filename = f'debug_no_hebrew_{i+1}.html'
                    with open(debug_filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"Saved debug response to: {debug_filename}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None


if __name__ == "__main__":
    print("Running debug version of Yad2 bypass test...\n")
    debug_strategy_1()
