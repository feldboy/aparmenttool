#!/usr/bin/env python3
"""
Hello World Script for RealtyScanner Agent

This script validates that the basic project setup is working correctly.
It tests:
1. Python environment and imports
2. Environment variable loading
3. Basic logging setup
4. Agno framework integration (if available)

Run with: python scripts/hello_world.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main():
    print("🏠 RealtyScanner Agent - Hello World Script")
    print("=" * 50)
    
    # Test 1: Python version
    print(f"✅ Python version: {sys.version}")
    
    # Test 2: Environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded successfully")
    except ImportError:
        print("⚠️  python-dotenv not installed yet")
    
    # Test 3: Basic imports
    try:
        import json  # noqa: F401
        import logging  # noqa: F401
        print("✅ Standard library imports working")
    except ImportError as e:
        print(f"❌ Standard library import failed: {e}")
        return False
    
    # Test 4: Project structure
    project_root = Path(__file__).parent.parent
    required_dirs = ["src", "tests", "config", "scripts", "docs"]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not (project_root / dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    else:
        print("✅ Project directory structure is correct")
    
    # Test 5: Configuration files
    config_files = [".env.example", "pyproject.toml", "README.md", ".gitignore"]
    missing_files = []
    
    for file_name in config_files:
        if not (project_root / file_name).exists():
            missing_files.append(file_name)
    
    if missing_files:
        print(f"❌ Missing configuration files: {missing_files}")
        return False
    else:
        print("✅ All required configuration files present")
    
    # Test 6: Try importing Agno (if installed)
    try:
        import agno
        print(f"✅ Agno framework available (version: {agno.__version__ if hasattr(agno, '__version__') else 'unknown'})")
    except ImportError:
        print("⚠️  Agno framework not installed yet (will be installed with Poetry)")
    
    print("\n" + "=" * 50)
    print("🎉 Hello World test completed successfully!")
    print("\nNext steps:")
    print("1. Install dependencies: poetry install")
    print("2. Copy .env.example to .env and configure your API keys")
    print("3. Start implementing Epic 1.2: MongoDB Database Schema & Connection")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
