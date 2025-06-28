"""
Command and message handlers for the Telegram bot
"""

import logging
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    chat_id = str(update.effective_chat.id)
    
    welcome_message = f"""
🏠 <b>Welcome to RealtyScanner Agent!</b>

Hi {user.first_name}! I'm your personal real estate assistant. I can help you:

🔍 <b>Find Properties</b> - Get instant notifications for new listings
⚙️ <b>Manage Profiles</b> - Configure your search preferences  
📊 <b>Track Notifications</b> - View your notification history
🛠️ <b>Settings</b> - Customize your experience

<i>Get started by setting up your search profile!</i>
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔧 Setup Profile", callback_data="setup_profile")],
        [InlineKeyboardButton("📋 View Profiles", callback_data="view_profiles")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ])
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    # Store user info for future use
    from .bot import get_bot
    bot = get_bot()
    bot.update_user_session(chat_id, {
        'user_info': {
            'id': user.id,
            'first_name': user.first_name,
            'username': user.username,
            'chat_id': chat_id
        }
    })

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🏠 <b>RealtyScanner Bot Commands</b>

<b>Main Commands:</b>
/start - Start the bot and see main menu
/profile - Manage your search profiles
/settings - Configure notification preferences
/notifications - View recent notifications
/help - Show this help message

<b>Features:</b>
• 🎯 Smart property matching based on your criteria
• 📱 Instant notifications from Yad2 and Facebook
• 🔄 Real-time updates every 5 minutes
• 📊 Detailed notification history
• ⚙️ Customizable search preferences

<b>Getting Started:</b>
1. Use /profile to create your search criteria
2. Set your preferred neighborhoods and price range
3. Configure notification settings
4. Sit back and receive instant property alerts!

Need help? Contact support or check our documentation.
"""
    
    await update.message.reply_text(help_text, parse_mode='HTML')

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /profile command"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Create New Profile", callback_data="create_profile")],
        [InlineKeyboardButton("📋 View All Profiles", callback_data="view_profiles")],
        [InlineKeyboardButton("✏️ Edit Profile", callback_data="edit_profile")],
        [InlineKeyboardButton("🗑️ Delete Profile", callback_data="delete_profile")]
    ])
    
    await update.message.reply_text(
        "🏠 <b>Profile Management</b>\n\nChoose an action:",
        reply_markup=keyboard,
        parse_mode='HTML'
    )

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Notification Settings", callback_data="notification_settings")],
        [InlineKeyboardButton("🎯 Search Preferences", callback_data="search_preferences")],
        [InlineKeyboardButton("📱 Contact Preferences", callback_data="contact_preferences")],
        [InlineKeyboardButton("🔄 Sync Frequency", callback_data="sync_frequency")]
    ])
    
    await update.message.reply_text(
        "⚙️ <b>Settings</b>\n\nConfigure your preferences:",
        reply_markup=keyboard,
        parse_mode='HTML'
    )

async def notifications_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /notifications command"""
    chat_id = str(update.effective_chat.id)
    
    # TODO: Integrate with database to fetch real notification history
    # For now, show a placeholder
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 View All History", callback_data="view_all_notifications")],
        [InlineKeyboardButton("🎯 Recent Matches", callback_data="recent_matches")],
        [InlineKeyboardButton("📈 Statistics", callback_data="notification_stats")]
    ])
    
    notification_summary = """
📊 <b>Notification Summary</b>

<b>Last 24 Hours:</b>
• 🏠 3 new properties found
• 📤 5 notifications sent
• 🎯 2 high-confidence matches

<b>This Week:</b>
• 🏠 12 new properties scanned
• 📤 18 notifications sent
• ⭐ 8 medium-confidence matches

