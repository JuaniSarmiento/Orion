"""
CORE Service - Business Logic Orchestrator
===========================================
Main entry point for the CORE microservice.

This service acts as the central orchestrator for business logic,
receiving NLU-processed data and executing the appropriate strategies
based on detected intents and entities.
"""

from fastapi import FastAPI
from schemas.nlu import NLUInput, ExecutionResponse
from strategies.trackear_pedido import TrackearPedidoStrategy
from strategies.consultar_stock import ConsultarStockStrategy
from strategies.consultar_precio import ConsultarPrecioStrategy
from strategies.cambiar_pedido import CambiarPedidoStrategy
from strategies.queja_reclamo import QuejaReclamoStrategy
from strategies.saludo import SaludoStrategy
from strategies.agradecimiento import AgradecimientoStrategy
from notifications import send_escalation_email

# Initialize FastAPI application
app = FastAPI(
    title="ORION CORE Service",
    description="Business logic orchestrator for intent-based action execution",
    version="2.0.0"  # Version bump for enhanced capabilities
)

# Strategy Registry: Maps intent names to their corresponding strategy classes
# This implements the Strategy Pattern, allowing easy addition of new intents
STRATEGIES = {
    "trackear_pedido": TrackearPedidoStrategy,
    "consultar_stock": ConsultarStockStrategy,
    "consultar_precio": ConsultarPrecioStrategy,
    "cambiar_pedido": CambiarPedidoStrategy,
    "queja_reclamo": QuejaReclamoStrategy,
    "saludo": SaludoStrategy,
    "agradecimiento": AgradecimientoStrategy,
}

# Failed Intent Tracker: In-memory counter for escalation to human
# ==================================================================
# This dictionary tracks consecutive failed intent attempts per user.
# Key: user_id (string)
# Value: count of consecutive "intencion_desconocida" occurrences (int)
#
# Escalation Logic:
# - When a user sends a message that results in "intencion_desconocida", 
#   their counter is incremented.
# - When a user sends a message with a recognized intent, their counter 
#   is reset to 0.
# - When the counter reaches 2, an escalation to human alert is triggered.
#
# Note: This is an in-memory solution that will be lost on service restart.
# For production, consider using Redis or a persistent database.
failed_intent_tracker = {}


@app.post("/execute", response_model=ExecutionResponse)
async def execute_action(nlu_data: NLUInput) -> ExecutionResponse:
    """
    Execute business logic based on NLU-processed data.
    
    This endpoint receives the analyzed data from the NLU service and
    orchestrates the appropriate business logic execution based on the
    detected intent. It uses the Strategy Pattern to dispatch requests
    to the appropriate handler for each intent type.
    
    Additionally, it tracks failed intent attempts per user and triggers
    escalation to human when a threshold is reached.
    
    Args:
        nlu_data (NLUInput): The NLU processing results including intent,
            entities, original text, and user identification.
    
    Returns:
        ExecutionResponse: Status and description of the executed action.
        
    Example Request:
        {
            "intent": "trackear_pedido",
            "entities": [
                {"label": "numero_pedido", "value": "481516"}
            ],
            "original_text": "¿Dónde está mi pedido 481516?",
            "channel_user_id": "+5491112345678"
        }
        
    Example Response:
        {
            "status": "success",
            "action": "Estrategia ejecutada: Buscando el pedido número 481516.",
            "details": {
                "intent": "trackear_pedido",
                "order_number": "481516",
                "next_step": "Consultar API de logística"
            }
        }
    """
    # Log the incoming NLU data
    print(f"🎯 CORE Service - Procesando intención: {nlu_data.intent}")
    print(f"📦 Entidades recibidas: {nlu_data.entities}")
    print(f"💬 Texto original: {nlu_data.original_text}")
    
    # Extract user_id for tracking failed attempts
    user_id = nlu_data.channel_user_id
    print(f"👤 Usuario: {user_id}")
    
    # ==========================================
    # FAILED INTENT TRACKING & ESCALATION LOGIC
    # ==========================================
    
    if nlu_data.intent != "intencion_desconocida":
        # ✅ Bot understood the intent
        # Reset counter for this user if it exists
        if user_id in failed_intent_tracker:
            print(f"✨ Intent reconocido. Reseteando contador para usuario {user_id}")
            print(f"   (Era: {failed_intent_tracker[user_id]} intentos fallidos)")
            del failed_intent_tracker[user_id]
    
    else:
        # ❌ Bot did not understand (intencion_desconocida)
        # Increment the failed attempts counter
        if user_id not in failed_intent_tracker:
            failed_intent_tracker[user_id] = 1
            print(f"⚠️ Intent desconocido. Inicializando contador para usuario {user_id}: 1")
        else:
            failed_intent_tracker[user_id] += 1
            print(f"⚠️ Intent desconocido. Incrementando contador para usuario {user_id}: {failed_intent_tracker[user_id]}")
        
        # Check if escalation threshold has been reached
        if failed_intent_tracker[user_id] >= 2:
            print("=" * 70)
            print(f"🚨 ¡ESCALAR A HUMANO! Usuario: {user_id} ha superado el umbral de intentos fallidos.")
            print(f"   Intentos consecutivos: {failed_intent_tracker[user_id]}")
            print(f"   Último mensaje: '{nlu_data.original_text}'")
            print("=" * 70)
            
            # Send email notification to support team
            await send_escalation_email(
                user_id=user_id,
                last_message=nlu_data.original_text,
                failed_attempts=failed_intent_tracker[user_id]
            )
            
            # Reset counter after triggering escalation
            failed_intent_tracker[user_id] = 0
            print(f"🔄 Contador reseteado para usuario {user_id}")
    
    # Log current state of failed_intent_tracker
    if failed_intent_tracker:
        print(f"📊 Estado actual del tracker: {failed_intent_tracker}")
    
    # ==========================================
    # END ESCALATION LOGIC
    # ==========================================
    
    # Convert Pydantic models to dictionaries for strategy execution
    entities_list = [entity.dict() for entity in nlu_data.entities]
    
    # Look up the appropriate strategy for this intent
    strategy_class = STRATEGIES.get(nlu_data.intent)
    
    if strategy_class:
        # Strategy found: instantiate and execute
        print(f"✅ Estrategia encontrada para intent '{nlu_data.intent}'")
        
        # Create an instance of the strategy
        strategy = strategy_class()
        
        # Execute the strategy with the provided entities (async)
        result = await strategy.execute(entities_list)
        
        # Log the execution result
        print(f"📤 Resultado de la estrategia: {result}")
        
        # Build and return the response
        response = ExecutionResponse(
            status=result.get("status", "success"),
            action=result.get("message", "Acción ejecutada correctamente"),
            details={
                "intent": nlu_data.intent,
                **{k: v for k, v in result.items() if k not in ["status", "message"]}
            }
        )
    else:
        # No strategy found for this intent
        print(f"⚠️ No se encontró estrategia para intent '{nlu_data.intent}'")
        
        response = ExecutionResponse(
            status="error",
            action=f"Intent '{nlu_data.intent}' no tiene estrategia asociada",
            details={
                "intent": nlu_data.intent,
                "available_intents": list(STRATEGIES.keys())
            }
        )
    
    return response


@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint for service monitoring.
    
    Returns:
        dict: Service status information.
    """
    return {
        "status": "healthy",
        "service": "core",
        "version": "1.0.0"
    }
