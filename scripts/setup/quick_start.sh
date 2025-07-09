#!/bin/bash
# Quick Start Script for RealtyScanner Agent
# This script helps you get the essential services running

echo "🏠 RealtyScanner Quick Start"
echo "================================"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📁 Creating environment configuration..."
    python scripts/setup_env.py
fi

echo ""
echo "🔧 Essential Configuration Needed:"
echo "Please update your .env file with:"
echo ""

# Check for Telegram Bot Token
if grep -q "TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here" .env; then
    echo "❌ TELEGRAM_BOT_TOKEN - Required!"
    echo "   1. Open Telegram and message @BotFather"
    echo "   2. Send: /newbot"
    echo "   3. Follow instructions to create bot"
    echo "   4. Copy token to .env file"
    echo ""
fi

# Check for MongoDB
if grep -q "MONGODB_URI=mongodb://localhost:27017" .env; then
    echo "⚠️  MONGODB_URI - Using local MongoDB"
    echo "   Option A: Install local MongoDB:"
    echo "   brew install mongodb-community"
    echo "   brew services start mongodb-community"
    echo ""
    echo "   Option B: Use MongoDB Atlas (recommended):"
    echo "   1. Go to https://mongodb.com/atlas"
    echo "   2. Create free cluster"
    echo "   3. Get connection string"
    echo "   4. Update MONGODB_URI in .env"
    echo ""
fi

echo "📝 After configuring, test with:"
echo "   python scripts/setup_env.py --validate"
echo "   python scripts/test_complete_flow.py"
echo ""

echo "🚀 To start the application:"
echo "   # Development mode:"
echo "   python src/telegram_bot/run_bot.py &      # start Telegram bot"
echo "   python src/web/run_server.py &           # start web dashboard"
echo "   python scripts/run_worker.py             # start background worker"
echo ""
echo "   # Production mode:"
echo "   docker-compose up -d"
echo ""

echo "📊 Access dashboard at: http://localhost:8000"
echo "🤖 Test your Telegram bot by sending /start"

# Automatically launch development services
echo "🛫 Launching all development services..."
python src/telegram_bot/run_bot.py &

# Free port 8000 if in use
if command -v lsof > /dev/null && lsof -ti tcp:8000 > /dev/null; then
  echo "⚠️ Port 8000 in use, terminating existing process"
  kill -9 $(lsof -ti tcp:8000)
fi
python src/web/run_server.py &
exec python scripts/run_worker.py
