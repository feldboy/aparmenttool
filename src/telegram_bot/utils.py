"""
Utility functions for the Telegram bot
"""

import logging
from typing import Dict, Any, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

def format_property_message(property_data: Dict[str, Any]) -> str:
    """
    Format a property listing for Telegram message
    
    Args:
        property_data: Property listing data
        
    Returns:
        Formatted HTML message string
    """
    
    # Extract property details
    title = property_data.get('title', 'Property Listing')
    price = property_data.get('price')
    rooms = property_data.get('rooms')
    location = property_data.get('location', 'Location not specified')
    description = property_data.get('description', '')
    confidence = property_data.get('match_confidence', 'medium')
    score = property_data.get('match_score', 0)
    
    # Choose emoji based on confidence
    if confidence == 'high':
        emoji = '🔥'
        confidence_text = 'HIGH CONFIDENCE'
    elif confidence == 'medium':
        emoji = '⭐'
        confidence_text = 'MEDIUM CONFIDENCE'
    else:
        emoji = '👍'
        confidence_text = 'LOW CONFIDENCE'
    
    # Format price
    price_text = f"{price:,} ILS/month" if price else "Price not specified"
    
    # Format rooms
    rooms_text = f"{rooms} rooms" if rooms else "Rooms not specified"
    
    # Truncate description if too long
    if description and len(description) > 200:
        description = description[:200] + "..."
    
    # Format reasons if available
    reasons_text = ""
    if 'match_reasons' in property_data and property_data['match_reasons']:
        reasons = property_data['match_reasons'][:3]  # Show top 3 reasons
        reasons_text = "\n\n✨ <b>Why this matches:</b>\n" + \
                      "\n".join(f"• {reason}" for reason in reasons)
    
    # Build the message
    message = f"""
{emoji} <b>New Property Match!</b>

🏠 <b>{title}</b>
💰 <b>Price:</b> {price_text}
🛏️ <b>Rooms:</b> {rooms_text}
📍 <b>Location:</b> {location}
🎯 <b>Match Score:</b> {score:.1f}/100 ({confidence_text})

{description}{reasons_text}
""".strip()
    
    return message

def format_notification_summary(notifications: list) -> str:
    """
    Format a summary of recent notifications
    
    Args:
        notifications: List of notification records
        
    Returns:
        Formatted summary message
    """
    if not notifications:
        return "📭 No recent notifications"
    
    total = len(notifications)
    recent = [n for n in notifications if n.get('created_at', 0) > 0]  # Last 24h logic would go here
    
    summary = f"""
📊 <b>Notification Summary</b>

<b>Recent Activity:</b>
• 📤 {len(recent)} notifications in last 24h
• 🏠 {total} total properties tracked
• 🎯 {sum(1 for n in notifications if n.get('confidence') == 'high')} high-confidence matches

<b>Latest Properties:</b>
"""
    
    # Add latest 3 properties
    for i, notification in enumerate(notifications[:3]):
        property_info = notification.get('property', {})
        price = property_info.get('price', 'N/A')
        location = property_info.get('location', 'Unknown')
        summary += f"\n• 🏠 {price} ILS - {location}"
    
    if total > 3:
        summary += f"\n\n... and {total - 3} more properties"
    
    return summary

def create_property_keyboard(property_data: Dict[str, Any]) -> InlineKeyboardMarkup:
    """
    Create inline keyboard for property actions
    
    Args:
        property_data: Property listing data
        
    Returns:
        InlineKeyboardMarkup with action buttons
    """
    listing_id = property_data.get('listing_id', 'unknown')
    url = property_data.get('url')
    
    buttons = []
    
    # View listing button (always present)
    if url:
        buttons.append([InlineKeyboardButton("🔗 View Listing", url=url)])
    
    # Action buttons
    action_row = [
        InlineKeyboardButton("❤️ Save", callback_data=f"property_save_{listing_id}"),
        InlineKeyboardButton("👎 Not Interested", callback_data=f"property_dismiss_{listing_id}")
    ]
    buttons.append(action_row)
    
    # Additional options
    options_row = [
        InlineKeyboardButton("📧 Share", callback_data=f"property_share_{listing_id}"),
        InlineKeyboardButton("📊 Details", callback_data=f"property_details_{listing_id}")
    ]
    buttons.append(options_row)
    
    return InlineKeyboardMarkup(buttons)

def create_profile_keyboard(profile_data: Dict[str, Any]) -> InlineKeyboardMarkup:
    """
    Create inline keyboard for profile management
    
    Args:
        profile_data: User profile data
        
    Returns:
        InlineKeyboardMarkup with profile action buttons
    """
    profile_id = profile_data.get('id', 'unknown')
    is_active = profile_data.get('is_active', True)
    
    buttons = []
    
    # Status toggle
    status_text = "⏸️ Pause" if is_active else "▶️ Activate"
    status_action = f"profile_pause_{profile_id}" if is_active else f"profile_activate_{profile_id}"
    buttons.append([InlineKeyboardButton(status_text, callback_data=status_action)])
    
    # Edit options
    edit_row = [
        InlineKeyboardButton("✏️ Edit", callback_data=f"profile_edit_{profile_id}"),
        InlineKeyboardButton("📋 View", callback_data=f"profile_view_{profile_id}")
    ]
    buttons.append(edit_row)
    
    # Advanced options
    advanced_row = [
        InlineKeyboardButton("📊 Statistics", callback_data=f"profile_stats_{profile_id}"),
        InlineKeyboardButton("🗑️ Delete", callback_data=f"profile_delete_{profile_id}")
    ]
    buttons.append(advanced_row)
    
    return InlineKeyboardMarkup(buttons)

