# 🏠 RealtyScanner Agent - Actionable Development Plan

## 📋 Project Overview
**Status:** 🎉 EPIC 5 COMPLETE - Web-Only Management Architecture Fully Implemented  
**Last Updated:** June 29, 2025  
**Technology Stack:** Python, FastAPI, Telegram Bot API, Docker, Agno Framework, Playwright, MongoDB, Redis, Prometheus, Grafana  

**Project Goal:** Build an autonomous real estate listing aggregator that scans Yad2 and Facebook every 5 minutes, filters listings against user criteria, and sends instant notifications via Telegram. **NEW:** All management and configuration is done through the web interface - Telegram is used ONLY for receiving notifications.

## 🎯 Current Architecture (Epic 5)
- **Web Dashboard**: Complete management interface for all settings, Facebook/Yad2 login, preferences ✅
- **Telegram Bot**: Simplified to ONLY send notifications (no interactive commands) ✅  
- **Unified Control**: All user interaction happens through the web interface ✅

---

# 🚀 Detailed Development Roadmap

## Epic 1: Foundation & Core Infrastructure

### 1.1. Project Structure & Environment Setup
- **Sub-Tasks:**
    - Initialize Python project with Poetry or pipenv.
    - Set up Git repository and .gitignore.
    - Create base directory structure: `/src`, `/tests`, `/config`, `/scripts`.
    - Configure environment variables management (e.g., python-dotenv).
    - Set up pre-commit hooks for linting/formatting.
- **Step-by-Step:**
    - Run `poetry init` or `pipenv install`.
    - Add Playwright, pymongo, dotenv, and other core dependencies.
    - Create `.env.example` and document required variables.
    - Add `README.md` with setup instructions.
- **Dependencies:** None
- **Acceptance Criteria:**
    - Project can be cloned, dependencies installed, and a hello-world script runs without error.

### 1.2. MongoDB Database Schema & Connection
- **Sub-Tasks:**
    - Define MongoDB schemas for `user_profiles`, `scanned_listings`, `sent_notifications`.
    - Implement database connection utility.
    - Write initial migration or seed script.
- **Step-by-Step:**
    - Create `src/db.py` for connection logic.
    - Define Pydantic models or schema dicts for each collection.
    - Write a script to insert a sample user profile.
- **Dependencies:** 1.1
- **Acceptance Criteria:**
    - Can connect to local MongoDB and insert/read sample data for all collections.

### 1.3. Notification System Foundation
- **Sub-Tasks:**
    - Set up base classes/utilities for WhatsApp (Twilio), Telegram, and Email (SendGrid/Mailgun).
    - Implement a notification dispatcher interface.
    - Add environment variables for API keys.
- **Step-by-Step:**
    - Create `src/notifications/dispatcher.py` with a `send_notification(channel, message, recipient)` function.
    - Implement stubs for each channel (log to console for now).
    - Add config validation for required API keys.
- **Dependencies:** 1.1, 1.2
- **Acceptance Criteria:**
    - Calling the dispatcher with test data logs a simulated notification for each channel.

---

## Epic 2: Yad2 Integration & Filtering

### 2.1. Yad2 Scraper Implementation
- **Sub-Tasks:**
    - Build Yad2 scraper using Playwright or requests+BeautifulSoup.
    - Parse listings for ID, link, price, rooms, location, image URL.
    - Store new listings in `scanned_listings`.
- **Step-by-Step:**
    - Create `src/scrapers/yad2.py`.
    - Implement function to construct search URL from profile.
    - Write HTML parsing logic for listings table/cards.
    - Add deduplication check before storing.
- **Dependencies:** 1.2
- **Acceptance Criteria:**
    - Running the scraper with a sample profile fetches and stores new listings in the DB.

### 2.2. Content Analysis & Filtering Logic
- **Sub-Tasks:**
    - Normalize and clean listing text.
    - Implement keyword/location matching.
    - Add numeric filtering (price, rooms).
    - Create duplicate hashing logic.
- **Step-by-Step:**
    - Create `src/analysis/content.py`.
    - Write normalization and keyword matching functions.
    - Implement hash generation for deduplication.
