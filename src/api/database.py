# src/api/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from the .env file in the project root
load_dotenv()

# --- Database Connection ---
# Construct the database URL from environment variables.
# This is a secure way to handle credentials and makes the app configurable.
DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', 5432)}"
    f"/{os.getenv('POSTGRES_DB')}"
)

# The engine is the entry point to the database. It manages connections.
# 'pool_pre_ping=True' checks connections for liveness before handing them out.
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
except Exception as e:
    print(f"Error creating database engine: {e}")
    # In a real app, you'd want more robust error handling or logging here.
    exit()


# A sessionmaker object is a factory for creating new Session objects.
# A Session is the primary interface for all database operations.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is a class that our ORM models will inherit from.
# It connects the model classes to the database tables.
Base = declarative_base()


# --- Dependency for FastAPI ---
def get_db():
    """
    This is a dependency function for FastAPI.
    It creates a new database session for each request and ensures it's
    closed correctly, even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
