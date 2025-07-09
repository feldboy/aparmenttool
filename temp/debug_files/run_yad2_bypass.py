#!/usr/bin/env python3
"""
CLI runner for Yad2 bypass testing

This script provides a command-line interface to test different strategies
for bypassing Yad2's ShieldSquare protection.
"""

import argparse
import logging
import json
import sys
import os
from pathlib import Path

# Add src to path so we can import our modules
src_path = str(Path(__file__).parent / 'src')
sys.path.insert(0, src_path)

try:
    from scrapers.yad2_bypass import Yad2BypassTester
except ImportError:
    print("Error: Could not import Yad2BypassTester. Make sure the src/scrapers directory exists.")
    sys.exit(1)


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('yad2_bypass_test.log')
        ]
    )


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='Test different strategies to bypass Yad2 ShieldSquare protection'
    )
    
    parser.add_argument(
        '--output-dir',
        default='yad2_bypass_results',
        help='Directory to save results (default: yad2_bypass_results)'
    )
    
    parser.add_argument(
        '--strategy',
        choices=['1', '2', '3', 'all'],
        default='all',
        help='Which strategy to run (1: user agents, 2: simple URLs, 3: API endpoints, all: run all)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--save-results',
        action='store_true',
        help='Save results to JSON file'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Yad2 bypass testing...")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Strategy: {args.strategy}")
    
    # Create bypass tester
    tester = Yad2BypassTester(output_dir=args.output_dir)
    
    # Run selected strategy
    results = None
    
    if args.strategy == 'all':
        results = tester.run_all_strategies()
    elif args.strategy == '1':
        logger.info("Running Strategy 1: Different User Agents")
        success = tester.test_strategy_1_different_user_agents()
        if success:
            tester.analyze_page_structure(success)
        results = tester.get_results()
    elif args.strategy == '2':
        logger.info("Running Strategy 2: Simple Search URLs")
        success = tester.test_strategy_2_simple_search()
        if success:
            tester.analyze_page_structure(success)
        results = tester.get_results()
    elif args.strategy == '3':
        logger.info("Running Strategy 3: API Endpoints")
        api_data = tester.test_strategy_3_api_endpoints()
        if api_data:
            logger.info("Found working API endpoint!")
        results = tester.get_results()
    
    # Print summary
    if results:
        logger.info("\n=== SUMMARY ===")
        logger.info(f"Successful strategies: {len(results['successful_strategies'])}")
        logger.info(f"Failed strategies: {len(results['failed_strategies'])}")
        logger.info(f"Files saved: {len(results['saved_files'])}")
        
        if results['successful_strategies']:
            logger.info("\nSuccessful strategies:")
            for strategy in results['successful_strategies']:
                logger.info(f"  - {strategy['strategy']}")
        
        if results['failed_strategies']:
            logger.info(f"\nFailed strategies: {', '.join(results['failed_strategies'])}")
        
        # Save results to JSON if requested
        if args.save_results:
            results_file = f"{args.output_dir}/test_results.json"
            try:
                with open(results_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                logger.info(f"Results saved to {results_file}")
            except Exception as e:
                logger.error(f"Failed to save results: {e}")
    
    logger.info("Testing completed.")


if __name__ == "__main__":
    main()