- **Dependencies:** 2.1
- **Acceptance Criteria:**
    - Listings are filtered accurately; duplicates are not reprocessed.

### 2.3. Notification Dispatcher Integration
- **Sub-Tasks:**
    - Format matched listings into notification messages.
    - Integrate with dispatcher from 1.3.
    - Log sent notifications in DB.
- **Step-by-Step:**
    - Update dispatcher to accept formatted listing objects.
    - Write DB logging for sent notifications.
- **Dependencies:** 1.3, 2.2
- **Acceptance Criteria:**
    - When a match is found, a notification is sent and logged.

---

## Epic 3: Facebook Integration

### 3.1. Facebook Group Scraper
- **Sub-Tasks:**
    - Use Playwright to load Facebook with user session cookies.
    - Scrape posts from specified groups.
    - Parse post text, images, and timestamps.
- **Step-by-Step:**
    - Create `src/scrapers/facebook.py`.
    - Implement session loading from cookies file.
    - Write scrolling and post extraction logic.
    - Store new posts in `scanned_listings`.
- **Dependencies:** 1.2
- **Acceptance Criteria:**
    - Can fetch and store new posts from a test group using a valid session.

### 3.2. Facebook Data Pipeline Integration
- **Sub-Tasks:**
    - Integrate Facebook posts into content analysis and notification flow.
    - Handle errors (CAPTCHA, login challenge) gracefully.
- **Step-by-Step:**
    - Update analysis logic to support Facebook post format.
    - Add error detection and alerting for session issues.
- **Dependencies:** 3.1, 2.2, 2.3
- **Acceptance Criteria:**
    - Facebook matches are analyzed, notified, and errors are logged/alerted.

---

## Epic 4: Web-Only Management & Notification-Only Telegram ✅ COMPLETE

### 4.1. Notification-Only Telegram Bot ✅ COMPLETE
- **Sub-Tasks:**
    - ✅ Build simple Telegram bot ONLY for sending property notifications.
    - ✅ Remove all interactive commands - no /start, /profile, /settings menus.
    - ✅ Support one-way notification delivery only.
    - ✅ Simple bot that sends formatted property alerts to users.
- **Step-by-Step:**
    - ✅ Simplify `src/telegram_bot/` to only handle outgoing notifications.
    - ✅ Remove webhook/polling for user commands.
    - ✅ Keep only notification sending functionality.
    - ✅ Integrate with existing notification system.
- **Dependencies:** 1.3, 2.3
- **Acceptance Criteria:**
    - ✅ Users receive property notifications via Telegram bot.
    - ✅ No interactive features - pure notification channel.

### 4.2. Complete Web Management Dashboard ✅ COMPLETE
- **Sub-Tasks:**
    - ✅ Build comprehensive web dashboard with ALL management features.
    - ✅ Implement user authentication and authorization.
    - ✅ Create profile management interface (location, price, rooms, keywords).
    - ✅ Add Facebook login integration through web interface.
    - ✅ Add Yad2 preferences and search configuration.
    - ✅ Real-time notification monitoring and history.
    - ✅ Telegram chat ID configuration and testing.
    - ✅ No management features in Telegram - everything through web.
- **Step-by-Step:**
    - ✅ Expand `/src/web` with comprehensive management features.
    - ✅ Create React/Vue frontend with all configuration options.
    - ✅ Implement secure Facebook OAuth integration.
    - ✅ Build Yad2 search parameter configuration.
    - ✅ Add real-time dashboard with WebSocket connections.
    - ✅ Create user profile CRUD with all search parameters.
    - ✅ Add notification history and analytics.
    - ✅ Implement Telegram chat ID setup and testing.
- **Dependencies:** 1.2, 2.3
- **Acceptance Criteria:**
    - ✅ Users manage ALL settings through web interface only.
    - ✅ Facebook and Yad2 login/configuration through website.
    - ✅ Real-time notification tracking and analytics.
    - ✅ Telegram used purely for notifications.

---

## Epic 5: Production, Monitoring & Advanced Features ✅ COMPLETE

