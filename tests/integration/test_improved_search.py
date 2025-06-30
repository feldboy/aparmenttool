#!/usr/bin/env python3
"""
Test script for improved apartment search functionality
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

async def test_search():
    """Test the improved search functionality"""
    try:
        from search.tavily import get_tavily_searcher
        
        print("🔍 Testing improved apartment search...")
        
        # Initialize searcher
        tavily = get_tavily_searcher()
        
        # Test search for today's listings
        print("\n📅 Testing search for TODAY's listings only...")
        search_query = "3 rooms Tel Aviv under 8000 NIS"
        
        results = await tavily.search_real_estate(
            query=search_query,
            location="tel aviv",
            max_results=5,
            today_only=True
        )
        
        print(f"✅ Found {len(results)} today-only results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title'][:80]}...")
            print(f"     Score: {result['score']:.2f}")
            print(f"     URL: {result['url'][:60]}...")
            print()
        
        # Test search for all listings
        print("\n📅 Testing search for ALL listings...")
        
        all_results = await tavily.search_real_estate(
            query=search_query,
            location="tel aviv",
            max_results=5,
            today_only=False
        )
        
        print(f"✅ Found {len(all_results)} total results:")
        for i, result in enumerate(all_results, 1):
            print(f"  {i}. {result['title'][:80]}...")
            print(f"     Score: {result['score']:.2f}")
            print(f"     URL: {result['url'][:60]}...")
            print()
        
        print("\n🎯 Search test completed!")
        print(f"Today-only results: {len(results)}")
        print(f"All results: {len(all_results)}")
        
        if len(results) < len(all_results):
            print("✅ Today-only filtering is working correctly!")
        else:
            print("⚠️  Today-only filtering may need adjustment")
            
    except Exception as e:
        print(f"❌ Error during search test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search())