<b>Quick Actions:</b>
"""
    
    await update.message.reply_text(
        notification_summary,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    chat_id = str(update.effective_chat.id)
    
    from .bot import get_bot
    bot = get_bot()
    session = bot.get_user_session(chat_id)
    
    if data == "setup_profile":
        await handle_setup_profile(update, context)
    elif data == "view_profiles":
        await handle_view_profiles(update, context)
    elif data == "create_profile":
        await handle_create_profile(update, context)
    elif data == "edit_profile":
        await handle_edit_profile(update, context)
    elif data == "delete_profile":
        await handle_delete_profile(update, context)
    elif data == "notification_settings":
        await handle_notification_settings(update, context)
    elif data == "search_preferences":
        await handle_search_preferences(update, context)
    elif data == "help":
        await help_command(update, context)
    elif data.startswith("property_"):
        await handle_property_action(update, context, data)
    else:
        await query.edit_message_text("⚠️ Unknown action. Please try again.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages (for profile setup flows)"""
    chat_id = str(update.effective_chat.id)
    text = update.message.text
    
    from .bot import get_bot
    bot = get_bot()
    session = bot.get_user_session(chat_id)
    
    state = session.get('state', 'idle')
    
    if state == 'waiting_profile_name':
        await handle_profile_name_input(update, context, text)
    elif state == 'waiting_price_range':
        await handle_price_range_input(update, context, text)
    elif state == 'waiting_rooms':
        await handle_rooms_input(update, context, text)
    elif state == 'waiting_location':
        await handle_location_input(update, context, text)
    else:
        # Default response for unhandled messages
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
        ])
        
        await update.message.reply_text(
            "I'm not sure what you mean. Use the buttons below or try /help for available commands.",
            reply_markup=keyboard
        )

# Profile setup handlers

async def handle_setup_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start profile setup flow"""
    query = update.callback_query
    chat_id = str(update.effective_chat.id)
    
    from .bot import get_bot
    bot = get_bot()
    bot.update_user_session(chat_id, {
        'state': 'waiting_profile_name',
        'profile_data': {}
    })
    
    await query.edit_message_text(
        "🏠 <b>Create New Search Profile</b>\n\n"
        "Let's set up your property search preferences step by step.\n\n"
        "📝 <b>Step 1:</b> What would you like to name this profile?\n"
        "<i>Example: 'Tel Aviv Apartment' or 'Family Home'</i>",
        parse_mode='HTML'
    )

async def handle_profile_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE, profile_name: str):
    """Handle profile name input"""
    chat_id = str(update.effective_chat.id)
    
    from .bot import get_bot
    bot = get_bot()
    session = bot.get_user_session(chat_id)
    session['profile_data']['name'] = profile_name
    session['state'] = 'waiting_price_range'
    
    await update.message.reply_text(
        f"✅ Profile name: <b>{profile_name}</b>\n\n"
        "💰 <b>Step 2:</b> What's your budget range?\n"
        "Please enter your price range in ILS.\n\n"
        "<i>Examples:</i>\n"
        "• <code>3000-5000</code> (range)\n"
        "• <code>max 4000</code> (maximum only)\n"
        "• <code>min 2500</code> (minimum only)",
        parse_mode='HTML'
    )

async def handle_price_range_input(update: Update, context: ContextTypes.DEFAULT_TYPE, price_text: str):
    """Handle price range input"""
    chat_id = str(update.effective_chat.id)
    
    try:
        # Parse price range
        price_range = parse_price_range(price_text)
        
        from .bot import get_bot
        bot = get_bot()
        session = bot.get_user_session(chat_id)
        session['profile_data']['price_range'] = price_range
        session['state'] = 'waiting_rooms'
        
        price_display = format_price_range(price_range)
        
        await update.message.reply_text(
            f"✅ Budget: <b>{price_display}</b>\n\n"
            "🏠 <b>Step 3:</b> How many rooms do you need?\n"
            "Please specify the room count.\n\n"
            "<i>Examples:</i>\n"
            "• <code>2-3</code> (2 to 3 rooms)\n"
            "• <code>min 2</code> (at least 2 rooms)\n"
            "• <code>max 4</code> (up to 4 rooms)\n"
            "• <code>2.5</code> (exactly 2.5 rooms)",
            parse_mode='HTML'
        )
    except ValueError as e:
        await update.message.reply_text(
            f"❌ Invalid price format: {e}\n\n"
            "Please try again with a valid format:\n"
            "• <code>3000-5000</code>\n"
            "• <code>max 4000</code>\n"
            "• <code>min 2500</code>",
            parse_mode='HTML'
        )

async def handle_rooms_input(update: Update, context: ContextTypes.DEFAULT_TYPE, rooms_text: str):
    """Handle rooms input"""
    chat_id = str(update.effective_chat.id)
    
    try:
        # Parse room range
        rooms_range = parse_rooms_range(rooms_text)
        
        from .bot import get_bot
        bot = get_bot()
        session = bot.get_user_session(chat_id)
        session['profile_data']['rooms_range'] = rooms_range
        session['state'] = 'waiting_location'
        
        rooms_display = format_rooms_range(rooms_range)
        
        await update.message.reply_text(
            f"✅ Rooms: <b>{rooms_display}</b>\n\n"
            "📍 <b>Step 4:</b> Where are you looking?\n"
            "Please specify your preferred locations.\n\n"
            "<i>Examples:</i>\n"
            "• <code>Tel Aviv</code>\n"
            "• <code>Jerusalem, Haifa</code>\n"
            "• <code>Tel Aviv: Florentin, Dizengoff</code> (city with neighborhoods)",
            parse_mode='HTML'
        )
    except ValueError as e:
        await update.message.reply_text(
            f"❌ Invalid room format: {e}\n\n"
            "Please try again with a valid format:\n"
            "• <code>2-3</code>\n"
            "• <code>min 2</code>\n"
            "• <code>2.5</code>",
            parse_mode='HTML'
        )

async def handle_location_input(update: Update, context: ContextTypes.DEFAULT_TYPE, location_text: str):
    """Handle location input and complete profile setup"""
    chat_id = str(update.effective_chat.id)
    
    try:
        # Parse location
        location_data = parse_location(location_text)
        
        from .bot import get_bot
        bot = get_bot()
        session = bot.get_user_session(chat_id)
        session['profile_data']['location'] = location_data
        session['state'] = 'idle'
        
        # Create complete profile summary
        profile_data = session['profile_data']
        
        summary = f"""