def create_settings_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard for settings menu"""
    buttons = [
        [InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications")],
        [InlineKeyboardButton("🎯 Search Preferences", callback_data="settings_search")],
        [InlineKeyboardButton("📱 Contact Methods", callback_data="settings_contact")],
        [InlineKeyboardButton("🔄 Sync Frequency", callback_data="settings_frequency")],
        [InlineKeyboardButton("🏠 Back to Main", callback_data="start")]
    ]
    
    return InlineKeyboardMarkup(buttons)

def create_confirmation_keyboard(action: str, item_id: str) -> InlineKeyboardMarkup:
    """
    Create confirmation keyboard for destructive actions
    
    Args:
        action: The action to confirm (e.g., 'delete', 'disable')
        item_id: ID of the item being acted upon
        
    Returns:
        InlineKeyboardMarkup with confirm/cancel buttons
    """
    buttons = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}_{item_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")
        ]
    ]
    
    return InlineKeyboardMarkup(buttons)

def format_user_profile_display(profile_data: Dict[str, Any]) -> str:
    """
    Format user profile for display
    
    Args:
        profile_data: User profile data
        
    Returns:
        Formatted profile display string
    """
    name = profile_data.get('name', 'Unnamed Profile')
    price_range = profile_data.get('price_range', {})
    rooms_range = profile_data.get('rooms_range', {})
    location = profile_data.get('location', {})
    is_active = profile_data.get('is_active', True)
    created_date = profile_data.get('created_at', 'Unknown')
    
    status_emoji = "✅" if is_active else "⏸️"
    status_text = "Active" if is_active else "Paused"
    
    # Format price range
    if 'min' in price_range and 'max' in price_range:
        price_text = f"{price_range['min']:,} - {price_range['max']:,} ILS"
    elif 'max' in price_range:
        price_text = f"Up to {price_range['max']:,} ILS"
    elif 'min' in price_range:
        price_text = f"From {price_range['min']:,} ILS"
    else:
        price_text = "Not specified"
    
    # Format rooms
    if 'min' in rooms_range and 'max' in rooms_range:
        rooms_text = f"{rooms_range['min']} - {rooms_range['max']} rooms"
    elif 'exact' in rooms_range:
        rooms_text = f"{rooms_range['exact']} rooms"
    else:
        rooms_text = "Not specified"
    
    # Format location
    if 'city' in location and 'neighborhoods' in location:
        location_text = f"{location['city']} ({', '.join(location['neighborhoods'])})"
    elif 'cities' in location:
        location_text = ', '.join(location['cities'])
    elif 'city' in location:
        location_text = location['city']
    else:
        location_text = "Not specified"
    
    profile_display = f"""
🏠 <b>{name}</b> {status_emoji}

<b>Status:</b> {status_text}
<b>Budget:</b> {price_text}
<b>Rooms:</b> {rooms_text}
<b>Location:</b> {location_text}
<b>Created:</b> {created_date}
""".strip()
    
    return profile_display

def escape_html(text: str) -> str:
    """Escape HTML special characters for Telegram HTML parsing"""
    if not text:
        return ""
    
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;'
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text

def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def format_timestamp(timestamp: float, format_type: str = "relative") -> str:
    """
    Format timestamp for display
    
    Args:
        timestamp: Unix timestamp
        format_type: 'relative' for "2 hours ago", 'absolute' for full date
        
    Returns:
        Formatted timestamp string
    """
    from datetime import datetime, timezone
    
    try:
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        
        if format_type == "relative":
            now = datetime.now(timezone.utc)
            diff = now - dt
            
            if diff.days > 0:
                return f"{diff.days} days ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hours ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minutes ago"
            else:
                return "Just now"
        else:
            return dt.strftime("%Y-%m-%d %H:%M")
            
    except (ValueError, OSError):
        return "Unknown time"

def validate_telegram_chat_id(chat_id: str) -> bool:
    """Validate Telegram chat ID format"""
    try:
        # Chat IDs can be negative (for groups) or positive (for users)
        int(chat_id)
        return True
    except ValueError:
        return False

def create_error_message(error_type: str, details: str = "") -> str:
    """Create standardized error message"""
    error_messages = {
        'invalid_input': '❌ Invalid input format',
        'not_found': '❌ Item not found',
        'permission_denied': '❌ Permission denied',
        'system_error': '❌ System error occurred',
        'network_error': '❌ Network connection error'
    }
    
    base_message = error_messages.get(error_type, '❌ Unknown error')
    
    if details:
        return f"{base_message}: {details}"
    else:
        return base_message

def create_success_message(action: str, details: str = "") -> str:
    """Create standardized success message"""
    success_messages = {
        'created': '✅ Successfully created',
        'updated': '✅ Successfully updated',
        'deleted': '✅ Successfully deleted',
        'saved': '✅ Successfully saved',
        'sent': '✅ Successfully sent'
    }
    
    base_message = success_messages.get(action, '✅ Success')
    
    if details:
        return f"{base_message}: {details}"
    else:
        return base_message
