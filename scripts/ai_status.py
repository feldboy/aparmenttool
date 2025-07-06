#!/usr/bin/env python3
"""
AI Agents Simple Demo
Simple demonstration of AI agents integration
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_ai_integration():
    """Check if AI integration is working"""
    print("🤖 Checking AI Integration...")
    print("=" * 40)
    
    try:
        # Test AI agents import
        from ai_agents import AIAgentManager
        print("✅ AI Agents module imported successfully")
        
        # Initialize manager
        ai_manager = AIAgentManager()
        print(f"✅ AI Manager initialized with {len(ai_manager.enabled_providers)} providers")
        
        if ai_manager.enabled_providers:
            print("📋 Available providers:")
            for provider in ai_manager.enabled_providers:
                print(f"   - {provider.value}")
        else:
            print("⚠️  No AI providers configured (missing API keys)")
            print("💡 To enable AI providers, add these to your .env file:")
            print("   OPENAI_API_KEY=sk-your-openai-key")
            print("   GOOGLE_API_KEY=your-google-key")
            print("   ANTHROPIC_API_KEY=sk-ant-your-anthropic-key")
            print("   DEEPSEEK_API_KEY=your-deepseek-key")
        
        # Test content analyzer
        from analysis.content import ContentAnalyzer
        analyzer = ContentAnalyzer()
        print(f"✅ Content Analyzer initialized")
        print(f"🔍 AI Analysis: {'Enabled' if analyzer.use_ai_analysis else 'Disabled'}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_ai_configuration():
    """Show current AI configuration"""
    print("\n🔧 AI Configuration:")
    print("=" * 40)
    
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    ai_configs = {
        'OpenAI': {
            'key': os.getenv('OPENAI_API_KEY', 'Not set'),
            'model': os.getenv('OPENAI_MODEL', 'gpt-4o')
        },
        'Google': {
            'key': os.getenv('GOOGLE_API_KEY', 'Not set'),
            'model': os.getenv('GOOGLE_MODEL', 'gemini-pro')
        },
        'Anthropic': {
            'key': os.getenv('ANTHROPIC_API_KEY', 'Not set'),
            'model': os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
        },
        'DeepSeek': {
            'key': os.getenv('DEEPSEEK_API_KEY', 'Not set'),
            'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        }
    }
    
    for provider, config in ai_configs.items():
        key_status = "✅ Set" if (config['key'] != 'Not set' and 
                                  not config['key'].startswith('your_') and 
                                  not config['key'].startswith('sk-your') and
                                  not config['key'].endswith('_here')) else "❌ Not set"
        print(f"{provider}:")
        print(f"  API Key: {key_status}")
        print(f"  Model: {config['model']}")
        print()

def show_integration_features():
    """Show AI integration features"""
    print("🎯 AI Integration Features:")
    print("=" * 40)
    print("✅ Multi-provider AI analysis")
    print("✅ Consensus scoring from multiple AI models")
    print("✅ Enhanced property extraction (location, price, rooms)")
    print("✅ AI-powered content analysis")
    print("✅ Automatic fallback to rule-based analysis")
    print("✅ Performance metrics tracking")
    print("✅ Configurable AI settings")
    print()
    
    print("🔧 Supported AI Providers:")
    print("  - OpenAI (GPT-4, GPT-3.5)")
    print("  - Google AI (Gemini Pro)")
    print("  - Anthropic (Claude 3.5 Sonnet)")
    print("  - DeepSeek (DeepSeek Chat)")
    print()
    
    print("💡 Integration Points:")
    print("  - Content Analyzer: Enhanced property analysis")
    print("  - Background Worker: AI-powered listing processing")
    print("  - Web Dashboard: AI insights display")
    print("  - Real-time Analysis: Live property evaluation")

def main():
    """Main function"""
    print("🏠 RealtyScanner AI Integration Status")
    print("=" * 50)
    
    # Check integration
    if check_ai_integration():
        print("\n✅ AI Integration is working!")
    else:
        print("\n❌ AI Integration has issues")
    
    # Show configuration
    show_ai_configuration()
    
    # Show features
    show_integration_features()
    
    print("📝 Next Steps:")
    print("1. Add AI provider API keys to .env file")
    print("2. Restart services: python start_services.py")
    print("3. Check logs for AI analysis activity")
    print("4. Test with: python scripts/demo_ai_agents.py")

if __name__ == "__main__":
    main()
