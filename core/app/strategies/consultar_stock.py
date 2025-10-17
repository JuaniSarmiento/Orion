"""
Consultar Stock Strategy
=========================
Strategy for handling stock consultation intent.

This strategy processes requests to check product availability by
extracting the product/order number from entities and querying the
integrations service for real stock information from Franco's inventory.
"""

import httpx
from typing import List, Dict, Any
from strategies.base import IntentStrategy


class ConsultarStockStrategy(IntentStrategy):
    """
    Strategy for consulting product stock availability.
    
    This strategy handles the 'consultar_stock' intent by:
    1. Extracting the product/order number from entities
    2. Validating that a number was provided
    3. Calling the INTEGRATIONS service to get stock information
    4. Returning structured data with the stock details
    
    The strategy communicates with the INTEGRATIONS service to obtain
    real-time inventory information from Franco's system.
    """
    
    async def execute(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute stock consultation strategy asynchronously.
        
        Searches for a product/order number entity in the provided entities list,
        queries the INTEGRATIONS service for stock information, and returns
        the results.
        
        Args:
            entities (List[Dict[str, Any]]): List of entities from NLU service.
                Expected to contain an entity with label 'numero_pedido'.
                
        Returns:
            Dict[str, Any]: Execution result with status and data.
                - On success: includes stock information from INTEGRATIONS
                - On error: indicates missing product number or API failure
                
        Examples:
            >>> strategy = ConsultarStockStrategy()
            >>> entities = [{"label": "numero_pedido", "value": "camiseta-titular"}]
            >>> result = await strategy.execute(entities)
            >>> print(result)
            {
                "status": "success",
                "message": "Stock disponible para el producto camiseta-titular.",
                "data": {
                    "product_id": "camiseta-titular",
                    "quantity": 10,
                    "status": "in_stock"
                }
            }
        """
        # Search for product/order number entity
        product_id = None
        
        for entity in entities:
            if entity.get("label") == "numero_pedido":
                product_id = entity.get("value")
                break
        
        # Validate that product ID was found
        if not product_id:
            # No product ID provided
            print(f"⚠️ Error: No se encontró identificador de producto en las entidades")
            
            return {
                "status": "error",
                "message": "No se proporcionó un identificador de producto.",
                "suggestion": "Por favor, indique el producto que desea consultar."
            }
        
        # Product ID found - query INTEGRATIONS service
        print(f"📦 Consultando stock para producto: {product_id}")
        print(f"🔄 Consultando servicio INTEGRATIONS...")
        
        try:
            # Call INTEGRATIONS service to get stock information
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://integrations:8000/stock/{product_id}",
                    timeout=10.0
                )
                
                # Check if request was successful
                if response.status_code == 200:
                    # Parse JSON response
                    data = response.json()
                    
                    print(f"✅ Respuesta recibida de INTEGRATIONS: {data}")
                    
                    # Build user-friendly message based on stock status
                    quantity = data.get("quantity", 0)
                    stock_status = data.get("status", "unknown")
                    
                    if quantity > 0:
                        message = f"¡Buenas noticias! Tenemos {quantity} unidades disponibles del producto {data['product_id']}."
                    else:
                        message = f"Lo sentimos, el producto {data['product_id']} no tiene stock disponible en este momento."
                    
                    # Return success with stock data
                    return {
                        "status": "success",
                        "message": message,
                        "data": data,
                        "product_id": data.get("product_id"),
                        "stock_quantity": quantity,
                        "stock_status": stock_status
                    }
                else:
                    # API returned non-200 status code
                    print(f"❌ Error al consultar INTEGRATIONS: Status {response.status_code}")
                    
                    return {
                        "status": "error",
                        "message": f"Error al consultar disponibilidad del producto. Código: {response.status_code}",
                        "product_id": product_id
                    }
                    
        except httpx.TimeoutException:
            # Request timeout
            print(f"⏱️ Timeout al consultar INTEGRATIONS service")
            
            return {
                "status": "error",
                "message": "Tiempo de espera agotado al consultar el sistema de inventario.",
                "product_id": product_id
            }
            
        except httpx.RequestError as e:
            # Connection error or other request issues
            print(f"❌ Error de conexión con INTEGRATIONS: {str(e)}")
            
            return {
                "status": "error",
                "message": "Error al conectar con el sistema de inventario. Por favor, intente más tarde.",
                "product_id": product_id,
                "error_details": str(e)
            }
