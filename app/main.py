"""
ORION - API Gateway
===================
Main entry point for the ORION FastAPI application.

This module serves as the central API Gateway, handling all incoming
webhook requests from external services like WhatsApp API.
"""

import httpx
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from schemas.messages import IncomingMessage
from database import save_message, conversations_collection

# Initialize FastAPI application
app = FastAPI(
    title="ORION API Gateway",
    description="Unified webhook entry point for external messaging services",
    version="1.0.0"
)

# Configure Jinja2 templates
# Note: Use relative path "templates" since working directory is /app in Docker
templates = Jinja2Templates(directory="templates")


@app.post("/webhook/message")
async def receive_webhook(message: IncomingMessage) -> dict:
    """
    Webhook endpoint for receiving and processing incoming messages.
    
    This is the single entry point for all messages arriving from external
    services such as the WhatsApp Business API. The endpoint orchestrates
    the complete processing pipeline:
    1. Validates incoming message structure
    2. Forwards to NLU service for intent/entity extraction
    3. Sends NLU results to CORE service for business logic execution
    4. Returns final execution result to the client
    
    Args:
        message (IncomingMessage): The incoming message payload containing
            channel, user_id, and text fields.
    
    Returns:
        dict: A JSON response containing the CORE service execution results
            with status, action, and details.
        
    Example Request Body:
        {
            "channel": "whatsapp",
            "user_id": "549112345678",
            "text": "¿Dónde está mi pedido 481516?"
        }
        
    Example Response:
        {
            "status": "success",
            "action": "Executing strategy for intent: trackear_pedido",
            "details": {
                "intent": "trackear_pedido",
                "entity_count": 1,
                "has_entities": true
            }
        }
    """
    # Log the incoming webhook message
    print(f"📨 Webhook recibido - Canal: {message.channel}, Usuario: {message.user_id}")
    print(f"💬 Texto del mensaje: {message.text}")
    
    # Use a single async client for all service calls
    async with httpx.AsyncClient() as client:
        # Step 1: Forward the message text to NLU service for processing
        print(f"🔄 Enviando a NLU service...")
        nlu_response = await client.post(
            "http://nlu:8000/process",
            json={
                "text": message.text,
                "channel_user_id": message.user_id  # Include user_id for tracking
            },
            timeout=10.0
        )
        
        # Parse the JSON response from NLU service
        nlu_data = nlu_response.json()
        print(f"🧠 Respuesta del NLU: {nlu_data}")
        
        # Step 2: Forward NLU results to CORE service for business logic execution
        print(f"🔄 Enviando a CORE service...")
        core_response = await client.post(
            "http://core:8000/execute",
            json=nlu_data,
            timeout=10.0
        )
        
        # Parse the JSON response from CORE service
        core_data = core_response.json()
        print(f"🎯 Respuesta del CORE: {core_data}")
    
    # ============================================
    # SAVE CONVERSATION TO MONGODB
    # ============================================
    
    # Create log document with complete interaction data
    log_document = {
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "channel": message.channel,
        "user_id": message.user_id,
        "message": {
            "text": message.text,
            "channel": message.channel
        },
        "nlu_response": nlu_data,
        "core_response": core_data
    }
    
    # Save to MongoDB
    print(f"💾 Guardando conversación en MongoDB...")
    save_message(log_document)
    
    # ============================================
    # END MONGODB SAVE
    # ============================================
    
    # Return the final execution result from CORE service to the client
    return core_data


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Dashboard endpoint for viewing conversation history.
    
    This endpoint provides a web-based interface for administrators to
    view all conversations stored in MongoDB. It displays:
    - Total conversation count
    - Unique users
    - Recent activity statistics
    - Full conversation history in a table
    
    Args:
        request (Request): FastAPI request object for template rendering.
    
    Returns:
        HTMLResponse: Rendered HTML dashboard page.
        
    Access:
        Open http://localhost:8080/dashboard in your browser
    """
    print(f"📊 Dashboard solicitado")
    
    # Check if MongoDB is available
    if conversations_collection is None:
        print("⚠️ MongoDB no disponible para el dashboard")
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "conversations": [],
                "total_conversations": 0,
                "unique_users": 0,
                "recent_count": 0
            }
        )
    
    try:
        # Fetch all conversations from MongoDB (sorted by timestamp, newest first)
        conversations = list(
            conversations_collection.find()
            .sort("timestamp", -1)
            .limit(100)  # Limit to last 100 conversations for performance
        )
        
        # Convert ObjectId to string for template rendering
        for conv in conversations:
            conv['_id'] = str(conv['_id'])
        
        # Calculate statistics
        total_conversations = conversations_collection.count_documents({})
        unique_users = len(conversations_collection.distinct("user_id"))
        
        # Count recent conversations (last 24 hours)
        from datetime import timedelta
        cutoff_time = (datetime.utcnow() - timedelta(hours=24)).isoformat() + 'Z'
        recent_count = conversations_collection.count_documents({
            "timestamp": {"$gte": cutoff_time}
        })
        
        print(f"✅ Dashboard cargado:")
        print(f"   Total: {total_conversations} conversaciones")
        print(f"   Usuarios únicos: {unique_users}")
        print(f"   Últimas 24h: {recent_count}")
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "conversations": conversations,
                "total_conversations": total_conversations,
                "unique_users": unique_users,
                "recent_count": recent_count
            }
        )
        
    except Exception as e:
        print(f"❌ Error al cargar dashboard: {str(e)}")
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "conversations": [],
                "total_conversations": 0,
                "unique_users": 0,
                "recent_count": 0
            }
        )


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        dict: Welcome message and available endpoints.
    """
    return {
        "service": "ORION API Gateway",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "webhook": "POST /webhook/message",
            "dashboard": "GET /dashboard"
        }
    }
