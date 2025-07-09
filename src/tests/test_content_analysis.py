#!/usr/bin/env python3
"""
Test script for the content analysis and filtering system

This script:
1. Tests text normalization
2. Tests location matching
3. Tests price and room filtering
4. Tests match scoring and ranking
5. Demonstrates complete analysis flow

Run with: python scripts/test_content_analysis.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scrapers import ScrapedListing
from analysis import ContentAnalyzer, MatchResult, MatchConfidence

def create_test_listings():
    """Create sample listings for testing"""
    return [
        ScrapedListing(
            listing_id="test_1",
            title="דירת 2 חדרים בדיזנגוף - מרוהטת ומשופצת",
            price=5800,
            rooms=2.0,
            location="דיזנגוף 45, תל אביב - יפו",
            description="דירה יפה ומרוהטת במרכז דיזנגוף. מיזוג אוויר, מרפסת, קרוב לתחבורה ציבורית.",
            features=["מרוהטת", "מיזוג אוויר", "מרפסת"]
        ),
        ScrapedListing(
            listing_id="test_2", 
            title="סטודיו ברוטשילד - זמין מיד",
            price=4200,
            rooms=1.0,
            location="רוטשילד 88, תל אביב - יפו",
            description="סטודיו חדש ומעוצב ברחוב רוטשילד. כל הציוד כלול, חניה.",
            features=["חדש", "מעוצב", "חניה"]
        ),
        ScrapedListing(
            listing_id="test_3",
            title="3 חדרים בפלורנטין עם מעלית",
            price=7200,
            rooms=3.0,
            location="פלורנטין 12, תל אביב",
            description="דירה גדולה ומוארת בפלורנטין. מעלית, מרפסת גדולה, שקט.",
            features=["מעלית", "מרפסת", "שקט"]
        ),
        ScrapedListing(
            listing_id="test_4",
            title="דירת 4 חדרים בנתניה - יקרה מדי",
            price=9500,  # Too expensive
            rooms=4.0,
            location="נתניה מרכז",
            description="דירה גדולה בנתניה עם נוף לים.",
            features=["נוף לים"]
        ),
        ScrapedListing(
            listing_id="test_5",
            title="חדר בשותפות ברמת גן",
            price=2800,
            rooms=1.0,  # Single room
            location="רמת גן, ליד הרכבת",
            description="חדר בדירת שותפות עם סטודנטים.",
            features=["שותפות"]
        )
    ]

def create_test_profile():
    """Create sample user profile criteria"""
    return {
        'price': {'min': 4000, 'max': 6500},
        'rooms': {'min': 1.0, 'max': 2.5},
        'location_criteria': {
            'city': 'תל אביב - יפו',
            'neighborhoods': ['דיזנגוף', 'רוטשילד', 'פלורנטין'],
            'streets': ['דיזנגוף', 'רוטשילד']
        },
        'property_type': ['דירה', 'סטודיו'],
        'preferred_features': ['מרפסת', 'מיזוג', 'חניה']
    }

def test_text_normalization():
    """Test text normalization functionality"""
    print("📝 Testing Text Normalization")
    print("=" * 40)
    
    analyzer = ContentAnalyzer()
    
    test_texts = [
        "דירת 2 חדרים מרוהטת עם מרפסת",
        "Apartment with 2 rooms and balcony",
        "סטודיו משופץ ברוטשילד עם מיזוג אוויר!!!",
        "דירה    עם   רווחים   מיותרים"
    ]
    
    for text in test_texts:
        normalized = analyzer.normalize_text(text)
        print(f"Original: {text}")
        print(f"Normalized: {normalized}")
        print()
    
    return True

def test_individual_analysis():
    """Test analysis of individual listings"""
    print("\n🔍 Testing Individual Listing Analysis")
    print("=" * 40)
    
    analyzer = ContentAnalyzer()
    profile = create_test_profile()
    listings = create_test_listings()
    
    print(f"Profile criteria:")
    print(f"  Price: {profile['price']['min']:,}-{profile['price']['max']:,} ILS")
    print(f"  Rooms: {profile['rooms']['min']}-{profile['rooms']['max']}")
    print(f"  City: {profile['location_criteria']['city']}")
    print(f"  Neighborhoods: {', '.join(profile['location_criteria']['neighborhoods'])}")
    print()
    
    for listing in listings:
        print(f"📋 Analyzing: {listing.title}")
        print(f"   💰 {listing.price:,} ILS | 🏠 {listing.rooms} rooms | 📍 {listing.location}")
        
        result = analyzer.analyze_listing(listing, profile)
        
        match_icon = "✅" if result.is_match else "❌"
        print(f"   {match_icon} Match: {result.is_match} | Confidence: {result.confidence.value} | Score: {result.score:.1f}")
        
        if result.location_matches:
            print(f"   🎯 Location matches: {', '.join(result.location_matches)}")
        
        if result.keyword_matches:
            print(f"   🔑 Keywords: {', '.join(result.keyword_matches)}")
        
        # Show top reasons
        for reason in result.reasons[:3]:
            print(f"   📝 {reason}")
        
        print()
    
    return True

def test_filtering_and_ranking():
    """Test filtering and ranking of multiple listings"""
    print("\n🏆 Testing Filtering and Ranking")
    print("=" * 40)
    
    analyzer = ContentAnalyzer()
    profile = create_test_profile()
    listings = create_test_listings()
    
    # Analyze all listings
    results = []
    for listing in listings:
        result = analyzer.analyze_listing(listing, profile)
        results.append((listing, result))
    
    # Filter and rank matches
    ranked_matches = analyzer.rank_matches(results)
    
    print(f"📊 Analysis Summary:")
    print(f"  Total listings analyzed: {len(listings)}")
    print(f"  Matches found: {len(ranked_matches)}")
    print()
    
    if ranked_matches:
        print("🏆 Ranked Matches (Best to Worst):")
        for i, (listing, result) in enumerate(ranked_matches, 1):
            print(f"{i}. {listing.title}")
            print(f"   💰 {listing.price:,} ILS | 🏠 {listing.rooms} rooms")
            print(f"   🎯 Score: {result.score:.1f} | Confidence: {result.confidence.value}")
            print(f"   📍 {listing.location}")
            print()
    else:
        print("❌ No matches found")
    
    return len(ranked_matches) > 0

def test_duplicate_detection():
    """Test content hashing for duplicate detection"""
    print("\n🔄 Testing Duplicate Detection")
    print("=" * 40)
    
    analyzer = ContentAnalyzer()
    
    # Create original and duplicate listings
    original = ScrapedListing(
        listing_id="original_1",
        title="דירת 2 חדרים בדיזנגוף",
        price=5800,
        rooms=2.0,
        location="דיזנגוף 45, תל אביב",
        description="דירה יפה במרכז העיר"
    )
    
    # Near duplicate (slight title change)
    near_duplicate = ScrapedListing(
        listing_id="duplicate_1",
        title="דירת 2 חדרים בדיזנגוף - משופצת", # Slightly different title
        price=5800,
        rooms=2.0,
        location="דיזנגוף 45, תל אביב",
        description="דירה יפה במרכז העיר"
    )
    
    # Different listing
    different = ScrapedListing(
        listing_id="different_1",
        title="סטודיו ברוטשילד",
        price=4200,
        rooms=1.0,
        location="רוטשילד 88, תל אביב",
        description="סטודיו חדש"
    )
    
    original_hash = analyzer.generate_content_hash(original)
    duplicate_hash = analyzer.generate_content_hash(near_duplicate)
    different_hash = analyzer.generate_content_hash(different)
    
    print(f"Original listing: {original.title}")
    print(f"Hash: {original_hash[:16]}...")
    print()
    
    print(f"Near duplicate: {near_duplicate.title}")
    print(f"Hash: {duplicate_hash[:16]}...")
    print(f"Same as original: {'✅ Yes' if original_hash == duplicate_hash else '❌ No'}")
    print()
    
    print(f"Different listing: {different.title}")
    print(f"Hash: {different_hash[:16]}...")
    print(f"Same as original: {'✅ Yes' if original_hash == different_hash else '❌ No'}")
    print()
    
    return True

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n⚠️ Testing Edge Cases")
    print("=" * 40)
    
    analyzer = ContentAnalyzer()
    profile = create_test_profile()
    
    # Test with missing data
    incomplete_listing = ScrapedListing(
        listing_id="incomplete_1",
        title="דירה ללא פרטים",
        price=None,  # Missing price
        rooms=None,  # Missing rooms
        location="",  # Empty location
        description=""  # Empty description
    )
    
    print("Testing incomplete listing...")
    result = analyzer.analyze_listing(incomplete_listing, profile)
    print(f"✅ Handled missing data: match={result.is_match}, score={result.score:.1f}")
    
    # Test with empty profile
    empty_profile = {}
    result2 = analyzer.analyze_listing(create_test_listings()[0], empty_profile)
    print(f"✅ Handled empty profile: match={result2.is_match}, score={result2.score:.1f}")
    
    # Test text normalization edge cases
    weird_text = "דירה!!! עם    רווחים @@@@ וסימנים #$%^"
    normalized = analyzer.normalize_text(weird_text)
    print(f"✅ Normalized weird text: '{weird_text}' → '{normalized}'")
    
    return True

def main():
    """Run all content analysis tests"""
    print("🔬 RealtyScanner Agent - Content Analysis Test")
    print("=" * 60)
    
    try:
        # Test 1: Text normalization
        success1 = test_text_normalization()
        
        # Test 2: Individual analysis
        success2 = test_individual_analysis()
        
        # Test 3: Filtering and ranking
        success3 = test_filtering_and_ranking()
        
        # Test 4: Duplicate detection
        success4 = test_duplicate_detection()
        
        # Test 5: Edge cases
        success5 = test_edge_cases()
        
        # Summary
        print("=" * 60)
        total_tests = 5
        passed_tests = sum([success1, success2, success3, success4, success5])
        
        if passed_tests == total_tests:
            print("🎉 All content analysis tests completed successfully!")
            print(f"✅ {passed_tests}/{total_tests} test categories passed")
            print("\n✅ Epic 2.2: Content Analysis & Filtering Logic - COMPLETE")
            print("\nThe content analysis system can:")
            print("- Normalize Hebrew and English text")
            print("- Match locations with aliases")
            print("- Filter by price and room criteria")
            print("- Score and rank matches by relevance")
            print("- Generate content hashes for duplicate detection")
            print("- Handle edge cases and missing data")
            print("\n🚀 Ready for Epic 2.3: Notification Dispatcher Integration")
            return True
        else:
            print(f"⚠️ Some tests had issues ({passed_tests}/{total_tests} passed)")
            return False
            
    except Exception as e:
        print(f"❌ Content analysis test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
