# 🚀 RealtyScanner Setup Guide

## Quick Start

### 1. Create GitHub Repository (Remote)

```bash
# Go to GitHub.com and create a new repository named "realtyscanner-agent"
# Then connect your local repository:

cd /Users/yaronfeldboy/Documents/aparmenttool
git remote add origin https://github.com/YOUR_USERNAME/realtyscanner-agent.git
git branch -M main
git push -u origin main
```

### 2. Environment Setup

1. **Copy environment template:**
```bash
cp .env.example .env
```

2. **Edit `.env` file with your actual values:**

#### Required for Basic Functionality:
```bash
# Generate a secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy the output to SECRET_KEY in .env

# MongoDB (you can use MongoDB Atlas for free)
MONGODB_URI=mongodb://localhost:27017  # or your MongoDB Atlas URI
MONGODB_DATABASE=realty_scanner

# Telegram Bot (ESSENTIAL)
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
```

#### Optional (for full features):
```bash
# Twilio (for WhatsApp notifications)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token

# SendGrid (for email notifications)  
SENDGRID_API_KEY=your_api_key

# Agno Framework (for AI features)
AGNO_API_KEY=your_agno_key
```

### 3. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Initialize database
python scripts/init_database.py
```

### 4. Run the Application

#### Development Mode:
```bash
# Terminal 1: Start MongoDB (if local)
mongod

# Terminal 2: Start Telegram Bot
python src/telegram_bot/run_bot.py

# Terminal 3: Start Web Dashboard
python src/web/run_server.py

# Terminal 4: Test the system
python scripts/test_complete_flow.py
```

#### Production Mode (Docker):
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f
```

## 🔧 Service-Specific Setup

### Telegram Bot Setup
1. Open Telegram and search for @BotFather
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token to `.env` file
5. Test: `python scripts/test_epic4_telegram_web.py`

### MongoDB Setup
**Option A: Local MongoDB**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**Option B: MongoDB Atlas (Recommended)**
1. Go to https://mongodb.com/atlas
2. Create free cluster
3. Get connection string
4. Update `MONGODB_URI` in `.env`

### Facebook Scraping Setup (Optional)
1. Login to Facebook in Chrome
2. Export cookies using browser extension
3. Save as `./config/facebook_cookies.json`
4. Update `FACEBOOK_COOKIES_FILE` path in `.env`

## 🧪 Testing

```bash
# Test individual components
python scripts/test_yad2_scraper.py
python scripts/test_notifications.py
python scripts/test_epic2_complete.py

# Test full integration
python scripts/test_complete_flow.py
```

## 📊 Monitoring

Access the dashboard at:
- **Development:** http://localhost:8000
- **Production:** http://your-domain.com

## 🔍 Troubleshooting

### Common Issues:

1. **MongoDB Connection Error:**
   - Check if MongoDB is running: `brew services list | grep mongo`
   - Verify connection string in `.env`

2. **Telegram Bot Not Responding:**
   - Verify token in `.env`
   - Check bot is enabled: send `/start` to your bot

3. **Scraping Issues:**
   - Update browser: `playwright install`
   - Check cookies file for Facebook

4. **Docker Issues:**
   - Check ports: `docker ps`
   - View logs: `docker-compose logs`

## 📝 Next Steps

1. **Configure your first search profile** via Telegram bot or web dashboard
2. **Set up monitoring** (Epic 5.2)
3. **Deploy to production** (Epic 5.1)
4. **Enable advanced analytics** (Epic 5.4)

## 🆘 Support

- Check logs: `tail -f logs/realtyscanner.log`
- Review documentation: `docs/`
- Test individual components in `scripts/`

---

🎯 **Goal:** Get notifications for new apartment listings within 5 minutes of posting!
