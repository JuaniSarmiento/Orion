"""
Strategy: Consultar Precio (Price Inquiry)
===========================================
Handles user queries about product prices.
"""

from .base import IntentStrategy


class ConsultarPrecioStrategy(IntentStrategy):
    """
    Strategy for handling price inquiries.
    
    This strategy responds to user questions about product pricing.
    In a real implementation, this would query a pricing database or API.
    """
    
    async def execute(self, entities: list) -> dict:
        """
        Execute price inquiry strategy.
        
        Args:
            entities (list): List of extracted entities.
            
        Returns:
            dict: Execution result with price information or guidance.
        """
        producto = None
        
        # Extract product entity if present
        for entity in entities:
            if entity.get("label") == "producto":
                producto = entity.get("value")
                break
        
        if producto:
            # In production: Query pricing database
            return {
                "status": "info",
                "action": f"Para consultar el precio de '{producto}', por favor visita nuestro catálogo en línea o contacta a ventas.",
                "details": {
                    "intent": "consultar_precio",
                    "producto": producto,
                    "message": "Esta funcionalidad estará disponible próximamente"
                }
            }
        else:
            return {
                "status": "info",
                "action": "Para consultar precios, visita nuestro catálogo en línea o especifica el producto que te interesa.",
                "details": {
                    "intent": "consultar_precio",
                    "message": "Necesitamos el nombre o código del producto"
                }
            }
