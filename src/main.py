 # The main script now handles the client connection explicitly.
import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from scraping.scraper import scrape_all_channels

# Load environment variables
load_dotenv()
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

async def main():
    """
    Main function to connect the client and run the pipeline steps.
    """
    print("🚀 Starting the data pipeline...")

    # The client is now created and connected here in main.
    # This makes the login prompt the very first step.
    client = TelegramClient('anon', API_ID, API_HASH)
    
    async with client:
        me = await client.get_me()
        print(f"✅ Successfully logged in as: {me.first_name}")

        # --- Task 1: Data Scraping ---
        print("--- Running Task 1: Data Scraping and Collection ---")
        await scrape_all_channels(client) # Pass the connected client to the scraper
        print("✅ Task 1 complete.")

if __name__ == "__main__":
    # The main entry point for the application.
    # This structure now forces the login prompt before anything else.
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred during the pipeline execution: {e}")
