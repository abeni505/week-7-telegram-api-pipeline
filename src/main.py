# src/main.py
import os
from dotenv import load_dotenv

load_dotenv()

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

print("✅ Task 0 setup complete: Successfully loaded secrets.")
print(f"Your Telegram API ID starts with: {api_id[:4]}...")