"""
INTEGRATIONS Service - External API Abstraction Layer
======================================================
Main entry point for the INTEGRATIONS microservice.

This service acts as an abstraction layer for all external API integrations,
providing a unified interface for the CORE service to interact with third-party
systems without needing to know their implementation details.
"""

from fastapi import FastAPI, Path
from fastapi.responses import JSONResponse
from datetime import datetime

# Initialize FastAPI application
app = FastAPI(
    title="ORION INTEGRATIONS Service",
    description="Abstraction layer for external API integrations (Inventory, Logistics, etc.)",
    version="1.0.0"
)


@app.get("/stock/{product_id}")
async def get_product_stock(
    product_id: str = Path(..., description="Unique identifier of the product")
):
    """
    Get product stock information from Franco's inventory system.
    
    This endpoint simulates Franco's inventory API, implementing the agreed
    contract for stock consultation. It provides realistic responses for
    both success and error scenarios.
    
    Contract Specification:
        - Success (200): Product found with stock information
        - Error (404): Product not found in inventory
    
    Args:
        product_id (str): The unique identifier of the product to query.
    
    Returns:
        JSONResponse: Product stock information or error message.
        
    Success Response (200):
        {
            "product_id": "camiseta-001",
            "sku": "SIM-PROD-001",
            "quantity": 15,
            "status": "in_stock",
            "last_updated": "2025-10-16T20:30:00Z"
        }
        
    Error Response (404):
        {
            "error": "Product not found",
            "product_id": "99999"
        }
        
    Status Values:
        - "in_stock": Product available with quantity > 0
        - "out_of_stock": Product not available (quantity = 0)
        - "low_stock": Product available but quantity < 5
    """
    # Log the stock check request
    print(f"📦 Consultando stock para producto: {product_id}")
    
    # Simulate error case: Product not found
    if product_id == "99999":
        print(f"❌ Producto {product_id} no encontrado en inventario")
        
        return JSONResponse(
            status_code=404,
            content={
                "error": "Product not found",
                "product_id": product_id
            }
        )
    
    # Success case: Product found
    # TODO: In production, call Franco's actual inventory API
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(f"{INVENTORY_API_URL}/products/{product_id}/stock")
    #     return response.json()
    
    # Simulate successful stock response
    stock_data = {
        "product_id": product_id,
        "sku": "SIM-PROD-001",
        "quantity": 15,
        "status": "in_stock",
        "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    print(f"✅ Stock encontrado: {stock_data}")
    
    return JSONResponse(
        status_code=200,
        content=stock_data
    )


@app.get("/logistics/tracking/{tracking_id}")
async def get_tracking_info(
    tracking_id: str = Path(..., description="Unique tracking identifier for the shipment")
):
    """
    Get shipment tracking information from logistics service.
    
    This endpoint simulates a logistics company API (Andreani, OCA, etc.),
    implementing the agreed contract for package tracking. It provides realistic
    responses based on the tracking ID pattern.
    
    Contract Specification:
        - Success (200): Tracking found with full shipment history
        - Error (404): Tracking ID not found
    
    Args:
        tracking_id (str): The unique tracking identifier to query.
    
    Returns:
        JSONResponse: Tracking information with history or error message.
        
    Tracking ID Patterns:
        - Contains "99999": Returns 404 (tracking not found)
        - Contains "delivered": Returns 200 with "delivered" status
        - Contains "failed": Returns 200 with "failed_delivery" status
        - Any other: Returns 200 with "in_transit" status
    """
    # Log the tracking request
    print(f"📍 Consultando tracking para: {tracking_id}")
    
    # Simulate error case: Tracking not found
    if "99999" in tracking_id:
        print(f"❌ Tracking {tracking_id} no encontrado")
        
        return JSONResponse(
            status_code=404,
            content={
                "error": "Tracking not found",
                "tracking_id": tracking_id,
                "message": "No se encontró información de seguimiento para el ID proporcionado",
                "suggestion": "Verifica que el número de tracking sea correcto o contacta al remitente"
            }
        )
    
    # Success case: Tracking found
    # Determine status based on tracking_id pattern
    if "delivered" in tracking_id.lower():
        # Simulate delivered package
        print(f"✅ Tracking {tracking_id} - Estado: ENTREGADO")
        
        tracking_data = {
            "tracking_id": tracking_id,
            "order_id": tracking_id.replace("TRK-", "").replace("delivered-", ""),
            "carrier": "Andreani",
            "status": "delivered",
            "status_label": "Entregado",
            "estimated_delivery_date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "current_location": {
                "city": "Buenos Aires",
                "state": "CABA",
                "country": "Argentina"
            },
            "recipient": {
                "name": "Juan Pérez",
                "address": "Av. Corrientes 1234, Piso 5",
                "city": "Buenos Aires",
                "postal_code": "C1043"
            },
            "delivery_confirmation": {
                "delivered_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "received_by": "Juan Pérez",
                "signature_url": "https://logistics-api.com/signatures/xyz123.png"
            },
            "history": [
                {
                    "timestamp": "2025-10-16T14:45:00Z",
                    "status": "delivered",
                    "location": "Av. Corrientes 1234",
                    "description": "Paquete entregado exitosamente"
                },
                {
                    "timestamp": "2025-10-16T10:30:00Z",
                    "status": "out_for_delivery",
                    "location": "Centro de Distribución CABA",
                    "description": "El paquete salió para entrega"
                },
                {
                    "timestamp": "2025-10-16T08:15:00Z",
                    "status": "in_transit",
                    "location": "Hub Buenos Aires",
                    "description": "Paquete en tránsito hacia centro de distribución"
                },
                {
                    "timestamp": "2025-10-15T14:20:00Z",
                    "status": "received",
                    "location": "Centro de Procesamiento Rosario",
                    "description": "Paquete recibido en origen"
                }
            ],
            "package_info": {
                "weight_kg": 0.5,
                "dimensions": "30x20x10 cm",
                "items_count": 1
            },
            "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
    elif "failed" in tracking_id.lower():
        # Simulate failed delivery attempt
        print(f"⚠️ Tracking {tracking_id} - Estado: INTENTO FALLIDO")
        
        tracking_data = {
            "tracking_id": tracking_id,
            "order_id": tracking_id.replace("TRK-", "").replace("failed-", ""),
            "carrier": "Andreani",
            "status": "failed_delivery",
            "status_label": "Intento de entrega fallido",
            "estimated_delivery_date": "2025-10-17T18:00:00Z",
            "current_location": {
                "city": "Buenos Aires",
                "state": "CABA",
                "country": "Argentina"
            },
            "recipient": {
                "name": "Juan Pérez",
                "address": "Av. Corrientes 1234, Piso 5",
                "city": "Buenos Aires",
                "postal_code": "C1043"
            },
            "failure_reason": "Destinatario ausente",
            "next_attempt": "2025-10-17T10:00:00Z",
            "history": [
                {
                    "timestamp": "2025-10-16T15:30:00Z",
                    "status": "failed_delivery",
                    "location": "Av. Corrientes 1234",
                    "description": "Intento de entrega - Nadie en el domicilio"
                },
                {
                    "timestamp": "2025-10-16T10:30:00Z",
                    "status": "out_for_delivery",
                    "location": "Centro de Distribución CABA",
                    "description": "El paquete salió para entrega"
                },
                {
                    "timestamp": "2025-10-16T08:15:00Z",
                    "status": "in_transit",
                    "location": "Hub Buenos Aires",
                    "description": "Paquete en tránsito hacia centro de distribución"
                },
                {
                    "timestamp": "2025-10-15T14:20:00Z",
                    "status": "received",
                    "location": "Centro de Procesamiento Rosario",
                    "description": "Paquete recibido en origen"
                }
            ],
            "package_info": {
                "weight_kg": 0.5,
                "dimensions": "30x20x10 cm",
                "items_count": 1
            },
            "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
    else:
        # Default case: Package in transit
        print(f"🚚 Tracking {tracking_id} - Estado: EN CAMINO")
        
        tracking_data = {
            "tracking_id": tracking_id,
            "order_id": tracking_id.replace("TRK-", ""),
            "carrier": "Andreani",
            "status": "in_transit",
            "status_label": "En camino",
            "estimated_delivery_date": "2025-10-18T18:00:00Z",
            "current_location": {
                "city": "Buenos Aires",
                "state": "CABA",
                "country": "Argentina"
            },
            "recipient": {
                "name": "Juan Pérez",
                "address": "Av. Corrientes 1234, Piso 5",
                "city": "Buenos Aires",
                "postal_code": "C1043"
            },
            "history": [
                {
                    "timestamp": "2025-10-16T10:30:00Z",
                    "status": "out_for_delivery",
                    "location": "Centro de Distribución CABA",
                    "description": "El paquete salió para entrega"
                },
                {
                    "timestamp": "2025-10-16T08:15:00Z",
                    "status": "in_transit",
                    "location": "Hub Buenos Aires",
                    "description": "Paquete en tránsito hacia centro de distribución"
                },
                {
                    "timestamp": "2025-10-15T14:20:00Z",
                    "status": "received",
                    "location": "Centro de Procesamiento Rosario",
                    "description": "Paquete recibido en origen"
                }
            ],
            "package_info": {
                "weight_kg": 0.5,
                "dimensions": "30x20x10 cm",
                "items_count": 1
            },
            "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    
    print(f"✅ Tracking data generado para {tracking_id}")
    
    return JSONResponse(
        status_code=200,
        content=tracking_data
    )


@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint for service monitoring.
    
    Returns:
        dict: Service status information.
    """
    return {
        "status": "healthy",
        "service": "integrations",
        "version": "1.0.0",
        "available_integrations": ["stock", "logistics"]
    }
