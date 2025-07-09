#!/usr/bin/env python3
"""
CLI runner for Yad2 bypass testing

This script provides a command-line interface to run the Yad2 bypass tester
with various options and configurations.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from scrapers.yad2_bypass import Yad2BypassTester
from scrapers.yad2_config import USER_AGENTS, TEST_URLS, API_ENDPOINTS, REQUEST_SETTINGS


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('yad2_bypass.log')
        ]
    )


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='Yad2 Bypass Tester - Test different strategies to bypass ShieldSquare protection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Run all strategies
  %(prog)s --strategy user-agents    # Run only user agent strategy
  %(prog)s --strategy simple-urls    # Run only simple URL strategy
  %(prog)s --strategy api-endpoints  # Run only API endpoint strategy
  %(prog)s --output results/         # Custom output directory
  %(prog)s --verbose                 # Enable verbose logging
        """
    )
    
    parser.add_argument(
        '--strategy', 
        choices=['user-agents', 'simple-urls', 'api-endpoints', 'all'],
        default='all',
        help='Which strategy to run (default: all)'
    )
    
    parser.add_argument(
        '--output', 
        default='yad2_bypass_results',
        help='Output directory for results (default: yad2_bypass_results)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually running tests'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=REQUEST_SETTINGS['timeout'],
        help=f'Request timeout in seconds (default: {REQUEST_SETTINGS["timeout"]})'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Print banner
    print("=" * 60)
    print("🔧 Yad2 Bypass Tester")
    print("=" * 60)
    print(f"Strategy: {args.strategy}")
    print(f"Output directory: {args.output}")
    print(f"Verbose logging: {args.verbose}")
    print(f"Dry run: {args.dry_run}")
    print("=" * 60)
    
    if args.dry_run:
        print("\n🧪 DRY RUN MODE - No actual requests will be made")
        print(f"\nWould test the following:")
        
        if args.strategy in ['user-agents', 'all']:
            print(f"- User Agent Strategy: {len(USER_AGENTS)} user agents")
            
        if args.strategy in ['simple-urls', 'all']:
            print(f"- Simple URL Strategy: {len(TEST_URLS)} URLs")
            
        if args.strategy in ['api-endpoints', 'all']:
            print(f"- API Endpoint Strategy: {len(API_ENDPOINTS)} endpoints")
            
        print(f"\nResults would be saved to: {args.output}/")
        return
    
    # Initialize the tester
    try:
        tester = Yad2BypassTester(output_dir=args.output)
        
        logger.info("Starting Yad2 bypass testing...")
        success_content = None
        
        # Run selected strategies
        if args.strategy in ['user-agents', 'all']:
            print("\n🔍 Testing User Agent Strategy...")
            success_content = tester.test_strategy_1_different_user_agents()
            
            if success_content:
                print("✅ User Agent strategy succeeded!")
                if args.strategy != 'all':
                    return analyze_and_finish(tester, success_content)
        
        if args.strategy in ['simple-urls', 'all'] and not success_content:
            print("\n🔍 Testing Simple URL Strategy...")
            success_content = tester.test_strategy_2_simple_search()
            
            if success_content:
                print("✅ Simple URL strategy succeeded!")
                if args.strategy != 'all':
                    return analyze_and_finish(tester, success_content)
        
        if args.strategy in ['api-endpoints', 'all'] and not success_content:
            print("\n🔍 Testing API Endpoint Strategy...")
            api_data = tester.test_strategy_3_api_endpoints()
            
            if api_data:
                print("✅ API endpoint strategy succeeded!")
                return analyze_and_finish(tester, None, api_data)
        
        # Final results
        print("\n" + "=" * 60)
        print("📊 FINAL RESULTS")
        print("=" * 60)
        
        if success_content or (args.strategy == 'api-endpoints' and 'api_data' in locals()):
            print("✅ SUCCESS! Found working bypass method(s)")
            print(f"📁 Results saved to: {args.output}/")
        else:
            print("❌ All strategies failed")
            print("🛡️  ShieldSquare protection appears to be very strong")
        
        # Print strategy results
        print(f"\n📈 Successful strategies: {len(tester.results['successful_strategies'])}")
        for strategy in tester.results['successful_strategies']:
            print(f"  ✅ {strategy['strategy']}")
            
        print(f"\n📉 Failed strategies: {len(tester.results['failed_strategies'])}")
        for strategy in tester.results['failed_strategies']:
            print(f"  ❌ {strategy}")
            
        print(f"\n📁 Files saved: {len(tester.results['saved_files'])}")
        for file_path in tester.results['saved_files']:
            print(f"  📄 {file_path}")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def analyze_and_finish(tester, success_content=None, api_data=None):
    """Analyze results and finish execution"""
    if success_content:
        print("\n🔍 Analyzing successful response...")
        tester.analyze_page_structure(success_content)
    
    if api_data:
        print(f"\n📊 API data contains {len(api_data) if isinstance(api_data, list) else 'unknown'} items")
    
    print("\n✅ Testing completed successfully!")


if __name__ == "__main__":
    main()