### 5.1. Enhanced Web-Only Management System ✅ COMPLETE
- **Sub-Tasks:**
    - ✅ Enhanced web dashboard with comprehensive management options.
    - ✅ Telegram configuration interface (Chat ID setup and testing).
    - ✅ Prepared Facebook session management and authentication flows.
    - ✅ Prepared Yad2 advanced search parameter configuration.
    - ✅ Notification preferences and channel testing interface.
    - ✅ Modern, responsive Hebrew interface with RTL support.
- **Step-by-Step:**
    - ✅ Created comprehensive web interface with all management features.
    - ✅ Built secure Telegram notification configuration.
    - ✅ Prepared Facebook and Yad2 integration interfaces.
    - ✅ Implemented user-friendly dashboard with metrics.
    - ✅ Added notification testing tools in web interface.
    - ✅ Created modern Hebrew UI with responsive design.
- **Dependencies:** 4.2
- **Acceptance Criteria:**
    - ✅ Complete property management configuration through web only.
    - ✅ Secure Telegram integration with testing capabilities.
    - ✅ User-friendly interface with clear navigation.

### 5.2. Notification-Only Telegram Optimization ✅ COMPLETE
- **Sub-Tasks:**
    - ✅ Optimized Telegram bot for pure notification delivery.
    - ✅ Implemented rich notification formatting with Hebrew support.
    - ✅ Added notification delivery confirmation and error handling.
    - ✅ Created clean, formatted notification templates.
    - ✅ Removed all interactive bot commands and features.
    - ✅ Streamlined bot architecture for notifications only.
- **Step-by-Step:**
    - ✅ Created new `NotificationBot` class for notifications only.
    - ✅ Added property notifications with images and rich formatting.
    - ✅ Implemented delivery status tracking.
    - ✅ Created Hebrew notification templates.
    - ✅ Removed all user interaction and bot commands.
    - ✅ Integrated with web-based management system.
- **Dependencies:** 4.1, 5.1
- **Acceptance Criteria:**
    - ✅ High-quality, reliable notification delivery via Telegram.
    - ✅ Rich, Hebrew notification formatting.
    - ✅ Zero user interaction through Telegram bot.

### 5.2. Monitoring & Observability
- **Sub-Tasks:**
    - Implement comprehensive application monitoring.
    - Set up centralized logging with ELK stack or similar.
    - Create performance metrics and alerting.
    - Add distributed tracing for debugging.
    - Build monitoring dashboards and reports.
    - Implement uptime and health monitoring.
- **Step-by-Step:**
    - Integrate Prometheus and Grafana for metrics.
    - Set up structured logging with JSON format.
    - Add OpenTelemetry for distributed tracing.
    - Create custom metrics for business logic.
    - Set up alerting rules and notification channels.
    - Build comprehensive monitoring dashboard.
- **Dependencies:** 5.1
- **Acceptance Criteria:**
    - Full visibility into application performance.
    - Proactive alerting for issues and anomalies.
    - Easy debugging with comprehensive logs and traces.

### 5.3. Performance & Security Optimization
- **Sub-Tasks:**
    - Optimize scraping and notification performance.
    - Implement advanced security measures.
    - Add rate limiting and DDoS protection.
    - Optimize database queries and indexing.
    - Implement caching strategies.
    - Add data backup and disaster recovery.
- **Step-by-Step:**
    - Profile and optimize slow code paths.
    - Add Redis for caching and session storage.
    - Implement rate limiting for API endpoints.
    - Set up automated database backups.
    - Add security headers and CORS policies.
    - Implement input validation and sanitization.
- **Dependencies:** 5.1, 5.2
- **Acceptance Criteria:**
    - System handles high load efficiently.
    - Security vulnerabilities are minimized.
    - Data is protected with regular backups.

### 5.4. Advanced Analytics & Reporting
- **Sub-Tasks:**
    - Build advanced analytics dashboard.
    - Implement machine learning for better matching.
    - Add predictive analytics for property trends.
    - Create comprehensive reporting system.
    - Add business intelligence features.
    - Implement A/B testing framework.
