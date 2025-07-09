#!/usr/bin/env python3
"""
Environment Setup Helper for RealtyScanner Agent
Generates secure keys and validates environment configuration
"""

import secrets
import sys
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key for JWT tokens"""
    return secrets.token_urlsafe(32)

def generate_encryption_key():
    """Generate encryption key for Facebook cookies"""
    return secrets.token_urlsafe(32)

def create_env_file():
    """Create .env file from template with generated keys"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ .env.example file not found!")
        return False
    
    if env_file.exists():
        response = input("📁 .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("✅ Keeping existing .env file")
            return True
    
    # Read template
    with open(env_example, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Generate secure keys
    secret_key = generate_secret_key()
    encryption_key = generate_encryption_key()
    dashboard_key = generate_secret_key()
    
    # Replace placeholder values
    content = content.replace(
        "SECRET_KEY=your-secret-key-change-this-to-a-random-string",
        f"SECRET_KEY={secret_key}"
    )
    content = content.replace(
        "FACEBOOK_SESSION_ENCRYPTION_KEY=your_encryption_key_here",
        f"FACEBOOK_SESSION_ENCRYPTION_KEY={encryption_key}"
    )
    content = content.replace(
        "DASHBOARD_SECRET_KEY=your_secret_key_for_dashboard_sessions",
        f"DASHBOARD_SECRET_KEY={dashboard_key}"
    )
    
    # Write .env file
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Created .env file with generated secret keys")
    print(f"🔑 Generated SECRET_KEY: {secret_key[:10]}...")
    print(f"🔑 Generated ENCRYPTION_KEY: {encryption_key[:10]}...")
    print(f"🔑 Generated DASHBOARD_KEY: {dashboard_key[:10]}...")
    
    return True

def validate_required_env():
    """Check for required environment variables"""
    required_vars = [
        "SECRET_KEY",
        "MONGODB_URI", 
        "TELEGRAM_BOT_TOKEN"
    ]
    
    missing = []
    
    if not Path(".env").exists():
        print("❌ .env file not found! Run this script first to create it.")
        return False
    
    # Load .env file manually for validation
    env_vars = {}
    with open(".env", 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                env_vars[key] = value
    
    for var in required_vars:
        if var not in env_vars or env_vars[var].startswith('your_'):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("\n📝 Please edit .env file and set:")
        for var in missing:
            if var == "TELEGRAM_BOT_TOKEN":
                print(f"   {var}=<get from @BotFather on Telegram>")
            elif var == "MONGODB_URI":
                print(f"   {var}=mongodb://localhost:27017 (or your MongoDB Atlas URI)")
            else:
                print(f"   {var}=<your value here>")
        return False
    
    print("✅ All required environment variables are configured")
    return True

def main():
    print("🏠 RealtyScanner Environment Setup")
    print("=" * 40)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    print("\n📋 Next Steps:")
    print("1. Edit .env file with your actual API keys:")
    print("   - TELEGRAM_BOT_TOKEN (required)")
    print("   - MONGODB_URI (required)")
    print("   - Other API keys (optional)")
    print("\n2. Run validation:")
    print("   python scripts/setup_env.py --validate")
    print("\n3. Test the setup:")
    print("   python scripts/test_complete_flow.py")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--validate":
        if validate_required_env():
            print("🚀 Environment is ready!")
        else:
            print("💡 Fix the issues above and run validation again")
            sys.exit(1)
    else:
        main()
