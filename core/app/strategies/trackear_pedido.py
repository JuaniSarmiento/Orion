"""
TrackearPedidoStrategy - Order Tracking Intent Handler
========================================================
Concrete strategy implementation for handling order tracking requests.

This strategy processes tracking number queries, communicating with the
INTEGRATIONS service to retrieve real-time shipment status information
from logistics systems.
"""

import httpx
from typing import List, Dict, Any
from strategies.base import IntentStrategy


class TrackearPedidoStrategy(IntentStrategy):
    """
    Strategy for handling order tracking requests.
    
    This strategy extracts tracking numbers from user queries and retrieves
    shipment status information from the INTEGRATIONS service, which acts as
    an abstraction layer for logistics APIs (Andreani, OCA, Correo Argentino).
    
    Flow:
        1. Extract tracking number from entities
        2. Validate tracking number is present
        3. Query INTEGRATIONS service logistics endpoint
        4. Parse tracking data and format user-friendly response
        5. Handle errors (404, timeout, connection issues)
    
    Expected Entities:
        - numero_pedido: The tracking number to query
    
    Integration:
        - Endpoint: GET http://integrations:8000/logistics/tracking/{tracking_id}
        - Timeout: 10 seconds
        - Handles: 200 (success), 404 (not found), connection errors
    """
    
    async def execute(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute the order tracking strategy.
        
        Extracts the tracking number from entities, calls the INTEGRATIONS
        service logistics endpoint, and returns formatted tracking information
        to the user.
        
        Args:
            entities (List[Dict[str, Any]]): List of extracted entities from NLU.
                Expected format: [{"label": "numero_pedido", "value": "481516"}]
        
        Returns:
            Dict[str, Any]: Strategy execution result with tracking information.
            
        Success Response (200):
            {
                "status": "success",
                "message": "Tu pedido está 'En camino'. Se encuentra en Buenos Aires...",
                "details": {
                    "intent": "trackear_pedido",
                    "tracking_id": "481516",
                    "carrier": "Andreani",
                    "status": "in_transit",
                    "estimated_delivery": "2025-10-18T18:00:00Z",
                    "current_location": {...},
                    "history": [...]
                }
            }
            
        Error Response (404):
            {
                "status": "error",
                "message": "No pudimos encontrar información para ese número de seguimiento...",
                "details": {
                    "intent": "trackear_pedido",
                    "tracking_id": "99999"
                }
            }
        """
        # Extract tracking number from entities
        # Priority 1: Look for complex tracking_id (e.g., TRK-delivered-123)
        # Priority 2: Fall back to simple numero_pedido (e.g., 481516)
        numero_pedido = None
        
        for entity in entities:
            if entity.get("label") == "tracking_id":
                numero_pedido = entity.get("value")
                break
        
        # Fallback to numero_pedido if tracking_id not found
        if not numero_pedido:
            for entity in entities:
                if entity.get("label") == "numero_pedido":
                    numero_pedido = entity.get("value")
                    break
        
        if not numero_pedido:
            return {
                "status": "error",
                "message": "No pude identificar el número de pedido en tu consulta. Por favor, proporciona un número de seguimiento válido.",
                "details": {
                    "intent": "trackear_pedido",
                    "missing_entity": "numero_pedido"
                }
            }
        
        # Call INTEGRATIONS service logistics endpoint
        integrations_url = f"http://integrations:8000/logistics/tracking/{numero_pedido}"
        print(f"🔗 Llamando a INTEGRATIONS: {integrations_url}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(integrations_url)
                
                # Handle successful response (200 OK)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Tracking encontrado: {data['status']}")
                    
                    # Format user-friendly message based on tracking data
                    status_label = data.get("status_label", "desconocido")
                    city = data.get("current_location", {}).get("city", "ubicación desconocida")
                    estimated_date = data.get("estimated_delivery_date", "fecha no disponible")
                    carrier = data.get("carrier", "transportista")
                    
                    # Build contextual message based on status
                    if data.get("status") == "delivered":
                        delivered_at = data.get("delivery_confirmation", {}).get("delivered_at", "")
                        received_by = data.get("delivery_confirmation", {}).get("received_by", "destinatario")
                        message = f"¡Buenas noticias! Tu pedido ya fue entregado. Recibido por {received_by} el {delivered_at[:10]}."
                        
                    elif data.get("status") == "failed_delivery":
                        reason = data.get("failure_reason", "motivo desconocido")
                        next_attempt = data.get("next_attempt", "próximamente")
                        message = f"Hubo un intento de entrega fallido ({reason}). El próximo intento será el {next_attempt[:10]}."
                        
                    else:
                        # Default message for in_transit and other statuses
                        message = f"Tu pedido está '{status_label}'. Se encuentra en {city} y la fecha estimada de entrega es {estimated_date[:10]}."
                    
                    # Get last movement from history
                    last_movement = "Sin información de movimientos"
                    if data.get("history") and len(data["history"]) > 0:
                        latest = data["history"][0]
                        last_movement = f"{latest.get('description', 'N/A')} - {latest.get('location', 'N/A')}"
                    
                    return {
                        "status": "success",
                        "message": message,
                        "details": {
                            "intent": "trackear_pedido",
                            "tracking_id": numero_pedido,
                            "carrier": carrier,
                            "status": data.get("status"),
                            "status_label": status_label,
                            "estimated_delivery": estimated_date,
                            "current_location": data.get("current_location"),
                            "last_movement": last_movement,
                            "history": data.get("history", [])
                        }
                    }
                
                # Handle tracking not found (404)
                elif response.status_code == 404:
                    error_data = response.json()
                    print(f"❌ Tracking no encontrado: {numero_pedido}")
                    
                    return {
                        "status": "error",
                        "message": "No pudimos encontrar información para ese número de seguimiento. Por favor, verifica que sea correcto o contacta al remitente.",
                        "details": {
                            "intent": "trackear_pedido",
                            "tracking_id": numero_pedido,
                            "error": error_data.get("error", "Tracking not found")
                        }
                    }
                
                # Handle other HTTP errors
                else:
                    print(f"⚠️ Error HTTP {response.status_code} desde INTEGRATIONS")
                    
                    return {
                        "status": "error",
                        "message": f"Error al consultar el seguimiento del pedido. Código: {response.status_code}",
                        "details": {
                            "intent": "trackear_pedido",
                            "tracking_id": numero_pedido,
                            "http_status": response.status_code
                        }
                    }
        
        except httpx.TimeoutException:
            print(f"⏱️ Timeout al consultar tracking para {numero_pedido}")
            
            return {
                "status": "error",
                "message": "La consulta de seguimiento tardó demasiado. Por favor, intenta nuevamente en unos momentos.",
                "details": {
                    "intent": "trackear_pedido",
                    "tracking_id": numero_pedido,
                    "error": "timeout"
                }
            }
        
        except httpx.RequestError as e:
            print(f"🔌 Error de conexión con INTEGRATIONS: {str(e)}")
            
            return {
                "status": "error",
                "message": "No pudimos conectar con el servicio de seguimiento. Por favor, intenta más tarde.",
                "details": {
                    "intent": "trackear_pedido",
                    "tracking_id": numero_pedido,
                    "error": "connection_error"
                }
            }

