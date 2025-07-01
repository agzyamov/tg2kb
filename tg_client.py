"""
Telegram client module using Telethon library.

Provides functionality to connect to Telegram, list channels,
select a channel, and download messages for processing.

TODO: Implement Telethon client connection
TODO: Add session management for persistent login
TODO: Add channel listing functionality
TODO: Add interactive channel selection
TODO: Add message downloading with pagination
TODO: Add JSON export functionality
TODO: Add error handling for network issues
TODO: Add rate limiting to avoid API restrictions
TODO: Add progress reporting for large downloads
TODO: Add message filtering options
"""

import os
import json
import asyncio
from typing import List, Dict, Optional
from pathlib import Path
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_telegram_credentials() -> tuple[str, str]:
    """
    Get Telegram API credentials from environment variables.
    
    Returns:
        Tuple of (api_id, api_hash)
        
    Raises:
        ValueError: If credentials are not found
    """
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    if not api_id or not api_hash:
        raise ValueError(
            "Telegram credentials not found. Please set TELEGRAM_API_ID and "
            "TELEGRAM_API_HASH in your .env file or environment variables."
        )
    
    return api_id, api_hash


def get_session_name() -> str:
    """
    Get Telegram session name from environment or use default.
    
    Returns:
        Session name for Telegram client
    """
    return os.getenv('TELEGRAM_SESSION_NAME', 'tg2kb_session')


async def connect_telethon(api_id: str, api_hash: str) -> Optional[TelegramClient]:
    """
    Establish connection to Telegram using Telethon.
    
    Args:
        api_id: Telegram API ID from https://my.telegram.org
        api_hash: Telegram API Hash from https://my.telegram.org
        
    Returns:
        Connected TelegramClient instance
    """
    session_name = get_session_name()
    client = TelegramClient(session_name, int(api_id), api_hash)
    
    try:
        await client.connect()
        
        # Check if already authorized
        if not await client.is_user_authorized():
            print("First time login required. Please follow the prompts:")
            phone = input("Enter your phone number (with country code, e.g., +1234567890): ")
            await client.send_code_request(phone)
            
            try:
                code = input("Enter the verification code sent to your phone: ")
                await client.sign_in(phone, code)
            except PhoneCodeInvalidError:
                print("Invalid code. Please try again.")
                return None
            except SessionPasswordNeededError:
                password = input("Enter your 2FA password: ")
                await client.sign_in(password=password)
        
        print("✅ Successfully connected to Telegram!")
        return client
        
    except Exception as e:
        print(f"❌ Failed to connect to Telegram: {e}")
        return None


async def get_user_channels(client: TelegramClient) -> List[Dict]:
    """
    Get list of user's joined channels and groups.
    
    Args:
        client: Connected TelegramClient instance
        
    Returns:
        List of channel dictionaries with title and ID
    """
    channels = []
    
    try:
        async for dialog in client.iter_dialogs():
            if isinstance(dialog.entity, (Channel, Chat)) and not isinstance(dialog.entity, User):
                channel_info = {
                    'id': dialog.entity.id,
                    'title': dialog.title,
                    'type': 'channel' if isinstance(dialog.entity, Channel) else 'group',
                    'participants_count': getattr(dialog.entity, 'participants_count', None)
                }
                channels.append(channel_info)
        
        print(f"📋 Found {len(channels)} channels/groups")
        return channels
        
    except Exception as e:
        print(f"❌ Error fetching channels: {e}")
        return []


def select_channel(channels: List[Dict]) -> Dict:
    """
    Interactive CLI prompt to select a channel from the list.
    
    Args:
        channels: List of channel dictionaries from get_user_channels()
        
    Returns:
        Selected channel dictionary
    """
    if not channels:
        print("❌ No channels found")
        return {}
    
    print("\n📺 Available channels:")
    for i, channel in enumerate(channels, 1):
        participants = channel.get('participants_count', 'N/A')
        print(f"{i:2d}. {channel['title']} ({channel['type']}, {participants} members)")
    
    while True:
        try:
            choice = input(f"\nSelect a channel (1-{len(channels)}): ")
            index = int(choice) - 1
            if 0 <= index < len(channels):
                selected = channels[index]
                print(f"✅ Selected: {selected['title']}")
                return selected
            else:
                print("❌ Invalid selection. Please try again.")
        except ValueError:
            print("❌ Please enter a valid number.")


async def download_messages(client: TelegramClient, channel_id: int, limit: int = 50) -> List[Dict]:
    """
    Download messages from the selected channel.
    
    Args:
        client: Connected TelegramClient instance
        channel_id: ID of the channel to download from
        limit: Maximum number of messages to download
        
    Returns:
        List of message dictionaries
    """
    messages = []
    
    try:
        print(f"📥 Downloading up to {limit} messages...")
        
        async for message in client.iter_messages(channel_id, limit=limit):
            if message.text:  # Only process text messages for now
                message_data = {
                    'id': message.id,
                    'type': 'message',
                    'date': message.date.isoformat(),
                    'from': message.sender.first_name if message.sender else 'Unknown',
                    'text': message.text,
                    'media_type': None,
                    'media_url': None
                }
                messages.append(message_data)
        
        print(f"✅ Downloaded {len(messages)} messages")
        return messages
        
    except Exception as e:
        print(f"❌ Error downloading messages: {e}")
        return []


def save_messages(messages: List[Dict], path: Path) -> None:
    """
    Save downloaded messages to JSON file.
    
    Args:
        messages: List of message dictionaries
        path: Path to save the JSON file
    """
    try:
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare export data
        export_data = {
            'name': 'Telegram Channel Export',
            'type': 'channel',
            'export_date': '2024-01-01T00:00:00Z',  # TODO: Use actual date
            'message_count': len(messages),
            'messages': messages
        }
        
        # Write to file
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Messages saved to {path}")
        
    except Exception as e:
        print(f"❌ Error saving messages: {e}")


async def main():
    """
    Main function to run the Telegram client workflow.
    """
    client = None
    try:
        print("🚀 Starting Telegram client...")
        
        # Get API credentials
        api_id, api_hash = get_telegram_credentials()
        print("✅ Credentials loaded")
        
        # Connect to Telegram
        client = await connect_telethon(api_id, api_hash)
        if not client:
            return
        
        # Get user channels
        channels = await get_user_channels(client)
        if not channels:
            print("❌ No channels found or error occurred")
            return
        
        # Let user select channel
        selected_channel = select_channel(channels)
        if not selected_channel:
            return
        
        # Download messages
        messages = await download_messages(client, selected_channel['id'])
        if not messages:
            print("❌ No messages downloaded")
            return
        
        # Save to file
        output_path = Path('examples/raw_dump.json')
        save_messages(messages, output_path)
        
        print(f"\n🎉 Success! Downloaded {len(messages)} messages from '{selected_channel['title']}'")
        print(f"📁 Output saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error in main workflow: {e}")
    finally:
        # Disconnect client
        if client is not None:
            try:
                await client.disconnect()
            except Exception:
                pass  # Ignore disconnect errors


if __name__ == "__main__":
    asyncio.run(main()) 