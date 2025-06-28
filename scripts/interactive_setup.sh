#!/bin/bash

# Interactive Setup Script for RealtyScanner
echo "🏠 RealtyScanner Interactive Setup"
echo "=================================="
echo ""

# Function to update .env file
update_env() {
    local key=$1
    local value=$2
    local file=".env"
    
    if grep -q "^${key}=" "$file"; then
        # Key exists, replace it
        sed -i '' "s|^${key}=.*|${key}=${value}|" "$file"
        echo "✅ Updated ${key}"
    else
        # Key doesn't exist, add it
        echo "${key}=${value}" >> "$file"
        echo "✅ Added ${key}"
    fi
}

echo "📱 STEP 1: Create Telegram Bot"
echo "1. Open Telegram and search for @BotFather"
echo "2. Send: /newbot"
echo "3. Choose a name for your bot (e.g., 'My Realty Scanner')"
echo "4. Choose a username ending with 'bot' (e.g., 'myrealtyscanner_bot')"
echo "5. Copy the token you receive"
echo ""
read -p "Enter your Telegram Bot Token: " bot_token

if [ ! -z "$bot_token" ]; then
    update_env "TELEGRAM_BOT_TOKEN" "$bot_token"
else
    echo "⚠️ Skipping Telegram Bot setup - you can add it later"
fi

echo ""
echo "🗄️ STEP 2: MongoDB Setup"
echo "Choose your MongoDB option:"
echo "1. MongoDB Atlas (Free, Recommended)"
echo "2. Local MongoDB"
echo "3. Skip for now"
echo ""
read -p "Choose option (1/2/3): " mongo_choice

case $mongo_choice in
    1)
        echo ""
        echo "📊 MongoDB Atlas Setup:"
        echo "1. Go to https://mongodb.com/atlas"
        echo "2. Create a free account"
        echo "3. Create a new cluster (free tier)"
        echo "4. Create a database user"
        echo "5. Get connection string (Connect -> Drivers -> Python)"
        echo "   It should look like: mongodb+srv://username:password@cluster.mongodb.net/database"
        echo ""
        read -p "Enter your MongoDB Atlas URI: " mongo_uri
        if [ ! -z "$mongo_uri" ]; then
            update_env "MONGODB_URI" "$mongo_uri"
        fi
        ;;
    2)
        echo "Installing MongoDB locally..."
        if command -v brew &> /dev/null; then
            brew install mongodb-community
            brew services start mongodb-community
            echo "✅ MongoDB installed and started"
            echo "✅ Using local MongoDB: mongodb://localhost:27017"
        else
            echo "⚠️ Homebrew not found. Please install MongoDB manually"
            echo "Visit: https://docs.mongodb.com/manual/installation/"
        fi
        ;;
    3)
        echo "⚠️ Skipping MongoDB setup - you can configure it later"
        ;;
esac

echo ""
echo "🎯 STEP 3: Optional Services"
echo ""
read -p "Do you want to set up WhatsApp notifications via Twilio? (y/n): " setup_whatsapp

if [ "$setup_whatsapp" = "y" ]; then
    echo "📱 Twilio WhatsApp Setup:"
    echo "1. Go to https://twilio.com"
    echo "2. Create account and get Account SID and Auth Token"
    echo "3. Enable WhatsApp sandbox for testing"
    echo ""
    read -p "Enter Twilio Account SID: " twilio_sid
    read -p "Enter Twilio Auth Token: " twilio_token
    
    if [ ! -z "$twilio_sid" ]; then
        update_env "TWILIO_ACCOUNT_SID" "$twilio_sid"
    fi
    if [ ! -z "$twilio_token" ]; then
        update_env "TWILIO_AUTH_TOKEN" "$twilio_token"
    fi
fi

echo ""
read -p "Do you want to set up email notifications via SendGrid? (y/n): " setup_email

if [ "$setup_email" = "y" ]; then
    echo "📧 SendGrid Setup:"
    echo "1. Go to https://sendgrid.com"
    echo "2. Create account and verify email"
    echo "3. Create API key in Settings -> API Keys"
    echo ""
    read -p "Enter SendGrid API Key: " sendgrid_key
    
    if [ ! -z "$sendgrid_key" ]; then
        update_env "SENDGRID_API_KEY" "$sendgrid_key"
    fi
fi

echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "🧪 Test your configuration:"
echo "python scripts/setup_env.py --validate"
echo ""
echo "🚀 Start the application:"
echo "python src/telegram_bot/run_bot.py"
echo ""
echo "📊 Access web dashboard:"
echo "python src/web/run_server.py"
echo "Then open: http://localhost:8000"
echo ""
echo "🤖 Test your Telegram bot by sending /start"
