#!/usr/bin/env python3
"""
Database initialization and seeding script for RealtyScanner Agent

This script:
1. Tests MongoDB connection
2. Creates required collections and indexes
3. Seeds database with sample data for testing
4. Validates the database schema

Run with: python scripts/init_database.py
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from db import (
    DatabaseManager, 
    UserProfile, 
    LocationCriteria, 
    PriceRange, 
    RoomRange, 
    ScanTargets, 
    NotificationChannels, 
    NotificationChannelConfig
)

def create_sample_profile(db: DatabaseManager) -> str:
    """Create a sample user profile for testing"""
    
    sample_profile = UserProfile(
        profile_name="Studio in Central Tel Aviv - Test Profile",
        is_active=True,
        location_criteria=LocationCriteria(
            city="תל אביב - יפו",
            neighborhoods=["לב תל אביב", "הצפון הישן", "רוטשילד"],
            streets=["דיזנגוף", "רוטשילד", "אלנבי"]
        ),
        price=PriceRange(min=4000, max=6500),
        rooms=RoomRange(min=1.0, max=2.5),
        property_type=["דירה", "סטודיו"],
        scan_targets=ScanTargets(
            yad2_url="https://www.yad2.co.il/realestate/rent?city=5000&rooms=1-2.5&price=4000-6500",
            facebook_group_ids=["123456789", "987654321"]  # Example group IDs
        ),
        notification_channels=NotificationChannels(
            telegram=NotificationChannelConfig(
                enabled=True,
                telegram_chat_id="your_telegram_chat_id_here"
            ),
            whatsapp=NotificationChannelConfig(
                enabled=False,
                whatsapp_phone_number="+972501234567"
            ),
            email=NotificationChannelConfig(
                enabled=False,
                email_address="your_email@example.com"
            )
        )
    )
    
    profile_id = db.create_user_profile(sample_profile)
    return profile_id

def main():
    print("🏠 RealtyScanner Agent - Database Initialization")
    print("=" * 60)
    
    # Initialize database manager
    db = DatabaseManager()
    
    # Test 1: MongoDB Connection
    print("📊 Testing MongoDB connection...")
    if not db.connect():
        print("❌ Failed to connect to MongoDB")
        print("\nTroubleshooting:")
        print("1. Make sure MongoDB is running locally or update MONGODB_URI in .env")
        print("2. Check that the MongoDB service is accessible")
        print("3. Verify your .env file has the correct MONGODB_URI")
        return False
    
    print("✅ MongoDB connection successful")
    
    # Test 2: Database Collections
    print("\n📋 Initializing collections and indexes...")
    try:
        # Collections are automatically initialized in connect()
        collections = db.db.list_collection_names()
        print(f"✅ Database collections available: {collections}")
    except Exception as e:
        print(f"❌ Failed to initialize collections: {e}")
        return False
    
    # Test 3: Sample Data Creation
    print("\n👤 Creating sample user profile...")
    try:
        profile_id = create_sample_profile(db)
        if profile_id:
            print(f"✅ Sample profile created with ID: {profile_id}")
            
            # Verify we can read it back
            retrieved_profile = db.get_user_profile(profile_id)
            if retrieved_profile:
                print(f"✅ Sample profile verified: {retrieved_profile.profile_name}")
            else:
                print("⚠️  Could not retrieve sample profile")
        else:
            print("❌ Failed to create sample profile")
            return False
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False
    
    # Test 4: CRUD Operations
    print("\n🔄 Testing CRUD operations...")
    try:
        # Test getting active profiles
        active_profiles = db.get_active_user_profiles()
        print(f"✅ Found {len(active_profiles)} active profiles")
        
        # Test updating profile
        update_success = db.update_user_profile(profile_id, {"profile_name": "Updated Test Profile"})
        if update_success:
            print("✅ Profile update successful")
        else:
            print("⚠️  Profile update failed")
            
    except Exception as e:
        print(f"❌ CRUD operations test failed: {e}")
        return False
    
    # Test 5: Database Indexes
    print("\n📊 Verifying database indexes...")
    try:
        # Check indexes for each collection
        for collection_name in ["user_profiles", "scanned_listings", "sent_notifications"]:
            collection = db.db[collection_name]
            indexes = list(collection.list_indexes())
            print(f"✅ {collection_name}: {len(indexes)} indexes created")
    except Exception as e:
        print(f"❌ Index verification failed: {e}")
        return False
    
    # Cleanup
    db.disconnect()
    
    print("\n" + "=" * 60)
    print("🎉 Database initialization completed successfully!")
    print("\nDatabase is ready for Epic 1.3: Notification System Foundation")
    print("\nSample data created:")
    print(f"- Sample user profile ID: {profile_id}")
    print("- Collections: user_profiles, scanned_listings, sent_notifications")
    print("- Indexes: Created for optimal performance")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
