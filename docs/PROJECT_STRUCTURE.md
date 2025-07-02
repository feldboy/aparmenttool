# Project Structure Guide

This document explains the organization of the RealtyScanner Agent project.

## Directory Structure

The project is organized into the following main directories:

### `/config`
Contains configuration files and environment variables for the application.
- `.env` - Active environment variables
- `.env.example` - Template for environment variables

### `/deployment`
Contains Docker and deployment configuration files.
- `Dockerfile` - Container definition
- `docker-compose.yml` - Development container orchestration
- `docker-compose.prod.yml` - Production container orchestration

### `/docs`
Documentation and guides for the project.
- `SETUP.md` - Setup instructions
- `FACEBOOK_SETUP_FIX.md` - Facebook integration guide
- `Epic4_Complete_Summary.md` - Documentation for Epic 4
- `Epic5_Complete_Summary.md` - Documentation for Epic 5

### `/frontend`
Frontend assets and JavaScript files.
- `dashboard.js` - Dashboard UI functionality

### `/logs`
Application logs.
- `worker.log` - Worker process logs

### `/scripts`
Utility and automation scripts.
- `demo_*.py` - Demo scripts
- `run_worker.py` - Script to run worker process
- `setup_env.py` - Environment setup script
- `quick_start.sh` - Quick start script

### `/src`
Main source code directory, organized by functionality.
- `/analysis` - Content analysis modules
- `/notifications` - Notification system
- `/scrapers` - Data scraping modules for Yad2 and Facebook
- `/search` - Search functionality
- `/telegram` - Telegram integration
- `/telegram_bot` - Telegram bot implementation
- `/web` - Web server and dashboard

### `/tests`
Test suites organized by test type.
- `/epic_tests` - Tests for project epics
- `/integration` - Integration tests
- `/system` - System tests
- `/unit` - Unit tests

## File Locations

- Python package configuration: `pyproject.toml` and `requirements.txt` in the root directory
- Test configuration: `pytest.ini` in the root directory
- Main README: `README.md` in the root directory
