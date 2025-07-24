# src/api/models.py

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

SCHEMA_NAME = "public_marts"

class Channel(Base):
    """
    SQLAlchemy ORM model for the 'dim_channels' table.
    """
    __tablename__ = 'dim_channels'
    __table_args__ = {'schema': SCHEMA_NAME}

    # --- FIX: Change channel_key from Integer to String ---
    channel_key = Column(String, primary_key=True, index=True)
    channel_id = Column(Integer, unique=True, index=True)
    channel_name = Column(String, unique=True, index=True)
    
    messages = relationship("Message", back_populates="channel")


class Message(Base):
    """
    SQLAlchemy ORM model for the 'fct_messages' table.
    """
    __tablename__ = 'fct_messages'
    __table_args__ = {'schema': SCHEMA_NAME}

    # --- FIX: Change message_key from Integer to String ---
    message_key = Column(String, primary_key=True, index=True)
    message_id = Column(Integer, unique=True, index=True)
    # --- FIX: Change channel_key from Integer to String ---
    channel_key = Column(String, ForeignKey(f'{SCHEMA_NAME}.dim_channels.channel_key'))
    date_key = Column(Integer)
    message_text = Column(String)
    
    channel = relationship("Channel", back_populates="messages")

