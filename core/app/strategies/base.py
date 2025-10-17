"""
Base Strategy
=============
Abstract base class for intent execution strategies.

This module defines the interface that all concrete strategy
classes must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IntentStrategy(ABC):
    """
    Abstract base class for intent execution strategies.
    
    All concrete strategy classes must inherit from this class and
    implement the execute method. This ensures a consistent interface
    across all intent handlers.
    
    The Strategy Pattern allows us to:
    - Separate business logic by intent
    - Add new intents without modifying existing code
    - Test each strategy in isolation
    - Maintain clean, organized code
    """
    
    @abstractmethod
    async def execute(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute the strategy's business logic asynchronously.
        
        This method must be implemented by all concrete strategy classes.
        It receives the entities extracted by the NLU service and returns
        a result dictionary with the execution outcome.
        
        Note: This method is async to support strategies that need to
        make HTTP calls to external services or perform other async operations.
        
        Args:
            entities (List[Dict[str, Any]]): List of entities extracted from
                the user's message. Each entity is a dictionary with 'label'
                and 'value' keys.
                
        Returns:
            Dict[str, Any]: A dictionary containing the execution result.
                Must include at least a 'status' key ('success' or 'error')
                and a 'message' key with details.
                
        Example:
            entities = [{"label": "numero_pedido", "value": "481516"}]
            result = await strategy.execute(entities)
            # result = {"status": "success", "message": "..."}
        """
        pass
