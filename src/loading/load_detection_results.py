# src/loading/load_detection_results.py

import os
import json
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv
import logging

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

# --- Paths ---
PROCESSED_DIR = 'data/processed/image_detections'
LOG_FILE = os.path.join(PROCESSED_DIR, 'loaded_files.log')

# --- Database Connection Details ---
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST', 'db') # 'db' is the service name in docker-compose
DB_PORT = os.getenv('POSTGRES_PORT', 5432)

# --- Schema and Table Names ---
SCHEMA_NAME = 'raw_data'
TABLE_NAME = 'image_detections'

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        logging.info("Database connection established successfully.")
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"Could not connect to the database: {e}")
        return None

def get_loaded_files():
    """Reads the log of already loaded files to prevent duplicates."""
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, 'r') as f:
        return set(f.read().splitlines())

def log_loaded_file(filename):
    """Adds a filename to the log of loaded files."""
    with open(LOG_FILE, 'a') as f:
        f.write(filename + '\n')

def load_data():
    """
    Main function to load new JSON detection results into the database.
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # 1. Create the schema if it doesn't exist
            logging.info(f"Ensuring schema '{SCHEMA_NAME}' exists.")
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME};")

            # 2. Create the table if it doesn't exist
            logging.info(f"Ensuring table '{SCHEMA_NAME}.{TABLE_NAME}' exists.")
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
                    id SERIAL PRIMARY KEY,
                    data JSONB,
                    loaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)

            # 3. Load new data
            loaded_files = get_loaded_files()
            files_to_load = [f for f in os.listdir(PROCESSED_DIR) if f.endswith('.json') and f not in loaded_files]

            if not files_to_load:
                logging.info("No new detection files to load.")
                return

            logging.info(f"Found {len(files_to_load)} new files to load.")
            for filename in files_to_load:
                filepath = os.path.join(PROCESSED_DIR, filename)
                with open(filepath, 'r') as f:
                    json_data = json.load(f)
                
                # Insert the JSON data into the table
                cur.execute(
                    f"INSERT INTO {SCHEMA_NAME}.{TABLE_NAME} (data) VALUES (%s);",
                    (Json(json_data),) # Use psycopg2.extras.Json to handle JSON correctly
                )
                log_loaded_file(filename)
                logging.info(f"Loaded data from {filename}.")

            conn.commit()
            logging.info("All new files loaded and committed successfully.")

    except Exception as e:
        logging.error(f"An error occurred during data loading: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")

if __name__ == '__main__':
    load_data()
