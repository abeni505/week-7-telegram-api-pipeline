# This new script loads the raw JSON files from the data lake into PostgreSQL.

import os
import json
import logging
import psycopg2
import time
from psycopg2.extras import Json

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Database Configuration ---
# These are read from the environment variables set in docker-compose.yml
DB_NAME = os.getenv("POSTGRES_DB", "mydatabase")
DB_USER = os.getenv("POSTGRES_USER", "myadmin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mysecretpassword")
DB_HOST = os.getenv("POSTGRES_HOST", "db") # 'db' is the service name in docker-compose
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATA_LAKE_PATH = 'data/raw/telegram_messages'

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            logging.info("Successfully connected to PostgreSQL database.")
            return conn
        except psycopg2.OperationalError as e:
            logging.error(f"Could not connect to database: {e}. Retrying in 5 seconds...")
            retries -= 1
            time.sleep(5)
    return None

def load_data_to_postgres():
    """
    Loads raw JSON data from the data lake into a 'raw_messages' table
    in the 'raw' schema of the PostgreSQL database.
    """
    conn = get_db_connection()
    if not conn:
        logging.critical("Failed to connect to the database after several retries. Aborting.")
        return

    try:
        with conn.cursor() as cur:
            # Create a schema for our raw data if it doesn't exist
            cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
            # Create the table to hold the raw JSON data
            cur.execute("""
                CREATE TABLE IF NOT EXISTS raw.raw_messages (
                    id SERIAL PRIMARY KEY,
                    channel_name VARCHAR(255),
                    message_data JSONB,
                    loaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            logging.info("Schema 'raw' and table 'raw_messages' are ready.")

            # --- NEW: Truncate the table to avoid duplicate data on re-runs ---
            logging.info("Truncating raw.raw_messages to prepare for new data load.")
            cur.execute("TRUNCATE TABLE raw.raw_messages RESTART IDENTITY;")


            # Iterate through the partitioned data lake directories
            if not os.path.exists(DATA_LAKE_PATH):
                logging.warning(f"Data lake path not found: {DATA_LAKE_PATH}. Skipping data loading.")
                return
                
            for date_folder in os.listdir(DATA_LAKE_PATH):
                date_path = os.path.join(DATA_LAKE_PATH, date_folder)
                if not os.path.isdir(date_path):
                    continue

                for json_file in os.listdir(date_path):
                    if not json_file.endswith('.json'):
                        continue
                    
                    channel_name = json_file.replace('.json', '')
                    file_path = os.path.join(date_path, json_file)

                    with open(file_path, 'r', encoding='utf-8') as f:
                        messages = json.load(f)
                        for message in messages:
                            # Insert each message as a new row with its JSON content
                            cur.execute(
                                "INSERT INTO raw.raw_messages (channel_name, message_data) VALUES (%s, %s);",
                                (channel_name, Json(message))
                            )
        
            conn.commit()
            logging.info("Successfully loaded all JSON files into raw.raw_messages.")

    except Exception as e:
        logging.error(f"An error occurred during data loading: {e}")
        conn.rollback()
    finally:
        conn.close()
        logging.info("Database connection closed.")
