"""
Strategy: Agradecimiento (Thanks/Goodbye)
=========================================
Handles thank you messages and farewells.
"""

from .base import IntentStrategy


class AgradecimientoStrategy(IntentStrategy):
    """
    Strategy for handling thanks and goodbyes.
    
    Provides a polite closing message.
    """
    
    async def execute(self, entities: list) -> dict:
        """
        Execute thanks/goodbye strategy.
        
        Args:
            entities (list): List of extracted entities.
            
        Returns:
            dict: Execution result with farewell message.
        """
        return {
            "status": "success",
            "action": "¡De nada! 😊 Fue un placer ayudarte. Si necesitas algo más, no dudes en escribirnos. ¡Que tengas un excelente día!",
            "details": {
                "intent": "agradecimiento",
                "conversation_ended": True
            }
        }
