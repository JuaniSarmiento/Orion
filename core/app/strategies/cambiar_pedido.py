"""
Strategy: Cambiar Pedido (Modify/Cancel Order)
==============================================
Handles order modification or cancellation requests.
"""

from .base import IntentStrategy


class CambiarPedidoStrategy(IntentStrategy):
    """
    Strategy for handling order modifications and cancellations.
    
    This strategy guides users through the order change/cancellation process.
    """
    
    async def execute(self, entities: list) -> dict:
        """
        Execute order modification strategy.
        
        Args:
            entities (list): List of extracted entities.
            
        Returns:
            dict: Execution result with modification instructions.
        """
        pedido_id = None
        
        # Extract order ID if present
        for entity in entities:
            if entity.get("label") in ["numero_pedido", "tracking_id"]:
                pedido_id = entity.get("value")
                break
        
        if pedido_id:
            return {
                "status": "info",
                "action": f"Para modificar o cancelar el pedido #{pedido_id}, comunícate con nuestro equipo de atención al cliente al 0800-XXX-XXXX. Las modificaciones dependen del estado actual del envío.",
                "details": {
                    "intent": "cambiar_pedido",
                    "pedido_id": pedido_id,
                    "contact": "0800-XXX-XXXX"
                }
            }
        else:
            return {
                "status": "info",
                "action": "Para modificar o cancelar un pedido, necesitamos tu número de orden. ¿Podrías proporcionárnoslo?",
                "details": {
                    "intent": "cambiar_pedido",
                    "message": "Número de pedido requerido"
                }
            }
