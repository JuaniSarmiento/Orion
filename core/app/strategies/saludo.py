"""
Strategy: Saludo (Greeting)
============================
Handles friendly greetings from users.
"""

from .base import IntentStrategy


class SaludoStrategy(IntentStrategy):
    """
    Strategy for handling greetings.
    
    Provides a friendly welcome message and offers help.
    """
    
    async def execute(self, entities: list) -> dict:
        """
        Execute greeting strategy.
        
        Args:
            entities (list): List of extracted entities.
            
        Returns:
            dict: Execution result with friendly greeting.
        """
        return {
            "status": "success",
            "action": "¡Hola! 👋 Bienvenido a ORION. ¿En qué puedo ayudarte hoy? Puedo ayudarte con:\n• Rastrear pedidos 📦\n• Consultar stock 📊\n• Información de productos 🛍️",
            "details": {
                "intent": "saludo",
                "available_services": [
                    "Rastreo de pedidos",
                    "Consulta de stock",
                    "Información general"
                ]
            }
        }
