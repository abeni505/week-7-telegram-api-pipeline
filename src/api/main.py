# src/api/main.py

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas
from .database import SessionLocal, engine

# This line is commented out because dbt is responsible for creating tables.
# The API should only read from them, not create them.
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- Dependency ---
# This function provides a database session to the API endpoints.
# It ensures that the database session is always closed after the request
# is finished, even if there was an error.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

@app.get("/")
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the Telegram Analytics API"}


@app.get("/api/search/messages", response_model=List[schemas.Message])
def search_for_messages(query: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Searches for messages containing a specific query string.
    
    - **query**: The keyword to search for in message text.
    - **skip**: Number of records to skip for pagination.
    - **limit**: Maximum number of records to return.
    """
    messages = crud.search_messages(db, query=query, skip=skip, limit=limit)
    return messages


@app.get("/api/channels/{channel_name}/activity", response_model=schemas.ChannelActivity)
def get_channel_activity_report(channel_name: str, db: Session = Depends(get_db)):
    """
    Provides a report on the activity of a specific channel, including the
    total number of messages.
    
    - **channel_name**: The name of the channel to retrieve activity for.
    """
    activity = crud.get_channel_activity(db, channel_name=channel_name)
    if not activity:
        raise HTTPException(status_code=404, detail="Channel not found")
    return schemas.ChannelActivity(channel_name=activity.channel_name, total_messages=activity.total_messages)


@app.get("/api/reports/top-products", response_model=List[schemas.TopProduct])
def get_top_products_report(limit: int = 10, db: Session = Depends(get_db)):
    """
    Returns a list of the most frequently mentioned products across all channels.
    
    - **limit**: The maximum number of top products to return.
    """
    top_products = crud.get_top_products(db, limit=limit)
    # --- FIX: Access dictionary items using square brackets ---
    # The crud function returns a list of dictionaries, so we need to use
    # key-based access (e.g., p['product_name']) instead of attribute-based
    # access (p.product_name).
    return [schemas.TopProduct(product_name=p['product_name'], mention_count=p['mention_count']) for p in top_products]

