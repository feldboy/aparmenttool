#!/usr/bin/env python3
"""
Simple test runner for Yad2 bypass testing

This script runs the Yad2BypassTester directly without complex imports.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Now import and run the test
if __name__ == "__main__":
    print("Testing different strategies to bypass Yad2 ShieldSquare protection...\n")
    
    # Import the bypass tester
    try:
        from src.scrapers.yad2_bypass import Yad2BypassTester
        
        # Create tester instance
        tester = Yad2BypassTester()
        
        # Run all strategies
        results = tester.run_all_strategies()
        
        # Print final summary
        print("\n" + "="*50)
        print("FINAL SUMMARY")
        print("="*50)
        print(f"Successful strategies: {len(results['successful_strategies'])}")
        print(f"Failed strategies: {len(results['failed_strategies'])}")
        print(f"Files saved: {len(results['saved_files'])}")
        
        if results['successful_strategies']:
            print("\nSuccessful strategies:")
            for strategy in results['successful_strategies']:
                print(f"  ✅ {strategy['strategy']}")
        
        if results['failed_strategies']:
            print(f"\nFailed strategies:")
            for strategy in results['failed_strategies']:
                print(f"  ❌ {strategy}")
        
        if results['saved_files']:
            print(f"\nSaved files:")
            for file in results['saved_files']:
                print(f"  📁 {file}")
                
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)
