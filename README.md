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

## 🏗️ Project Structure

```
aparmenttool/
├── src/                    # Main source code
│   ├── telegram_bot/      # Interactive Telegram bot
│   │   ├── bot.py         # Bot application
│   │   ├── handlers.py    # Command and message handlers
│   │   ├── utils.py       # Utility functions
│   │   └── run_bot.py     # Bot runner script
│   ├── web/               # Web dashboard
│   │   ├── app.py         # FastAPI application
│   │   ├── api.py         # API endpoints
│   │   ├── auth.py        # Authentication
│   │   ├── websocket.py   # Real-time updates
│   │   ├── templates/     # HTML templates
│   │   └── run_server.py  # Server runner script
│   ├── scrapers/          # Web scrapers (Yad2, Facebook)
│   ├── analysis/          # Content analysis and filtering
│   ├── notifications/     # Multi-channel notifications
│   ├── db.py             # Database connection and models
│   └── main.py           # Main application entry point
├── tests/                 # Test files
├── scripts/              # Test and utility scripts
├── docs/                 # Documentation
│   ├── Todo.md           # Development roadmap
│   └── Epic4_Implementation_Guide.md  # Epic 4 guide
└── agno/                 # Agno framework (git submodule)
```

The project follows a detailed roadmap outlined in `docs/Todo.md`:

- ✅ **Epic 1.1**: Project Structure & Environment Setup
- 🏗️ **Epic 1.2**: MongoDB Database Schema & Connection
- 📋 **Epic 1.3**: Notification System Foundation
- 📋 **Epic 2**: Yad2 Integration & Filtering
- 📋 **Epic 3**: Facebook Integration
- 📋 **Epic 4**: User Management & Dashboard
- 📋 **Epic 5**: Production, Monitoring & Optimization

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
