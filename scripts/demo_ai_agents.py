#!/usr/bin/env python3
"""
AI Agents Demo Script
Demonstrates the integrated AI-powered property analysis system
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_ai_agents():
    """Test AI agents integration"""
    try:
        from ai_agents import AIAgentManager, AnalysisRequest
        from ai_agents.models import AIProvider
        
        print("🤖 RealtyScanner AI Agents Integration Demo")
        print("=" * 60)
        
        # Initialize AI manager
        ai_manager = AIAgentManager()
        
        if not ai_manager.enabled_providers:
            print("❌ No AI providers configured!")
            print("Please add API keys to your .env file:")
            print("   OPENAI_API_KEY=your_openai_key")
            print("   GOOGLE_API_KEY=your_google_key")
            print("   ANTHROPIC_API_KEY=your_anthropic_key")
            print("   DEEPSEEK_API_KEY=your_deepseek_key")
            return
        
        print(f"✅ AI Providers enabled: {[p.value for p in ai_manager.enabled_providers]}")
        
        # Test connectivity
        print("\n🔗 Testing provider connectivity...")
        connectivity_results = await ai_manager.test_providers()
        for provider, status in connectivity_results.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {provider.value}: {'Connected' if status else 'Failed'}")
        
        # Demo property analysis
        print("\n📊 Demo Property Analysis:")
        print("-" * 40)
        
        # Sample property text in Hebrew
        sample_property = """
        דירת 3 חדרים מרווחת בלב תל אביב
        
        דירה יפהפייה של 3 חדרים בשכונת דיזנגוף, רחוב שינקין 15.
        הדירה משופצת לחלוטין, 80 מ"ר, קומה 2 מתוך 4.
        מחיר: 2,500,000 שקל
        
        כוללת:
        - מרפסת גדולה עם נוף לעיר
        - חניה באבטחה
        - מעלית
        - מיזוג אוויר בכל החדרים
        - קרוב לתחבורה ציבורית
        
        ליצירת קשר: 050-1234567
        """
        
        # Create analysis request
        request = AnalysisRequest(
            property_id="demo_property_001",
            raw_text=sample_property,
            source_url="https://example.com/property/123",
            source_platform="demo",
            priority=1
        )
        
        # Run analysis with multiple providers
        print(f"🔍 Analyzing property with {len(ai_manager.enabled_providers)} AI providers...")
        analysis = await ai_manager.analyze_property_multi(request)
        
        # Display results
        print(f"\n📋 Analysis Results:")
        print(f"   Property ID: {analysis.property_id}")
        print(f"   Consensus Score: {analysis.consensus_score:.2f}")
        print(f"   Location: {analysis.location or 'N/A'}")
        print(f"   City: {analysis.city or 'N/A'}")
        print(f"   Neighborhood: {analysis.neighborhood or 'N/A'}")
        print(f"   Property Type: {analysis.property_type or 'N/A'}")
        print(f"   Rooms: {analysis.rooms or 'N/A'}")
        print(f"   Size: {analysis.size_sqm or 'N/A'} sqm")
        print(f"   Price: {analysis.price or 'N/A'} {analysis.currency or ''}")
        print(f"   Floor: {analysis.floor or 'N/A'}")
        print(f"   Quality Score: {analysis.quality_score or 'N/A'}/10")
        print(f"   Features: {', '.join(analysis.features) if analysis.features else 'N/A'}")
        print(f"   Amenities: {', '.join(analysis.amenities) if analysis.amenities else 'N/A'}")
        print(f"   Condition: {analysis.condition or 'N/A'}")
        
        # Show individual AI responses
        print(f"\n🤖 Individual AI Responses:")
        for i, response in enumerate(analysis.ai_responses):
            print(f"   {i+1}. {response.provider.value}:")
            print(f"      Model: {response.model_used}")
            print(f"      Confidence: {response.confidence:.2f}")
            print(f"      Processing Time: {response.processing_time:.2f}s")
            print(f"      Tokens Used: {response.tokens_used}")
            if response.metadata.get('error'):
                print(f"      Error: {response.metadata['error']}")
        
        # Show performance metrics
        print(f"\n📈 Performance Metrics:")
        metrics = ai_manager.get_performance_metrics()
        for provider, performance in metrics.items():
            if performance.total_requests > 0:
                print(f"   {provider.value}:")
                print(f"      Success Rate: {performance.success_rate:.1f}%")
                print(f"      Avg Response Time: {performance.average_response_time:.2f}s")
                print(f"      Avg Confidence: {performance.average_confidence:.2f}")
                print(f"      Total Tokens: {performance.total_tokens_used}")
        
        # Close AI manager
        await ai_manager.close()
        
        print(f"\n🎉 AI Agents demo completed successfully!")
        print(f"💡 Tips:")
        print(f"   - Add more API keys to enable more providers")
        print(f"   - Higher consensus scores indicate better agreement between AI models")
        print(f"   - Use analyze_property_single() for single provider analysis")
        
    except ImportError as e:
        print(f"❌ AI Agents module not available: {e}")
        print("Please ensure all AI packages are installed:")
        print("   pip install openai google-generativeai anthropic httpx")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")

async def test_content_analyzer_with_ai():
    """Test content analyzer with AI integration"""
    try:
        from analysis.content import ContentAnalyzer
        from scrapers.base import ScrapedListing, ListingSource
        
        print("\n🔍 Content Analyzer with AI Integration Demo")
        print("=" * 60)
        
        # Create content analyzer
        analyzer = ContentAnalyzer()
        
        if not analyzer.use_ai_analysis:
            print("❌ AI analysis not available in content analyzer")
            return
        
        # Create sample listing
        sample_listing = ScrapedListing(
            id="test_listing_001",
            title="דירת 3 חדרים מרווחת בתל אביב",
            description="דירה יפהפייה של 3 חדרים בשכונת דיזנגוף, 80 מ\"ר, קומה 2, משופצת, מחיר 2,500,000 שקל",
            price=2500000,
            location="תל אביב, רחוב שינקין 15",
            rooms=3,
            url="https://example.com/property/123",
            source=ListingSource.YAD2,
            raw_data={}
        )
        
        # Define profile criteria
        profile_criteria = {
            'price': {'min_price': 2000000, 'max_price': 3000000},
            'rooms': {'min_rooms': 2, 'max_rooms': 4},
            'location_criteria': {'areas': ['תל אביב', 'דיזנגוף']}
        }
        
        # Run AI-powered analysis
        print("🤖 Running AI-powered content analysis...")
        result = await analyzer.analyze_listing_with_ai(sample_listing, profile_criteria)
        
        # Display results
        print(f"\n📊 Analysis Results:")
        print(f"   Match: {'✅ Yes' if result.is_match else '❌ No'}")
        print(f"   Confidence: {result.confidence.value}")
        print(f"   Score: {result.score:.1f}/100")
        print(f"   Price Match: {'✅' if result.price_match else '❌'}")
        print(f"   Rooms Match: {'✅' if result.rooms_match else '❌'}")
        print(f"   Location Matches: {result.location_matches}")
        print(f"   Keyword Matches: {result.keyword_matches}")
        print(f"   Reasons:")
        for reason in result.reasons:
            print(f"      - {reason}")
        
        print(f"\n✅ Content analyzer AI integration working!")
        
    except Exception as e:
        logger.error(f"Content analyzer demo failed: {e}")
        print(f"❌ Content analyzer demo failed: {e}")

async def main():
    """Main demo function"""
    print("🏠 RealtyScanner AI Integration Demo")
    print("=" * 60)
    
    # Test AI agents
    await test_ai_agents()
    
    # Test content analyzer with AI
    await test_content_analyzer_with_ai()

if __name__ == "__main__":
    asyncio.run(main())
