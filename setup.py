#!/usr/bin/env python3
"""
Pu_Sok - Telegram Security Guard Bot
A strict but funny security guard at UYFC-PV, Prey Veng

This script sets up the bot for deployment on Render.com
Run this once before deploying
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_setup():
    """Check if bot is properly configured"""
    print("=" * 60)
    print("🔍 Checking Pu_Sok Bot Setup...")
    print("=" * 60)
    
    errors = []
    
    # Check BOT_TOKEN
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token or bot_token == 'your_bot_token_here_from_botfather':
        errors.append("❌ BOT_TOKEN not configured in .env")
    else:
        print(f"✅ BOT_TOKEN: Configured (token length: {len(bot_token)})")
    
    # Check SPECIFIC_ADMIN_ID
    admin_id = os.getenv('SPECIFIC_ADMIN_ID')
    if not admin_id or admin_id == '0':
        print("⚠️  SPECIFIC_ADMIN_ID: Not set (optional, but recommended)")
    else:
        print(f"✅ SPECIFIC_ADMIN_ID: {admin_id}")
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    required_packages = ['telebot', 'dotenv']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: installed")
        except ImportError:
            errors.append(f"❌ {package} not installed. Run: pip install -r requirements.txt")
    
    print("\n" + "=" * 60)
    if errors:
        print("⚠️  SETUP ISSUES:")
        for error in errors:
            print(f"  {error}")
        print("=" * 60)
        return False
    else:
        print("✅ Bot is ready! Run: python bot.py")
        print("=" * 60)
        return True


if __name__ == "__main__":
    if not check_setup():
        sys.exit(1)
