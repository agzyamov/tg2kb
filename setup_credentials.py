#!/usr/bin/env python3
"""
Helper script to set up Telegram API credentials in .env file.
This script safely updates the .env file with your actual credentials.
"""

import os
import re
from pathlib import Path
from typing import Optional

def update_env_file(api_id: str, api_hash: str, openai_key: Optional[str] = None):
    """
    Update the .env file with provided credentials.
    
    Args:
        api_id: Telegram API ID
        api_hash: Telegram API Hash
        openai_key: OpenAI API key (optional)
    """
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found. Please run 'cp config.example.env .env' first.")
        return False
    
    # Read current .env file
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Update Telegram credentials
    content = re.sub(
        r'TELEGRAM_API_ID=.*',
        f'TELEGRAM_API_ID={api_id}',
        content
    )
    content = re.sub(
        r'TELEGRAM_API_HASH=.*',
        f'TELEGRAM_API_HASH={api_hash}',
        content
    )
    
    # Update OpenAI key if provided
    if openai_key:
        content = re.sub(
            r'OPENAI_API_KEY=.*',
            f'OPENAI_API_KEY={openai_key}',
            content
        )
    
    # Write updated content
    with open(env_path, 'w') as f:
        f.write(content)
    
    print("✅ Credentials updated in .env file")
    return True

def main():
    print("🔐 Telegram API Credentials Setup")
    print("=" * 40)
    print()
    print("To get your credentials:")
    print("1. Go to https://my.telegram.org")
    print("2. Log in with your phone number")
    print("3. Click 'API development tools'")
    print("4. Create a new application")
    print("5. Copy your api_id and api_hash")
    print()
    
    # Get credentials from user
    api_id = input("Enter your Telegram API ID: ").strip()
    api_hash = input("Enter your Telegram API Hash: ").strip()
    
    if not api_id or not api_hash:
        print("❌ Both API ID and API Hash are required")
        return
    
    # Optional OpenAI key
    openai_key = input("Enter your OpenAI API Key (optional, press Enter to skip): ").strip()
    if not openai_key:
        openai_key = None
    
    # Update .env file
    if update_env_file(api_id, api_hash, openai_key):
        print()
        print("🎉 Setup complete! You can now run:")
        print("   python tg_client.py")
        print()
        print("⚠️  Remember: The .env file is gitignored for security")

if __name__ == "__main__":
    main() 