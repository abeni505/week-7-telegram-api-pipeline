# This file contains all the logic for scraping Telegram channels.

import os
import json
import logging
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import Message
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

# List of channels to scrape
CHANNELS = ['ChemedHealth', 'lobelia4cosmetics', 'tikvahpharma']
DATA_LAKE_PATH = 'data/raw/telegram_messages'
IMAGE_PATH = 'data/raw/images'
SCRAPE_LIMIT = 100 # Limit the number of messages to scrape per channel

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def scrape_all_channels(client: TelegramClient):
    """
    Connects to Telegram and scrapes messages from the specified channels.

    Args:
        client (TelegramClient): An authenticated Telethon client instance.
    """
    logging.info("Starting channel scraping process...")
    for channel_name in CHANNELS:
        try:
            logging.info(f"--- Starting scrape for channel: {channel_name} ---")
            
            # Get the channel entity (metadata) from Telegram
            entity = await client.get_entity(channel_name)
            logging.info(f"Successfully got entity for '{channel_name}'. Now iterating messages.")

            messages_by_date = {}

            # Iterate through messages in the channel, up to the defined limit
            async for message in client.iter_messages(entity, limit=SCRAPE_LIMIT):
                # We only care about messages with text content
                if not isinstance(message, Message) or not message.text:
                    continue

                # Group messages by date to create partitioned files
                message_date_str = message.date.strftime('%Y-%m-%d')
                if message_date_str not in messages_by_date:
                    messages_by_date[message_date_str] = []

                # If the message has a photo, download it and record its path
                photo_filename = None
                if message.photo:
                    photo_dir = os.path.join(IMAGE_PATH, message_date_str, channel_name)
                    os.makedirs(photo_dir, exist_ok=True)
                    photo_filename = await client.download_media(message.photo, file=photo_dir)
                    logging.info(f"Downloaded photo to: {photo_filename}")

                # Create a dictionary with the relevant message data
                message_data = {
                    'id': message.id,
                    'date': message.date.isoformat(),
                    'text': message.text,
                    'sender_id': message.sender_id,
                    'photo_path': photo_filename
                }
                messages_by_date[message_date_str].append(message_data)

            # Save the grouped messages into partitioned JSON files
            for date_str, messages_list in messages_by_date.items():
                file_dir = os.path.join(DATA_LAKE_PATH, date_str)
                os.makedirs(file_dir, exist_ok=True)
                file_path = os.path.join(file_dir, f"{channel_name}.json")

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(messages_list, f, ensure_ascii=False, indent=4)
                logging.info(f"Saved {len(messages_list)} messages to {file_path}")

        except Exception as e:
            logging.error(f"Could not scrape channel '{channel_name}'. Reason: {e}")
            continue # Move to the next channel if an error occurs

        # Add a polite delay to avoid being rate-limited by Telegram
        logging.info(f"Finished scraping {channel_name}. Waiting for 15 seconds...")
        await asyncio.sleep(15)

    logging.info("--- All channels scraped successfully ---")

    