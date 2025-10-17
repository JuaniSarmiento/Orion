"""
NLU Schemas
===========
Pydantic schemas for NLU data structures.

This module defines the schemas for NLU responses received from
the NLU service, including intents and entities.
"""

from pydantic import BaseModel
from typing import List, Dict, Any


class Entity(BaseModel):
    """
    Schema for an individual entity extracted by NLU.
    
    Attributes:
        label (str): The type/category of the entity (e.g., 'numero_pedido').
        value (str): The actual value of the entity.
        
    Example:
        {
            "label": "numero_pedido",
            "value": "481516"
        }
    """
    label: str
    value: str


class NLUInput(BaseModel):
    """
    Schema for NLU service response data.
    
    This schema represents the processed output from the NLU service,
    containing the detected intent, extracted entities, original text,
    and user identification for tracking purposes.
    
    Attributes:
        intent (str): The detected user intent (e.g., 'trackear_pedido').
        entities (List[Entity]): List of entities extracted from the text.
        original_text (str): The original input text that was processed.
        channel_user_id (str): User identifier for conversation tracking.
        
    Example:
        {
            "intent": "trackear_pedido",
            "entities": [
                {"label": "numero_pedido", "value": "481516"}
            ],
            "original_text": "¿Dónde está mi pedido 481516?",
            "channel_user_id": "+5491112345678"
        }
    """
    intent: str
    entities: List[Entity]
    original_text: str
    channel_user_id: str = "unknown"  # Default for backwards compatibility


class ExecutionResponse(BaseModel):
    """
    Schema for execution response from CORE service.
    
    Attributes:
        status (str): Execution status ('success', 'error', etc.).
        action (str): Description of the action being executed.
        details (Dict[str, Any], optional): Additional execution details.
        
    Example:
        {
            "status": "success",
            "action": "Executing strategy for intent: trackear_pedido",
            "details": {}
        }
    """
    status: str
    action: str
    details: Dict[str, Any] = {}
