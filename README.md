# RealtyScanner Agent 🏠

An autonomous real estate listing aggregator that scans Yad2 and Facebook every 5 minutes, filters listings against user criteria, and sends instant notifications via interactive Telegram bot, web dashboard, WhatsApp, and Email using the Agno framework.

## 🚀 Features

- **Multi-source Scanning**: Automated scraping of Yad2 and Facebook groups
- **Intelligent Filtering**: Advanced content analysis with location and price matching
- **Interactive Telegram Bot**: Full-featured bot with conversational profile setup
- **Professional Web Dashboard**: Modern interface for profile and notification management
- **Multi-channel Notifications**: Telegram, WhatsApp, Email, and real-time web alerts
- **Real-time Synchronization**: Cross-platform data sync and live updates
- **Built with Agno**: Leverages the powerful Agno framework for multi-agent systems

## 📁 Project Structure

```
aparmenttool/
├── config/            # Configuration files and environment variables
├── deployment/        # Docker and deployment configuration files
├── docs/             # Documentation and guides
├── frontend/         # Web frontend assets
├── logs/             # Application logs
├── scripts/          # Utility and automation scripts
├── src/              # Source code
│   ├── analysis/     # Content analysis modules
│   ├── notifications/# Notification system
│   ├── scrapers/     # Data scraping modules
│   ├── search/       # Search functionality
│   ├── telegram/     # Telegram integration
│   ├── telegram_bot/ # Telegram bot implementation
│   └── web/          # Web server and dashboard
└── tests/            # Test suites
    ├── epic_tests/   # Tests for project epics
    ├── integration/  # Integration tests
    ├── system/       # System tests
    └── unit/         # Unit tests
```

## 📋 Project Status

**Status**: ✅ EPIC 4 COMPLETE - Multi-platform Telegram Bot & Web Dashboard  
**Technology Stack**: Python, FastAPI, Telegram Bot API, Agno Framework, Playwright, MongoDB  
**Last Updated**: June 28, 2025

### 🎉 Recently Completed: Epic 4

**🤖 Interactive Telegram Bot**
- Conversational profile setup and management
- Rich property notifications with inline buttons  
- Command system (/start, /profile, /settings, /notifications)
- Real-time user interaction and feedback

**🌐 Professional Web Dashboard**
- Modern FastAPI backend with RESTful API
- Responsive interface with real-time updates
- Authentication and session management
- Comprehensive analytics and monitoring

**🔄 Cross-platform Integration**
- Unified user experience across bot and web
- Real-time data synchronization
- Multi-channel notification enhancement
- Seamless profile management

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.11+
- MongoDB (local or cloud instance)
- Telegram Bot Token (from @BotFather)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aparmenttool
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and configuration
   ```

   **Required Environment Variables:**
   ```bash
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   SECRET_KEY=your_secret_key_here
   MONGODB_URL=mongodb://localhost:27017/realtyscanner
   ```

4. **Get Telegram Bot Token**
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Send `/newbot` and follow instructions
   - Copy your bot token to the environment file

### 🚀 Quick Start

#### Start Telegram Bot
```bash
# Development mode (polling)
python src/telegram_bot/run_bot.py --mode polling --debug

# Production mode (webhook)
python src/telegram_bot/run_bot.py --mode webhook --webhook-url https://your-domain.com
```

#### Start Web Dashboard
```bash
# Development server
python src/web/run_server.py --host 0.0.0.0 --port 8000 --reload

# Access dashboard at: http://localhost:8000
# API docs at: http://localhost:8000/api/docs
```

#### Test the System
```bash
# Run Epic 4 tests
python scripts/test_epic4_telegram_web.py

# Run notification system tests
python scripts/test_notifications_sim.py

# Run complete integration test
python scripts/test_epic2_complete.py
```

### 📱 Using the Telegram Bot

1. **Start the bot**: Send `/start` to your Telegram bot
2. **Create profile**: Click "🔧 Setup Profile" and follow the conversation
3. **Manage settings**: Use `/settings` to configure notifications
4. **View notifications**: Use `/notifications` to see recent alerts

### 🌐 Using the Web Dashboard

1. **Access dashboard**: Open http://localhost:8000
2. **Login**: Use demo credentials (admin/admin)
3. **Manage profiles**: Create, edit, and monitor search profiles
4. **View analytics**: Track notifications and system performance

## 🔧 Configuration

### API Keys Required

1. **Telegram Bot**: Create via [@BotFather](https://t.me/botfather)
2. **Twilio** (for WhatsApp): Sign up at [twilio.com](https://www.twilio.com/)
3. **SendGrid** (for Email): Sign up at [sendgrid.com](https://sendgrid.com/)
4. **Agno**: Get API key from [agno.com](https://agno.com/)

### Database Schema

The application uses three main MongoDB collections:
- `user_profiles`: Search criteria and preferences
- `scanned_listings`: Listing cache for deduplication
- `sent_notifications`: Notification history

## 🚨 Security Notes

- Never commit API keys to version control
- Use environment variables for all sensitive configuration
- Facebook session cookies are encrypted at rest
- Implement rate limiting for API calls

## 📚 Documentation

- [Complete Development Plan](docs/Todo.md)
- [Architecture Overview](docs/Todo.md#architectural-design--agent-skill-definition)
- [Database Schema](docs/Todo.md#proposed-database-schema-mongodb)

## 🤝 Contributing

1. Follow the development roadmap in `docs/Todo.md`
2. Use conventional commits
3. Run tests before submitting PRs
4. Follow the established code style (Black + isort)

## 📄 License

MIT License - see LICENSE file for details

---

**Built with ❤️ using the Agno Framework**
