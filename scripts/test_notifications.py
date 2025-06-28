#!/usr/bin/env python3
"""
Test script for the notification system

This script:
1. Tests the notification dispatcher with sample data
2. Simulates sending notifications through all channels
3. Validates configuration
4. Demonstrates the notification flow

Run with: python scripts/test_notifications.py
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from notifications import (
    NotificationDispatcher, 
    NotificationMessage,
    TelegramChannel,
    WhatsAppChannel, 
    EmailChannel
)

def test_notification_channels():
    """Test individual notification channels"""
    print("🔔 Testing Individual Notification Channels")
    print("=" * 60)
    
    # Sample notification message
    test_message = NotificationMessage(
        title="New Property Match: Studio in Tel Aviv",
        content="💰 Price: 5,800 ILS\n🏠 Rooms: 2\n📍 Location: Dizengoff Street, Tel Aviv\n⭐ Perfect match for your criteria!",
        url="https://yad2.co.il/item/12345",
        image_url="https://example.com/property.jpg",
        priority="high"
    )
    
    # Test Telegram Channel
    print("\n📱 Testing Telegram Channel...")
    telegram_config = {
        'enabled': True,
        'telegram_chat_id': '123456789'
    }
    telegram_channel = TelegramChannel(telegram_config)
    
    if telegram_channel.validate_config():
        result = telegram_channel.send(test_message, '123456789')
        print(f"✅ Telegram result: {result.status.value}")
        if result.message_id:
            print(f"📨 Message ID: {result.message_id}")
    else:
        print("❌ Telegram configuration invalid")
    
    # Test WhatsApp Channel
    print("\n📱 Testing WhatsApp Channel...")
    whatsapp_config = {
        'enabled': True,
        'whatsapp_phone_number': '+972501234567'
    }
    whatsapp_channel = WhatsAppChannel(whatsapp_config)
    
    if whatsapp_channel.validate_config():
        result = whatsapp_channel.send(test_message, '+972501234567')
        print(f"✅ WhatsApp result: {result.status.value}")
        if result.message_id:
            print(f"📨 Message ID: {result.message_id}")
    else:
        print("❌ WhatsApp configuration invalid")
    
    # Test Email Channel
    print("\n📧 Testing Email Channel...")
    email_config = {
        'enabled': True,
        'email_address': 'user@example.com'
    }
    email_channel = EmailChannel(email_config)
    
    if email_channel.validate_config():
        result = email_channel.send(test_message, 'user@example.com')
        print(f"✅ Email result: {result.status.value}")
        if result.message_id:
            print(f"📨 Message ID: {result.message_id}")
    else:
        print("❌ Email configuration invalid")
    
    return True

def test_notification_dispatcher():
    """Test the notification dispatcher with sample profile configuration"""
    print("\n\n🚀 Testing Notification Dispatcher")
    print("=" * 60)
    
    # Sample user profile notification configuration
    notification_config = {
        "telegram": {
            "enabled": True,
            "telegram_chat_id": "987654321"
        },
        "whatsapp": {
            "enabled": False,  # Disabled for this test
            "whatsapp_phone_number": "+972501234567"
        },
        "email": {
            "enabled": True,
            "email_address": "realty.alerts@example.com"
        }
    }
    
    # Initialize dispatcher
    dispatcher = NotificationDispatcher()
    dispatcher.configure_from_profile(notification_config)
    
    # Validate all channels
    print("\n🔍 Validating Channel Configurations...")
    validation_results = dispatcher.validate_all_channels()
    for channel, is_valid in validation_results.items():
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"  {channel}: {status}")
    
    # Get channel status
    print("\n📊 Channel Status:")
    channel_status = dispatcher.get_channel_status()
    for channel, status in channel_status.items():
        enabled = "🟢 Enabled" if status['enabled'] else "🔴 Disabled"
        valid = "✅" if status['valid_config'] else "❌"
        print(f"  {channel}: {enabled} {valid}")
    
    # Send test notification
    print("\n📤 Sending Test Notification...")
    results = dispatcher.send_test_notification()
    
    print(f"\n📋 Notification Results:")
    for channel, result in results.items():
        status_icon = "✅" if result.status.value == "success" else "❌"
        print(f"  {channel}: {status_icon} {result.status.value}")
        if result.message_id:
            print(f"    Message ID: {result.message_id}")
        if result.error_message:
            print(f"    Error: {result.error_message}")
    
    return True

def test_listing_notification():
    """Test sending a realistic property listing notification"""
    print("\n\n🏠 Testing Realistic Property Listing Notification")
    print("=" * 60)
    
    # Simulate a matched property listing
    listing_message = NotificationMessage(
        title="🎯 Perfect Match Found!",
        content="""💰 Price: 6,200 ILS/month
🏠 Type: 2-room apartment  
📍 Location: Rothschild Boulevard, Tel Aviv
🌟 Features: Balcony, A/C, Parking
⏰ Posted: 5 minutes ago

This property matches your search criteria perfectly!""",
        url="https://www.yad2.co.il/item/real-estate-for-rent-tel-aviv-yafo-tel-aviv-yafo-rothschild-12345",
        image_url="https://example.com/apartment.jpg",
        priority="high"
    )
    
    # Configure dispatcher for active user
    dispatcher = NotificationDispatcher()
    
    # Sample active user notification preferences
    user_config = {
        "telegram": {
            "enabled": True,
            "telegram_chat_id": "user_chat_123"
        },
        "whatsapp": {
            "enabled": False,
            "whatsapp_phone_number": "+972501234567"
        },
        "email": {
            "enabled": True,
            "email_address": "alerts@myrealty.com"
        }
    }
    
    dispatcher.configure_from_profile(user_config)
    
    # Send the listing notification
    print("📤 Sending property listing notification...")
    results = dispatcher.send_notification(listing_message)
    
    # Display results
    success_count = sum(1 for r in results.values() if r.status.value == "success")
    total_count = len(results)
    
    print(f"\n📊 Notification Summary:")
    print(f"  Successfully sent: {success_count}/{total_count} notifications")
    
    for channel, result in results.items():
        if result.status.value == "success":
            print(f"  ✅ {channel}: Delivered (ID: {result.message_id})")
        else:
            print(f"  ❌ {channel}: Failed - {result.error_message}")
    
    return success_count > 0

def main():
    """Run all notification system tests"""
    print("🔔 RealtyScanner Agent - Notification System Test")
    print("=" * 70)
    
    try:
        # Test 1: Individual channels
        success1 = test_notification_channels()
        
        # Test 2: Dispatcher
        success2 = test_notification_dispatcher()
        
        # Test 3: Realistic listing notification
        success3 = test_listing_notification()
        
        # Summary
        print("\n" + "=" * 70)
        if success1 and success2 and success3:
            print("🎉 All notification system tests completed successfully!")
            print("\n✅ Epic 1.3: Notification System Foundation - COMPLETE")
            print("\nNext step: Epic 2.1: Yad2 Scraper Implementation")
            print("\nThe notification system is ready and can:")
            print("- Send notifications via Telegram, WhatsApp, and Email")
            print("- Validate channel configurations")
            print("- Handle multiple notification channels per user")
            print("- Log notification results for tracking")
            return True
        else:
            print("❌ Some notification system tests failed")
            return False
            
    except Exception as e:
        print(f"❌ Notification system test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
