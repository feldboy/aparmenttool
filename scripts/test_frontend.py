#!/usr/bin/env python3
"""
Test script to verify the refactored frontend works correctly
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_frontend_files():
    """Test that all required frontend files exist"""
    print("🔍 Testing frontend files...")
    
    base_dir = Path(__file__).parent.parent / "src" / "web"
    
    # Check required files
    required_files = [
        "templates/dashboard_refactored.html",
        "static/js/app.js",
        "static/js/api.js",
        "static/js/utils.js",
        "static/js/components.js",
        "static/js/components-extended.js",
        "static/css/dashboard.css"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = base_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required frontend files exist")
    return True

def test_js_syntax():
    """Basic syntax check for JavaScript files"""
    print("\n🔍 Testing JavaScript syntax...")
    
    base_dir = Path(__file__).parent.parent / "src" / "web" / "static" / "js"
    
    js_files = [
        "app.js",
        "api.js", 
        "utils.js",
        "components.js",
        "components-extended.js"
    ]
    
    for js_file in js_files:
        file_path = base_dir / js_file
        if file_path.exists():
            try:
                # Basic syntax check - look for common issues
                content = file_path.read_text()
                
                # Check for basic syntax issues
                if content.count('{') != content.count('}'):
                    print(f"❌ {js_file}: Mismatched braces")
                    return False
                
                if content.count('(') != content.count(')'):
                    print(f"❌ {js_file}: Mismatched parentheses")
                    return False
                
                print(f"✅ {js_file}: Basic syntax OK")
                
            except Exception as e:
                print(f"❌ {js_file}: Error reading file - {e}")
                return False
    
    print("✅ JavaScript syntax checks passed")
    return True

def test_css_syntax():
    """Basic syntax check for CSS files"""
    print("\n🔍 Testing CSS syntax...")
    
    css_file = Path(__file__).parent.parent / "src" / "web" / "static" / "css" / "dashboard.css"
    
    if css_file.exists():
        try:
            content = css_file.read_text()
            
            # Check for basic CSS syntax issues
            if content.count('{') != content.count('}'):
                print(f"❌ dashboard.css: Mismatched braces")
                return False
            
            # Check for CSS variable definitions
            if '--primary-color' not in content:
                print(f"❌ dashboard.css: Missing CSS variables")
                return False
            
            print(f"✅ dashboard.css: Basic syntax OK")
            
        except Exception as e:
            print(f"❌ dashboard.css: Error reading file - {e}")
            return False
    
    print("✅ CSS syntax checks passed")
    return True

def test_html_structure():
    """Test HTML template structure"""
    print("\n🔍 Testing HTML structure...")
    
    template_file = Path(__file__).parent.parent / "src" / "web" / "templates" / "dashboard_refactored.html"
    
    if template_file.exists():
        try:
            content = template_file.read_text()
            
            # Check for required elements
            required_elements = [
                'id="global-loading"',
                'id="sidebar"',
                'id="dashboard"',
                'id="profiles"',
                'id="telegram"',
                'id="facebook"',
                'id="yad2"',
                'id="notifications"',
                'id="settings"',
                'data-nav=',
                'class="content-section"'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                print(f"❌ Missing HTML elements: {missing_elements}")
                return False
            
            print(f"✅ dashboard_refactored.html: Required elements found")
            
        except Exception as e:
            print(f"❌ dashboard_refactored.html: Error reading file - {e}")
            return False
    
    print("✅ HTML structure checks passed")
    return True

def run_all_tests():
    """Run all frontend tests"""
    print("🚀 Running frontend refactoring tests...\n")
    
    tests = [
        test_frontend_files,
        test_js_syntax,
        test_css_syntax,
        test_html_structure
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            failed += 1
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All frontend tests passed! The refactored frontend is ready.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
