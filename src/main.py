# The main script is updated with simplified dbt commands.

import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from scraping.scraper import scrape_all_channels
from loading.loader import load_data_to_postgres

# Load environment variables
load_dotenv()
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

async def main():
    """
    Main function to run the full data pipeline.
    """
    print("🚀 Starting the data pipeline...")

    # # --- Task 1: Data Scraping (Commented out for faster testing) ---

    client = TelegramClient('anon', API_ID, API_HASH)
    async with client:
        me = await client.get_me()
        print(f"✅ Logged in as: {me.first_name}")
        print("--- Running Task 1: Data Scraping and Collection ---")
        await scrape_all_channels(client)
        print("✅ Task 1 complete.")


    # --- Task 2: Load to Warehouse & Transform ---
    print("--- Running Task 2: Data Modeling and Transformation ---")
    
    # Step 1: Load raw data from data lake to PostgreSQL
    print("Loading raw data into PostgreSQL...")
    load_data_to_postgres()
    print("✅ Raw data loaded.")

    # Step 2: Run dbt to transform the data
    print("Running dbt transformations...")
    # The --profiles-dir flag is no longer needed
    dbt_command = "dbt run --project-dir ./dbt_project"
    os.system(dbt_command)
    print("✅ dbt transformations complete.")

    # Step 3: Run dbt tests
    print("Running dbt tests...")
    dbt_test_command = "dbt test --project-dir ./dbt_project"
    os.system(dbt_test_command)
    print("✅ dbt tests complete.")

    print("✅ Task 2 complete.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred during the pipeline execution: {e}")