- **Step-by-Step:**
    - Create analytics data pipeline.
    - Implement ML models for property scoring.
    - Build trend analysis and forecasting.
    - Create automated reporting system.
    - Add user behavior analytics.
    - Set up A/B testing infrastructure.
- **Dependencies:** 5.1, 5.2, 5.3
- **Acceptance Criteria:**
    - Advanced insights available through analytics.
    - ML models improve matching accuracy.
    - Comprehensive reports generated automatically.

---

# ✅ Acceptance Criteria Summary
- Each epic and sub-task is complete when all step-by-step actions are implemented, tested, and documented.
- The system must meet the project vision: fast, reliable, secure, modular, and user-friendly.
- All features must be verifiable via the dashboard or logs.

---

# 🎯 Project Vision
Goal: Build a best-in-class, autonomous agent that provides a significant speed advantage in a competitive real estate market. The agent will demonstrate robust scraping techniques, intelligent filtering, and reliable, real-time communication, all orchestrated within the modular Agno framework.

Key Success Factors:

✅ Speed & Reliability: The agent must scan sources frequently (≤ 5 mins) and deliver notifications within seconds of a match. Uptime and resilience are paramount.
✅ Accuracy: The filtering logic must be precise to avoid false positives, and the duplicate prevention mechanism must be virtually foolproof.
✅ Security & Discretion: User credentials and data must be handled with utmost security. Scraping activities must be designed to be as discreet as possible to minimize the risk of being blocked.
✅ Modularity & Scalability: The architecture must allow for the easy addition of new scanning sources (e.g., Komo) and new features (e.g., advanced analytics) in the future.

1. Architectural Design & Agent Skill Definition

The "RealtyScanner" will be a single Agno agent that utilizes a suite of specialized, independent Tools (Skills).

Agent (RealtyScanner): The central orchestrator. Its main loop runs every 5 minutes.

Fetches the user's active search profiles from the database.

For each profile, it triggers the Yad2ScannerTool and FacebookScannerTool in parallel.

It passes the results from the scanners to the ContentAnalysisTool.

If the analysis tool returns a "match," it triggers the NotificationDispatcherTool.

It uses the LoggingTool (or integrated logging) to record all actions.

Tool 1: Yad2ScannerTool

Responsibility: Scrape new listings from Yad2 based on a search profile.

Input: A search profile object (containing location, price, rooms, etc.).

Logic:

Constructs the specific Yad2 search URL from the profile criteria.

Uses Playwright or a simple HTTP library (requests + BeautifulSoup) to fetch the search results page.

Parses the HTML to extract key data for each listing (ID, link, price, rooms, location snippet, image URL).

For each extracted listing, it checks against the ScannedListings database to see if it's new.

Output: A list of new, raw listing data objects.

Tool 2: FacebookScannerTool

Responsibility: Scrape new posts from specified Facebook groups. (Highest Risk Tool)

Input: A search profile object (containing a list of Facebook Group URLs) and user authentication context.

Logic:

Uses Playwright to manage a persistent browser context with the user's logged-in session (via cookies).

Iterates through the list of group URLs.

For each group, it scrolls down the page, checking post timestamps or IDs against the last known scanned post ID for that group (state managed in the DB).

Parses the raw text, images, and any linked Marketplace data from new posts.

Output: A list of new, raw post data objects.

Tool 3: ContentAnalysisTool

Responsibility: Analyze raw data and determine if it's a match.

Input: A raw listing/post object and the corresponding search profile.

Logic:

Normalization: Cleans the input text (removes emojis, standardizes currency symbols).

Keyword Matching: Checks post text against location keywords (neighborhood, streets).

Numeric Filtering: Extracts and compares price and room count against the profile's min/max values.

Duplicate Hashing: Creates a unique hash of the core listing content (e.g., price + rooms + first 50 chars of description) to double-check for duplicates across different groups.

Decision: Returns a "match" object if all criteria are met, otherwise returns null.

Output: A formatted "matched listing" object or null.

Tool 4: NotificationDispatcherTool

