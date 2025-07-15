# This is a new, one-time script just for logging in.
import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

print("--- Telegram Login Script ---")
print("This script will log you in and create an 'anon.session' file.")

# Load environment variables
load_dotenv()
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

# We use the same session name 'anon' as in the main script
client = TelegramClient('anon', API_ID, API_HASH)

async def login():
    """Connects the client and creates the session file."""
    # The .start() method will handle the interactive login prompt.
    await client.start()
    me = await client.get_me()
    print(f"✅ Successfully logged in as {me.first_name} and created anon.session file.")
    await client.disconnect()

if __name__ == "__main__":
    # Run the login coroutine
    asyncio.run(login())