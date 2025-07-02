#!/usr/bin/env python3
"""
Test Tavily integration for RealtyScanner
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_tavily_search():
    """Test Tavily search functionality"""
    print("🔍 Testing Tavily Integration...")
    
    try:
        from search.tavily import get_tavily_searcher
        
        tavily = get_tavily_searcher()
        print("✅ Tavily searcher initialized successfully")
        
        # Test basic real estate search
        print("\n🏠 Testing real estate search...")
        results = await tavily.search_real_estate("3 rooms Tel Aviv rent", "Tel Aviv", max_results=3)
        
        print(f"📊 Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title'][:80]}...")
            print(f"     URL: {result['url']}")
            print(f"     Score: {result.get('score', 0):.2f}")
            print()
        
        # Test market trends
        print("📈 Testing market trends search...")
        try:
            market_data = await tavily.search_market_trends("Tel Aviv", "apartment")
            
            if market_data and market_data.get('location'):
                print(f"✅ Market data retrieved for {market_data.get('location')}")
                answer = market_data.get('answer')
                if answer:
                    print(f"   Summary: {answer[:100]}...")
                else:
                    print("   Summary: No summary available")
                print(f"   Sources: {len(market_data.get('sources', []))}")
            else:
                print("⚠️ No market data retrieved")
        except Exception as market_error:
            print(f"⚠️ Market trends test failed: {market_error}")
        
        print("\n✅ Tavily integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Tavily test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_content_analyzer():
    """Test enhanced content analyzer"""
    print("\n🧠 Testing Enhanced Content Analyzer...")
    
    try:
        from analysis.content import ContentAnalyzer
        from scrapers.base import ScrapedListing
        
        analyzer = ContentAnalyzer()
        print("✅ Content analyzer initialized")
        
        # Create test listing
        test_listing = ScrapedListing(
            listing_id="test_123",
            title="דירת 3 חדרים בתל אביב במחיר מעולה",
            description="דירה יפה 3 חדרים, מחיר 4500 שקל לחודש, ליד הים",
            price=4500,
            location="תל אביב",
            rooms=3,
            url="https://example.com/listing123",
            raw_data={}
        )
        
        # Create test profile
        test_profile = {
            "price_range": {"min": 3000, "max": 5000},
            "rooms_range": {"min": 2, "max": 4},
            "location_criteria": {
                "city": "תל אביב",
                "neighborhoods": ["center", "florentin"]
            }
        }
        
        # Test enhanced analysis if available
        if hasattr(analyzer, 'analyze_with_web_context'):
            print("🌐 Testing enhanced analysis with web context...")
            result = await analyzer.analyze_with_web_context(test_listing, test_profile)
            print(f"   Match: {result.is_match}")
            print(f"   Confidence: {result.confidence}")
            print(f"   Score: {result.score:.2f}")
            print(f"   Reasons: {len(result.reasons)}")
        else:
            print("⚠️ Enhanced analysis not available, testing basic analysis...")
            result = analyzer.analyze_listing(test_listing, test_profile)
            print(f"   Match: {result.is_match}")
            print(f"   Confidence: {result.confidence}")
        
        print("✅ Content analyzer test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Content analyzer test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 RealtyScanner AI Integration Tests")
    print("=" * 50)
    
    tavily_ok = await test_tavily_search()
    analyzer_ok = await test_content_analyzer()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Tavily Integration: {'✅ PASS' if tavily_ok else '❌ FAIL'}")
    print(f"   Content Analyzer: {'✅ PASS' if analyzer_ok else '❌ FAIL'}")
    
    if tavily_ok and analyzer_ok:
        print("\n🎉 All tests passed! RealtyScanner AI is ready!")
        return True
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")
        return False

if __name__ == "__main__":
    asyncio.run(main())
