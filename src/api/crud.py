# src/api/crud.py

from sqlalchemy.orm import Session
from sqlalchemy import func, text
from . import models, schemas

# This file contains functions that directly interact with the database
# to read or write data.

def search_messages(db: Session, query: str, skip: int = 0, limit: int = 100):
    """
    Searches for messages containing a specific query string in their text.
    
    Args:
        db: The database session.
        query: The text to search for within messages.
        skip: The number of records to skip (for pagination).
        limit: The maximum number of records to return.
        
    Returns:
        A list of Message objects that match the query.
    """
    # Using 'ilike' for case-insensitive search
    return db.query(models.Message).filter(models.Message.message_text.ilike(f"%{query}%")).offset(skip).limit(limit).all()


def get_channel_activity(db: Session, channel_name: str):
    """
    Calculates the total number of messages for a specific channel.
    
    Args:
        db: The database session.
        channel_name: The name of the channel to analyze.
        
    Returns:
        A dictionary with channel name and total messages, or None if not found.
    """
    # This query joins the Message and Channel tables, filters by channel name,
    # and counts the resulting messages.
    activity = db.query(
        models.Channel.channel_name,
        func.count(models.Message.message_id).label('total_messages')
    ).join(models.Message, models.Channel.channel_key == models.Message.channel_key)\
     .filter(models.Channel.channel_name == channel_name)\
     .group_by(models.Channel.channel_name)\
     .first()
    
    return activity


def get_top_products(db: Session, limit: int = 10):
    """
    Finds the most frequently mentioned products across all messages by searching
    for a predefined list of keywords.
    """
    # In a real-world scenario, this list could come from a dedicated table or a config file.
    # We are expanding the list for a more realistic search.
    product_keywords = [
        "paracetamol", "amoxicillin", "vitamin c", "ibuprofen", "aspirin",
        "panadol", "augmentin", "ciprofloxacin", "metformin", "salbutamol",
        "diclofenac", "omeprazole", "azithromycin", "doxycycline", "prednisolone"
    ]
    
    mention_counts = []
    
    # This loop executes a separate query for each keyword.
    # While not the most performant on huge datasets, it's clear, robust,
    # and works well for this use case.
    for product in product_keywords:
        # Using f-string for the search term is safe here because it's not user input.
        # The query counts rows where the message_text contains the product keyword.
        count = db.query(func.count(models.Message.message_key))\
                  .filter(models.Message.message_text.ilike(f"%{product}%"))\
                  .scalar() # .scalar() returns a single value
        
        if count > 0:
            mention_counts.append({"product_name": product, "mention_count": count})
            
    # Sort the results by mention_count in descending order
    sorted_products = sorted(mention_counts, key=lambda x: x['mention_count'], reverse=True)
    
    # Return the top N results based on the limit
    return sorted_products[:limit]