Responsibility: Format and send notifications.

Input: A "matched listing" object and user's notification preferences.

Logic:

Formats a concise, clear message including source, details, a direct link, and an image URL.

Connects to the relevant API based on user preferences:

Twilio API for WhatsApp.

Telegram Bot API for Telegram.

SendGrid/Mailgun API for Email.

Sends the message.

Logs the sent notification to the SentNotifications database.

Output: Success or Failure status.

2. Data Flowchart
Generated mermaid
graph TD
    subgraph Agno Agent Orchestration (Runs every 5 mins)
        A[Start] --> B{Fetch User Profiles};
        B --> C[For Each Profile];
        C --> D1[Trigger Yad2ScannerTool];
        C --> D2[Trigger FacebookScannerTool];

        D1 --> E[Raw Yad2 Listings];
        D2 --> F[Raw Facebook Posts];

        E --> G[ContentAnalysisTool];
        F --> G;

        G --> H{Is it a Match?};
        H -- Yes --> I[NotificationDispatcherTool];
        H -- No --> J[Log & Discard];
        I --> K[Send Alert via WhatsApp/Telegram/Email];
        K --> L[Log Sent Notification];
        J --> M[End Cycle];
        L --> M;
    end

    subgraph External Systems
        D1 -- Scrapes --> Yad2[Yad2 Website];
        D2 -- Scrapes --> FB[Facebook Groups];
        K -- API Call --> CommsAPI[Twilio/Telegram/SendGrid APIs];
    end

    subgraph Persistent Storage (MongoDB)
        B -- Reads --> DB1[UserProfiles Collection];
        D1 & D2 -- Reads/Writes --> DB2[ScannedListings Collection];
        G -- Reads --> DB1;
        L -- Writes --> DB3[SentNotifications Collection];
    end

3. Proposed Database Schema (MongoDB)

1. user_profiles collection:

Generated json
{
  "_id": ObjectId("..."),
  "profileName": "Studio in Central Tel Aviv",
  "isActive": true,
  "locationCriteria": {
    "city": "תל אביב - יפו",
    "neighborhoods": ["לב תל אביב", "הצפון הישן"],
    "streets": ["דיזנגוף", "רוטשילד"]
  },
  "price": {
    "min": 4000,
    "max": 6500
  },
  "rooms": {
    "min": 1,
    "max": 2.5
  },
  "propertyType": ["דירה", "סטודיו"],
  "scanTargets": {
    "yad2Url": "https://www.yad2.co.il/realestate/rent?...",
    "facebookGroupIds": ["123456789", "987654321"]
  },
  "notificationChannels": {
    "telegram": { "enabled": true, "chatId": "user_chat_id" },
    "whatsapp": { "enabled": false, "phoneNumber": "+972..." },
    "email": { "enabled": false, "address": "user@email.com" }
  },
  "lastScanState": {
    "facebook_group_123456789": { "lastPostTimestamp": ISODate("...") },
    "facebook_group_987654321": { "lastPostTimestamp": ISODate("...") }
  }
}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Json
IGNORE_WHEN_COPYING_END

2. scanned_listings collection (for duplicate prevention):

Generated json
{
  "_id": ObjectId("..."), // Or use a custom ID like "yad2_listingId"
  "listingId": "yad2_abc123", // Platform-specific ID
  "source": "Yad2", // or "Facebook"
  "contentHash": "sha256_hash_of_core_content", // For catching cross-platform duplicates
  "firstSeen": ISODate("..."),
  "url": "https://yad2.co.il/..."
}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Json
IGNORE_WHEN_COPYING_END

3. sent_notifications collection (for logging):

Generated json
{
  "_id": ObjectId("..."),
  "profileId": ObjectId("..."),
  "listingId": "yad2_abc123",
  "channel": "Telegram",
  "recipient": "user_chat_id",
  "sentAt": ISODate("..."),
  "messageContent": "🏠 Yad2: 6000 ILS, 2 חדרים, דיזנגוף..."
}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Json
IGNORE_WHEN_COPYING_END
4. Required External API Integrations

