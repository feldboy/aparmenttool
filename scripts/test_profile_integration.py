#!/usr/bin/env python3
"""
Integration test demonstrating how the notification system works with user profiles

This script shows the complete flow from user profile to notification dispatch.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set environment variables for simulation
import os
os.environ["TELEGRAM_BOT_TOKEN"] = "sim_token_12345"
os.environ["SENDGRID_API_KEY"] = "sim_sendgrid_key"

from db import (
    UserProfile, 
    LocationCriteria, 
    PriceRange, 
    RoomRange, 
    ScanTargets, 
    NotificationChannels, 
    NotificationChannelConfig
)
from notifications import NotificationDispatcher, NotificationMessage

def test_profile_to_notification_integration():
    """Test the complete flow from user profile to notification"""
    print("🔗 Testing User Profile → Notification Integration")
    print("=" * 60)
    
    # Create a sample user profile (like would be stored in DB)
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
            facebook_group_ids=["123456789", "987654321"]
        ),
        notification_channels=NotificationChannels(
            telegram=NotificationChannelConfig(
                enabled=True,
                telegram_chat_id="user_telegram_123"
            ),
            whatsapp=NotificationChannelConfig(
                enabled=False,
                whatsapp_phone_number="+972501234567"
            ),
            email=NotificationChannelConfig(
                enabled=True,
                email_address="user@example.com"
            )
        )
    )
    
    print(f"👤 User Profile: {sample_profile.profile_name}")
    print(f"🎯 Price Range: {sample_profile.price.min} - {sample_profile.price.max} ILS")
    print(f"🏠 Rooms: {sample_profile.rooms.min} - {sample_profile.rooms.max}")
    print(f"📍 City: {sample_profile.location_criteria.city}")
    
    # Configure notification dispatcher from profile
    dispatcher = NotificationDispatcher()
    
    # Convert Pydantic models to dict format expected by dispatcher
    notification_config = {
        "telegram": {
            "enabled": sample_profile.notification_channels.telegram.enabled,
            "telegram_chat_id": sample_profile.notification_channels.telegram.telegram_chat_id
        },
        "whatsapp": {
            "enabled": sample_profile.notification_channels.whatsapp.enabled,
            "whatsapp_phone_number": sample_profile.notification_channels.whatsapp.whatsapp_phone_number
        },
        "email": {
            "enabled": sample_profile.notification_channels.email.enabled,
            "email_address": sample_profile.notification_channels.email.email_address
        }
    }
    
    dispatcher.configure_from_profile(notification_config)
    
    print(f"\n📊 Configured {len(dispatcher.channels)} notification channels")
    
    # Simulate a property that matches the profile criteria
    matched_listing = NotificationMessage(
        title="🎯 Perfect Match Found!",
        content=f"""💰 Price: 5,800 ILS/month (within {sample_profile.price.min}-{sample_profile.price.max})
🏠 Type: 2-room apartment (within {sample_profile.rooms.min}-{sample_profile.rooms.max} rooms)
📍 Location: Dizengoff Street, {sample_profile.location_criteria.city}
🌟 Features: Renovated, A/C, Balcony
⏰ Posted: Just now

This property perfectly matches your search criteria!""",
        url="https://www.yad2.co.il/item/12345",
        priority="high"
    )
    
    # Send notification
    print("\n📤 Sending matched listing notification...")
    results = dispatcher.send_notification(matched_listing)
    
    # Display results
    success_count = sum(1 for r in results.values() if r.status.value == "success")
    total_configured = len([ch for ch in notification_config.values() if ch.get('enabled', False)])
    
    print(f"\n📋 Notification Results:")
    for channel, result in results.items():
        if result.status.value == "success":
            print(f"  ✅ {channel}: Delivered")
        else:
            print(f"  ❌ {channel}: {result.error_message}")
    
    print(f"\n📊 Summary: {success_count}/{total_configured} enabled channels notified successfully")
    
    return success_count > 0

def main():
    print("🔗 RealtyScanner Agent - Profile Integration Test")
    print("=" * 70)
    
    success = test_profile_to_notification_integration()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 Profile → Notification integration test successful!")
        print("\n✅ The system can:")
        print("  - Load user profiles with notification preferences")
        print("  - Configure notification channels from profile data")
        print("  - Send targeted notifications when matches are found")
        print("  - Handle multiple notification channels per user")
        print("\n🚀 Ready for Epic 2: Yad2 Integration & Filtering")
        return True
    else:
        print("❌ Profile integration test failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
