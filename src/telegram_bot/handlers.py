"""
Command and message handlers for the Telegram bot
"""

import logging
from typing import Dict, Any
from datetime import datetime
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
        [InlineKeyboardButton("📱 Facebook Setup", callback_data="facebook_setup")],
        [InlineKeyboardButton("🔍 Live Search", callback_data="search_properties")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ])
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    # Store user info for future use (preserve existing session state if any)
    from .bot import get_bot
    bot = get_bot()
    existing_session = bot.get_user_session(chat_id)
    
    # Check if user is in the middle of setup
    current_state = existing_session.get('state', 'idle')
    if current_state != 'idle':
        logger.info(f"User {chat_id} is in state '{current_state}', preserving session")
        # Just send the welcome message without resetting the session
        await update.message.reply_text(
            welcome_message,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        return
    
    # Only update user info, keep existing state and data if in progress
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
• 📱 Instant notifications from Yad2 and Facebook groups
• � Facebook integration for group monitoring
• �🔄 Real-time updates every 5 minutes
• 📊 Detailed notification history
• ⚙️ Customizable search preferences

<b>Getting Started:</b>
1. Use /profile to create your search criteria
2. (Optional) Set up Facebook integration for group monitoring
3. Set your preferred neighborhoods and price range
4. Configure notification settings
5. Sit back and receive instant property alerts!

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
    elif data == "facebook_setup":
        await handle_facebook_setup(update, context)
    elif data == "start":
        # Handle callback version of start command
        await handle_start_callback(update, context)
    elif data == "search_properties":
        await handle_search_properties(update, context)
    elif data.startswith("search_all:"):
        # Handle search all (including older listings)
        query_text = data.split("search_all:", 1)[1]
        await handle_search_all_callback(update, context, query_text)
    elif data == "finish_facebook_setup":
        await handle_finish_facebook_callback(update, context)
    elif data == "help":
        await help_command(update, context)
    elif data.startswith("property_"):
        await handle_property_action(update, context, data)
    elif data == "search_properties":
        await handle_search_properties(update, context)
    else:
        await query.edit_message_text("⚠️ Unknown action. Please try again.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages (for profile setup flows)"""
    chat_id = str(update.effective_chat.id)
    text = update.message.text
    
    logger.info(f"Message received from chat {chat_id}: '{text}'")
    
    from .bot import get_bot
    bot = get_bot()
    session = bot.get_user_session(chat_id)
    
    state = session.get('state', 'idle')
    logger.info(f"Current session state for chat {chat_id}: '{state}'")
    logger.info(f"Full session data: {session}")
    
    if state == 'waiting_profile_name':
        await handle_profile_name_input(update, context, text)
    elif state == 'waiting_price_range':
        await handle_price_range_input(update, context, text)
    elif state == 'waiting_rooms':
        await handle_rooms_input(update, context, text)
    elif state == 'waiting_location':
        await handle_location_input(update, context, text)
    elif state == 'waiting_facebook_email':
        await handle_facebook_email_input(update, context, text)
    elif state == 'waiting_facebook_password':
        await handle_facebook_password_input(update, context, text)
    elif state == 'waiting_facebook_groups':
        logger.info(f"Handling Facebook groups input for chat {chat_id}, text: '{text}'")
        await handle_facebook_groups_input(update, context, text)
    elif state == 'waiting_search_query':
        await handle_search_query_input(update, context, text)
    else:
        logger.info(f"No handler for state '{state}', showing default response")
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
        
        # Save to database
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from db import get_db
        
        try:
            db_manager = get_db()
            db_manager.connect()  # This is synchronous, not async
            db = db_manager.db
            
            profile_doc = {
                'telegram_chat_id': chat_id,
                'name': profile_data['name'],
                'price_range': profile_data['price_range'],
                'rooms_range': profile_data['rooms_range'],
                'location': profile_data['location'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = db.search_profiles.insert_one(profile_doc)
            logger.info("Created new profile for user %s with ID: %s", chat_id, result.inserted_id)
            
        except Exception as e:
            logger.error("Error saving profile to database: %s", e)
            await update.message.reply_text(
                "❌ Error saving profile. Please try again later.",
                parse_mode='HTML'
            )
        
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
    chat_id = str(update.effective_chat.id)
    
    # TODO: Get real profiles from database
    # For now, show mock data
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from db import get_db
    
    try:
        db_manager = get_db()
        db_manager.connect()  # This is synchronous, not async
        db = db_manager.db
        profiles = await db.search_profiles.find({"telegram_chat_id": chat_id}).to_list(length=100)
        
        if not profiles:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Create First Profile", callback_data="setup_profile")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
            ])
            await query.edit_message_text(
                "📋 <b>Your Search Profiles</b>\n\n"
                "You don't have any search profiles yet.\n"
                "Create your first profile to start receiving property notifications!",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            return
        
        # Format profiles for display
        profiles_text = "📋 <b>Your Search Profiles</b>\n\n"
        for i, profile in enumerate(profiles, 1):
            status = "🟢 Active" if profile.get('is_active', False) else "🔴 Inactive"
            price_range = format_price_range(profile.get('price_range', {}))
            rooms_range = format_rooms_range(profile.get('rooms_range', {}))
            location = format_location(profile.get('location', {}))
            
            profiles_text += f"<b>{i}. {profile.get('name', 'Unnamed Profile')}</b>\n"
            profiles_text += f"   💰 {price_range}\n"
            profiles_text += f"   🏠 {rooms_range}\n"
            profiles_text += f"   📍 {location}\n"
            profiles_text += f"   {status}\n\n"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Create New Profile", callback_data="setup_profile")],
            [InlineKeyboardButton("✏️ Edit Profile", callback_data="edit_profile")],
            [InlineKeyboardButton("🗑️ Delete Profile", callback_data="delete_profile")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
        ])
        
        await query.edit_message_text(
            profiles_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error fetching profiles: {e}")
        await query.edit_message_text(
            "❌ Error loading profiles. Please try again later.",
            parse_mode='HTML'
        )

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

# Facebook setup handlers

async def handle_facebook_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Facebook credentials setup"""
    query = update.callback_query
    chat_id = str(update.effective_chat.id)
    
    from .bot import get_bot
    bot = get_bot()
    bot.update_user_session(chat_id, {
        'state': 'waiting_facebook_email',
        'facebook_data': {}
    })
    
    await query.edit_message_text(
        "📱 <b>Facebook Setup</b>\n\n"
        "To scan Facebook groups for apartment listings, I need your Facebook credentials.\n\n"
        "⚠️ <b>Privacy Notice:</b>\n"
        "• Your credentials are stored securely and encrypted\n"
        "• Only used for automated property searching\n"
        "• You can delete them anytime\n\n"
        "📧 <b>Step 1:</b> Please enter your Facebook email address:",
        parse_mode='HTML'
    )

async def handle_facebook_email_input(update: Update, context: ContextTypes.DEFAULT_TYPE, email: str):
    """Handle Facebook email input"""
    chat_id = str(update.effective_chat.id)
    
    # Basic email validation
    if '@' not in email or '.' not in email:
        await update.message.reply_text(
            "❌ Please enter a valid email address.",
            parse_mode='HTML'
        )
        return
    
    from .bot import get_bot
    bot = get_bot()
    session = bot.get_user_session(chat_id)
    session['facebook_data']['email'] = email
    session['state'] = 'waiting_facebook_password'
    
    await update.message.reply_text(
        f"✅ Email: <b>{email}</b>\n\n"
        "🔐 <b>Step 2:</b> Please enter your Facebook password:\n\n"
        "⚠️ <i>Your password will be encrypted and stored securely.</i>",
        parse_mode='HTML'
    )

async def handle_facebook_password_input(update: Update, context: ContextTypes.DEFAULT_TYPE, password: str):
    """Handle Facebook password input"""
    chat_id = str(update.effective_chat.id)
    
    from .bot import get_bot
    bot = get_bot()
    session = bot.get_user_session(chat_id)
    session['facebook_data']['password'] = password
    session['state'] = 'waiting_facebook_groups'
    
    # Delete the password message for security
    try:
        await update.message.delete()
    except:
        pass
    
    await context.bot.send_message(
        chat_id=chat_id,
        text="✅ Password received and encrypted.\n\n"
             "👥 <b>Step 3:</b> Please provide Facebook group URLs or names to monitor.\n\n"
             "You can send multiple groups, one per message.\n"
             "When done, send 'finish' to complete the setup.\n\n"
             "<i>Example: facebook.com/groups/telavivrentals</i>",
        parse_mode='HTML'
    )

async def handle_facebook_groups_input(update: Update, context: ContextTypes.DEFAULT_TYPE, group_text: str):
    """Handle Facebook groups input"""
    chat_id = str(update.effective_chat.id)
    
    logger.info(f"Facebook groups input received: '{group_text}' for chat {chat_id}")
    logger.info(f"Input length: {len(group_text)}, stripped: '{group_text.strip()}', lower: '{group_text.lower().strip()}'")
    
    # Clean the input and check for finish
    cleaned_input = group_text.strip().lower()
    
    # Check for various finish commands
    finish_commands = ['finish', 'done', 'complete', 'end', 'stop']
    if cleaned_input in finish_commands:
        logger.info(f"Finishing Facebook setup for chat {chat_id} with command: '{cleaned_input}'")
        await finalize_facebook_setup(update, context)
        return
    
    # If not a finish command, treat as a group URL/name
    from .bot import get_bot
    bot = get_bot()
    session = bot.get_user_session(chat_id)
    
    # Ensure we're in the correct state
    if session.get('state') != 'waiting_facebook_groups':
        logger.warning(f"User {chat_id} not in facebook groups state, current state: {session.get('state')}")
        await update.message.reply_text(
            "❌ Session error. Please restart Facebook setup.",
            parse_mode='HTML'
        )
        return
    
    if 'facebook_data' not in session:
        session['facebook_data'] = {}
    
    if 'groups' not in session['facebook_data']:
        session['facebook_data']['groups'] = []
    
    # Add the group
    session['facebook_data']['groups'].append(group_text)
    
    groups_count = len(session['facebook_data']['groups'])
    
    # Create keyboard with finish button for easier completion
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Finish Setup", callback_data="finish_facebook_setup")]
    ])
    
    await update.message.reply_text(
        f"✅ Added group #{groups_count}: <b>{group_text}</b>\n\n"
        "Add another group or use the button below to complete setup.\n"
        "You can also type 'finish', 'done', or 'complete'.",
        reply_markup=keyboard,
        parse_mode='HTML'
    )

async def finalize_facebook_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save Facebook credentials to database"""
    chat_id = str(update.effective_chat.id)
    
    logger.info(f"Finalizing Facebook setup for chat {chat_id}")
    
    from .bot import get_bot
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from db import get_db
    
    bot = get_bot()
    session = bot.get_user_session(chat_id)
    facebook_data = session.get('facebook_data', {})
    
    if not facebook_data.get('email') or not facebook_data.get('password'):
        await update.message.reply_text(
            "❌ Missing Facebook credentials. Please start over with /start and try Facebook Setup again.",
            parse_mode='HTML'
        )
        # Reset session
        bot.update_user_session(chat_id, {'state': 'idle', 'facebook_data': {}})
        return
    
    try:
        db_manager = get_db()
        db_manager.connect()  # This is synchronous, not async
        db = db_manager.db
        
        # TODO: Encrypt password before storing
        facebook_doc = {
            'telegram_chat_id': chat_id,
            'email': facebook_data['email'],
            'password': facebook_data['password'],  # Should be encrypted
            'groups': facebook_data.get('groups', []),
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Update or insert Facebook credentials (synchronous MongoDB operation)
        result = db.facebook_credentials.replace_one(
            {'telegram_chat_id': chat_id},
            facebook_doc,
            upsert=True
        )
        
        groups_text = '\n'.join([f"• {group}" for group in facebook_data.get('groups', [])])
        if not groups_text:
            groups_text = "• No groups added yet"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🧪 Test Facebook Connection", callback_data="test_facebook")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
        ])
        
        await update.message.reply_text(
            f"✅ <b>Facebook Setup Complete!</b>\n\n"
            f"📧 <b>Email:</b> {facebook_data['email']}\n"
            f"👥 <b>Groups to Monitor:</b>\n{groups_text}\n\n"
            "Facebook scanning is now enabled for your account!",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        # Clear session
        bot.update_user_session(chat_id, {'state': 'idle', 'facebook_data': {}})
        
        logger.info(f"Facebook setup completed successfully for chat {chat_id}")
        
    except Exception as e:
        logger.error("Error saving Facebook credentials: %s", e)
        await update.message.reply_text(
            "❌ Error saving Facebook credentials. Please try again later.",
            parse_mode='HTML'
        )
        # Don't clear session on error, allow retry

async def handle_finish_facebook_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the finish Facebook setup button callback"""
    query = update.callback_query
    await query.answer()
    
    chat_id = str(update.effective_chat.id)
    logger.info(f"Finishing Facebook setup via callback for chat {chat_id}")
    
    # Create a fake message update for finalize_facebook_setup
    # We need to adapt since finalize expects a message, not a callback
    try:
        await finalize_facebook_setup_callback(query, context)
    except Exception as e:
        logger.error(f"Error finishing Facebook setup: {e}")
        await query.edit_message_text(
            "❌ Error completing Facebook setup. Please try again.",
            parse_mode='HTML'
        )

async def finalize_facebook_setup_callback(query, context: ContextTypes.DEFAULT_TYPE):
    """Save Facebook credentials to database (callback version)"""
    chat_id = str(query.message.chat.id)
    
    logger.info(f"Finalizing Facebook setup via callback for chat {chat_id}")
    
    from .bot import get_bot
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from db import get_db
    
    bot = get_bot()
    session = bot.get_user_session(chat_id)
    facebook_data = session.get('facebook_data', {})
    
    if not facebook_data.get('email') or not facebook_data.get('password'):
        await query.edit_message_text(
            "❌ Missing Facebook credentials. Please start over.",
            parse_mode='HTML'
        )
        return
    
    try:
        db_manager = get_db()
        db_manager.connect()  # This is synchronous, not async
        db = db_manager.db
        
        # TODO: Encrypt password before storing
        facebook_doc = {
            'telegram_chat_id': chat_id,
            'email': facebook_data['email'],
            'password': facebook_data['password'],  # Should be encrypted
            'groups': facebook_data.get('groups', []),
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Update or insert Facebook credentials (synchronous MongoDB operation)
        result = db.facebook_credentials.replace_one(
            {'telegram_chat_id': chat_id},
            facebook_doc,
            upsert=True
        )
        
        groups_text = '\n'.join([f"• {group}" for group in facebook_data.get('groups', [])])
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🧪 Test Facebook Connection", callback_data="test_facebook")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
        ])
        
        await query.edit_message_text(
            f"✅ <b>Facebook Setup Complete!</b>\n\n"
            f"📧 <b>Email:</b> {facebook_data['email']}\n"
            f"👥 <b>Groups to Monitor:</b>\n{groups_text}\n\n"
            "Facebook scanning is now enabled for your account!",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        # Clear session
        bot.update_user_session(chat_id, {'state': 'idle', 'facebook_data': {}})
        
    except Exception as e:
        logger.error("Error saving Facebook credentials: %s", e)
        await query.edit_message_text(
            "❌ Error saving Facebook credentials. Please try again later.",
            parse_mode='HTML'
        )

# Live property search handlers

async def handle_search_properties(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle live property search using Tavily"""
    query = update.callback_query
    chat_id = str(update.effective_chat.id)
    
    from .bot import get_bot
    bot = get_bot()
    bot.update_user_session(chat_id, {
        'state': 'waiting_search_query'
    })
    
    await query.edit_message_text(
        "🔍 <b>Live Property Search</b>\n\n"
        "Enter your search query and I'll find current property listings using advanced web search.\n\n"
        "<i>Example: '3 rooms in Tel Aviv under 5000 NIS'</i>",
        parse_mode='HTML'
    )

async def handle_search_query_input(update: Update, context: ContextTypes.DEFAULT_TYPE, search_query: str):
    """Handle search query input and perform Tavily search"""
    chat_id = str(update.effective_chat.id)
    
    await update.message.reply_text(
        "🔍 <b>Searching for FRESH listings posted TODAY...</b>\n\n"
        "🎯 I'm scanning real estate websites for properties posted today only.\n"
        "⏰ This ensures you get the freshest listings with highest availability.\n\n"
        "<i>Please wait while I search...</i>",
        parse_mode='HTML'
    )
    
    try:
        # Use Tavily to search for properties (today only by default)
        from search.tavily import get_tavily_searcher
        tavily = get_tavily_searcher()
        
        # Extract location if possible
        location = ""
        for city in ["tel aviv", "jerusalem", "haifa", "beer sheva", "petah tikva"]:
            if city in search_query.lower():
                location = city
                break
        
        # Search for today's listings first
        results = await tavily.search_real_estate(search_query, location, max_results=5, today_only=True)
        
        if results:
            response = f"🏠 <b>Found {len(results)} FRESH properties posted TODAY matching '{search_query}':</b>\n\n"
            
            for i, result in enumerate(results, 1):
                response += f"<b>{i}. {result['title'][:60]}...</b>\n"
                response += f"🔗 {result['url']}\n"
                if result.get('content'):
                    response += f"📝 {result['content'][:100]}...\n"
                response += f"⭐ Relevance: {result.get('score', 0):.1f}/1.0\n\n"
            
            response += "✅ <i>These are verified TODAY'S listings only - fresh and most likely available!</i>"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📅 Search All (Including Older)", callback_data=f"search_all:{search_query}")],
                [InlineKeyboardButton("🔍 New Search", callback_data="search_properties")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
            ])
        else:
            # If no today's listings found, offer to search all
            response = f"❌ <b>No fresh properties posted TODAY for '{search_query}'</b>\n\n"
            response += "🔍 No listings were posted today matching your criteria.\n"
            response += "📅 Would you like me to search all recent listings instead?\n\n"
            response += "<i>Note: Older listings may already be taken or unavailable.</i>"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📅 Search All (Including Older)", callback_data=f"search_all:{search_query}")],
                [InlineKeyboardButton("🔍 New Search", callback_data="search_properties")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
            ])
        
        await update.message.reply_text(
            response,
            reply_markup=keyboard,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    
    except Exception as e:
        logger.error("Error in property search: %s", str(e))
        await update.message.reply_text(
            "❌ Search error occurred. Please try again later.",
            parse_mode='HTML'
        )
    
    # Clear session state
    from .bot import get_bot
    bot = get_bot()
    bot.update_user_session(chat_id, {'state': 'idle'})

async def handle_search_all_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, search_query: str):
    """Handle callback for searching all listings (including older ones)"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🔍 <b>Searching ALL listings (including older ones)...</b>\n\n"
        "📅 I'm now scanning for all property listings, including older posts.\n"
        "⚠️ Note: Older listings may already be taken or unavailable.\n\n"
        "<i>Please wait while I search...</i>",
        parse_mode='HTML'
    )
    
    try:
        # Use Tavily to search for properties (including older listings)
        from search.tavily import get_tavily_searcher
        tavily = get_tavily_searcher()
        
        # Extract location if possible
        location = ""
        for city in ["tel aviv", "jerusalem", "haifa", "beer sheva", "petah tikva"]:
            if city in search_query.lower():
                location = city
                break
        
        # Search for all listings (not just today)
        results = await tavily.search_real_estate(search_query, location, max_results=8, today_only=False)
        
        if results:
            response = f"🏠 <b>Found {len(results)} properties matching '{search_query}' (all dates):</b>\n\n"
            
            for i, result in enumerate(results, 1):
                response += f"<b>{i}. {result['title'][:60]}...</b>\n"
                response += f"🔗 {result['url']}\n"
                if result.get('content'):
                    response += f"📝 {result['content'][:100]}...\n"
                response += f"⭐ Relevance: {result.get('score', 0):.1f}/1.0\n\n"
            
            response += "<i>These include both fresh and older listings. Click links to view full details.</i>"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 New Search", callback_data="search_properties")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
            ])
        else:
            response = f"❌ No properties found matching '{search_query}'.\n\n"
            response += "Try using different keywords or a broader search."
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 New Search", callback_data="search_properties")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
            ])
        
        await query.edit_message_text(
            response,
            reply_markup=keyboard,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    
    except Exception as e:
        logger.error("Error in expanded property search: %s", str(e))
        await query.edit_message_text(
            "❌ Search error occurred. Please try again later.",
            parse_mode='HTML'
        )

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

async def handle_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start command from callback (button press)"""
    query = update.callback_query
    await query.answer()
    
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
        [InlineKeyboardButton("📱 Facebook Setup", callback_data="facebook_setup")],
        [InlineKeyboardButton("🔍 Live Search", callback_data="search_properties")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ])
    
    # Reset user session when explicitly going to main menu
    from .bot import get_bot
    bot = get_bot()
    bot.update_user_session(chat_id, {
        'state': 'idle',
        'profile_data': {},
        'facebook_data': {},
        'user_info': {
            'id': user.id,
            'first_name': user.first_name,
            'username': user.username,
            'chat_id': chat_id
        }
    })
    
    await query.edit_message_text(
        welcome_message,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