✅ <b>Profile Created Successfully!</b>

<b>Profile Details:</b>
📝 Name: {profile_data['name']}
💰 Budget: {format_price_range(profile_data['price_range'])}
🏠 Rooms: {format_rooms_range(profile_data['rooms_range'])}
📍 Location: {format_location(location_data)}

Your profile is now active and you'll receive notifications for matching properties!
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✏️ Edit Profile", callback_data="edit_profile")],
            [InlineKeyboardButton("🔔 Test Notification", callback_data="test_notification")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
        ])
        
        await update.message.reply_text(
            summary,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        # TODO: Save profile to database
        logger.info(f"Created new profile for user {chat_id}: {profile_data}")
        
    except ValueError as e:
        await update.message.reply_text(
            f"❌ Invalid location format: {e}\n\n"
            "Please try again with a valid format:\n"
            "• <code>Tel Aviv</code>\n"
            "• <code>Jerusalem, Haifa</code>",
            parse_mode='HTML'
        )

# Additional handler functions (placeholders for now)

async def handle_view_profiles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle view profiles action"""
    query = update.callback_query
    await query.edit_message_text("📋 <b>Your Profiles</b>\n\nProfile management coming soon!", parse_mode='HTML')

async def handle_create_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle create profile action"""
    await handle_setup_profile(update, context)

async def handle_edit_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle edit profile action"""
    query = update.callback_query
    await query.edit_message_text("✏️ <b>Edit Profile</b>\n\nProfile editing coming soon!", parse_mode='HTML')

async def handle_delete_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle delete profile action"""
    query = update.callback_query
    await query.edit_message_text("🗑️ <b>Delete Profile</b>\n\nProfile deletion coming soon!", parse_mode='HTML')

async def handle_notification_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle notification settings"""
    query = update.callback_query
    await query.edit_message_text("🔔 <b>Notification Settings</b>\n\nSettings configuration coming soon!", parse_mode='HTML')

async def handle_search_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search preferences"""
    query = update.callback_query
    await query.edit_message_text("🎯 <b>Search Preferences</b>\n\nPreferences configuration coming soon!", parse_mode='HTML')

async def handle_property_action(update: Update, context: ContextTypes.DEFAULT_TYPE, action_data: str):
    """Handle property-related actions"""
    query = update.callback_query
    await query.edit_message_text("🏠 <b>Property Action</b>\n\nProperty actions coming soon!", parse_mode='HTML')

# Utility functions for parsing user input

def parse_price_range(price_text: str) -> Dict[str, Any]:
    """Parse price range from user input"""
    price_text = price_text.strip().lower()
    
    if '-' in price_text:
        # Range format: "3000-5000"
        parts = price_text.split('-')
        if len(parts) != 2:
            raise ValueError("Invalid range format")
        min_price = int(parts[0].strip())
        max_price = int(parts[1].strip())
        return {'min': min_price, 'max': max_price}
    elif price_text.startswith('max'):
        # Max only format: "max 4000"
        max_price = int(price_text.replace('max', '').strip())
        return {'max': max_price}
    elif price_text.startswith('min'):
        # Min only format: "min 2500"
        min_price = int(price_text.replace('min', '').strip())
        return {'min': min_price}
    else:
        # Single value - treat as max
        price = int(price_text)
        return {'max': price}

def parse_rooms_range(rooms_text: str) -> Dict[str, Any]:
    """Parse rooms range from user input"""
    rooms_text = rooms_text.strip().lower()
    
    if '-' in rooms_text:
        # Range format: "2-3"
        parts = rooms_text.split('-')
        if len(parts) != 2:
            raise ValueError("Invalid range format")
        min_rooms = float(parts[0].strip())
        max_rooms = float(parts[1].strip())
        return {'min': min_rooms, 'max': max_rooms}
    elif rooms_text.startswith('max'):
        # Max only format: "max 4"
        max_rooms = float(rooms_text.replace('max', '').strip())
        return {'max': max_rooms}
    elif rooms_text.startswith('min'):
        # Min only format: "min 2"
        min_rooms = float(rooms_text.replace('min', '').strip())
        return {'min': min_rooms}
    else:
        # Single value - exact match
        rooms = float(rooms_text)
        return {'exact': rooms}

def parse_location(location_text: str) -> Dict[str, Any]:
    """Parse location from user input"""
    if ':' in location_text:
        # City with neighborhoods: "Tel Aviv: Florentin, Dizengoff"
        parts = location_text.split(':', 1)
        city = parts[0].strip()
        neighborhoods = [n.strip() for n in parts[1].split(',')]
        return {'city': city, 'neighborhoods': neighborhoods}
    elif ',' in location_text:
        # Multiple cities: "Tel Aviv, Jerusalem"
        cities = [c.strip() for c in location_text.split(',')]
        return {'cities': cities}
    else:
        # Single city: "Tel Aviv"
        return {'city': location_text.strip()}

def format_price_range(price_range: Dict[str, Any]) -> str:
    """Format price range for display"""
    if 'min' in price_range and 'max' in price_range:
        return f"{price_range['min']:,} - {price_range['max']:,} ILS"
    elif 'max' in price_range:
        return f"Up to {price_range['max']:,} ILS"
    elif 'min' in price_range:
        return f"From {price_range['min']:,} ILS"
    else:
        return "Not specified"

def format_rooms_range(rooms_range: Dict[str, Any]) -> str:
    """Format rooms range for display"""
    if 'min' in rooms_range and 'max' in rooms_range:
        return f"{rooms_range['min']} - {rooms_range['max']} rooms"
    elif 'max' in rooms_range:
        return f"Up to {rooms_range['max']} rooms"
    elif 'min' in rooms_range:
        return f"At least {rooms_range['min']} rooms"
    elif 'exact' in rooms_range:
        return f"{rooms_range['exact']} rooms"
    else:
        return "Not specified"

def format_location(location_data: Dict[str, Any]) -> str:
    """Format location for display"""
    if 'city' in location_data and 'neighborhoods' in location_data:
        neighborhoods = ', '.join(location_data['neighborhoods'])
        return f"{location_data['city']} ({neighborhoods})"
    elif 'cities' in location_data:
        return ', '.join(location_data['cities'])
    elif 'city' in location_data:
        return location_data['city']
    else:
        return "Not specified"

def setup_handlers(application):
    """Set up all bot handlers"""
    from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("notifications", notifications_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Message handlers for conversation states
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("All bot handlers registered successfully")
    return application
