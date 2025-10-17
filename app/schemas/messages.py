"""
Message Schemas
===============
Pydantic schemas for message data validation and serialization.

This module defines the data models for incoming and outgoing messages
in the ORION API Gateway.
"""

from pydantic import BaseModel


class IncomingMessage(BaseModel):
    """
    Schema for incoming webhook messages.
    
    This schema defines the structure and validates all incoming messages
    received through the /webhook/message endpoint. It ensures that all
    required fields are present and of the correct type.
    
    Attributes:
        channel (str): The communication channel (e.g., 'whatsapp', 'telegram').
        user_id (str): Unique identifier for the user sending the message.
        text (str): The actual text content of the message.
        
    Example:
        {
            "channel": "whatsapp",
            "user_id": "549112345678",
            "text": "Hello, ORION!"
        }
    """
    channel: str
    user_id: str
    text: str