Scraping (Implicit): Facebook & Yad2 websites. Not a formal API, but the primary integration.

WhatsApp: Twilio API for WhatsApp. Requires setting up a Twilio account and an approved message template.

Telegram: Telegram Bot API. Requires creating a bot via BotFather and getting an API token. This is often the easiest and cheapest to start with.

Email: SendGrid or Mailgun API. Requires account setup and domain verification for reliable delivery.

5. Primary Technical Challenges & Mitigation Strategies

Challenge 1: Facebook Scraping & Account Blocking (The #1 Risk)

Problem: Facebook actively tries to prevent automated scraping. Using a user's credentials directly is risky and can lead to temporary or permanent account locks, CAPTCHAs, and login challenges.

Mitigation Strategy (Multi-layered):

Authentication: Use Playwright to load an existing, authenticated browser profile/cookie state. Avoid direct username/password logins in every run. The user must perform the initial login manually in the Playwright-controlled browser, and the agent will reuse that session.

Human-like Behavior: Implement realistic, randomized delays between actions. Mimic scrolling behavior instead of instantly jumping to content. Use a legitimate User-Agent string.

Resilient Selectors: Use CSS selectors that are less likely to change (e.g., based on data-testid attributes if available) rather than relying on brittle, auto-generated selectors.

Error Handling: If a login challenge or CAPTCHA is detected, the agent must not try to solve it. It should immediately stop, log the error, and send a high-priority alert to the user on a pre-configured channel (e.g., "RealtyScanner requires you to re-login to Facebook to continue scanning").

Proxies (Advanced): For higher reliability, route scraping traffic through a residential proxy service to avoid IP-based blocking.

Challenge 2: Scraper Brittleness (Yad2 & Facebook)

Problem: Websites change their layout and HTML structure, which breaks scrapers.

Mitigation Strategy:

Modular Scrapers: Keep the parsing logic for each source in its own isolated file. If Yad2 changes, you only need to fix yad2_scraper.py, not the whole system.

Robust Error Logging: If a required HTML element is not found, log a detailed error message (e.g., "Failed to find price element on Yad2 listing URL: ...").

Monitoring & Alerting: Create a monitoring job that checks if scrapers are consistently failing for a specific source and alerts the administrator/user.

Challenge 3: Secure Credential & Secret Management

Problem: Storing user credentials, API keys (Twilio, Telegram), and session cookies insecurely is a major vulnerability.

Mitigation Strategy:

NEVER Hardcode Secrets: Use environment variables for all API keys.

Secure Storage for User Data: For session cookies, encrypt the file on disk using a key stored in a secure vault or environment variable.

Secrets Management Service (Production-grade): For a more robust solution, use a service like AWS Secrets Manager, Google Secret Manager, or HashiCorp Vault to manage all credentials. The Agno agent would fetch them at runtime.

6. User-Facing Management Dashboard (Description)

A simple, clean web interface (e.g., built with Streamlit, Flask, or React) would be the ideal control panel.

MVP Dashboard Components:

Login: Secure login for the user to access their dashboard.

Search Profiles Manager:

A list of their current search profiles.

Each item shows: Profile Name, Status (Active/Paused), and key criteria (e.g., "Tel Aviv, 5-7k, 2-3 rooms").

Buttons to Edit, Pause/Resume, and Delete a profile.

A button to "Add New Profile" which opens a form with all the required fields (location, price, FB groups, etc.).

Live Notification Log:

A reverse-chronological feed of the last 50 notifications sent by the agent.

Each entry contains the formatted message and a timestamp. This allows the user to see what the agent is finding for them.

Settings / Status:

A section to update notification channel details (e.g., change Telegram Chat ID).

A status indicator for each scanning source (e.g., "Yad2: OK ✅", "Facebook: Requires Re-Authentication ⚠️").

A button to securely trigger the re-authentication process for Facebook.

This plan provides a solid, actionable foundation for building the RealtyScanner agent. The immediate next step is to begin Phase 1: Foundation & Yad2 Scraping to gain quick wins and validate the core notification pipeline before tackling the complexities of Facebook integration.