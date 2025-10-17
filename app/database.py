"""
Database Module - MongoDB Connection and Operations
====================================================
Handles MongoDB connection and data persistence for conversation logs.

This module provides functions to connect to MongoDB and save conversation
history, enabling analytics and audit trails for all user interactions.
"""

import os
from datetime import datetime
import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


# ============================================
# MongoDB Connection Configuration
# ============================================

# Read MongoDB configuration from environment variables
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = os.getenv('MONGO_PORT', '27017')
MONGO_USER = os.getenv('MONGO_USER', 'orion_admin')
MONGO_PASS = os.getenv('MONGO_PASS', 'supersecretpassword')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'orion_conversations')

# Build MongoDB connection URI
# Format: mongodb://username:password@host:port/
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/"

print(f"📊 MongoDB Configuration:")
print(f"   Host: {MONGO_HOST}:{MONGO_PORT}")
print(f"   Database: {MONGO_DB_NAME}")
print(f"   User: {MONGO_USER}")


# ============================================
# MongoDB Client Initialization
# ============================================

try:
    # Create MongoDB client
    # This client is reused across all requests (singleton pattern)
    client: MongoClient = pymongo.MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000  # 5 second timeout for connection
    )
    
    # Test the connection
    client.admin.command('ping')
    print(f"✅ MongoDB connection successful!")
    
    # Select database
    db: Database = client[MONGO_DB_NAME]
    
    # Select collection for conversation logs
    conversations_collection: Collection = db["conversations"]
    
    print(f"✅ Database '{MONGO_DB_NAME}' selected")
    print(f"✅ Collection 'conversations' ready")
    
except pymongo.errors.ServerSelectionTimeoutError as e:
    print(f"❌ Error: No se pudo conectar a MongoDB")
    print(f"   Verifica que el servicio 'db' esté corriendo: docker-compose ps")
    print(f"   Error: {str(e)}")
    client = None
    db = None
    conversations_collection = None
    
except pymongo.errors.OperationFailure as e:
    print(f"❌ Error de autenticación en MongoDB")
    print(f"   Verifica MONGO_USER y MONGO_PASS en .env")
    print(f"   Error: {str(e)}")
    client = None
    db = None
    conversations_collection = None
    
except Exception as e:
    print(f"❌ Error inesperado al conectar a MongoDB: {str(e)}")
    client = None
    db = None
    conversations_collection = None


# ============================================
# Database Operations
# ============================================

def save_message(message_data: dict) -> bool:
    """
    Save a conversation message to MongoDB.
    
    This function persists a complete interaction (user message, NLU analysis,
    and CORE response) to the conversations collection for audit, analytics,
    and future improvements to the NLU model.
    
    Args:
        message_data (dict): Dictionary containing the conversation data.
            Expected keys:
                - timestamp (str): ISO format timestamp
                - channel (str): Communication channel (e.g., "whatsapp")
                - user_id (str): Unique user identifier
                - message (dict): Original user message
                - nlu_response (dict): NLU service response
                - core_response (dict): CORE service response
    
    Returns:
        bool: True if message saved successfully, False otherwise.
        
    Example:
        >>> log_document = {
        ...     "timestamp": "2025-10-16T20:30:00Z",
        ...     "channel": "whatsapp",
        ...     "user_id": "+5491112345678",
        ...     "message": {"text": "¿Dónde está mi pedido?"},
        ...     "nlu_response": {"intent": "trackear_pedido", ...},
        ...     "core_response": {"status": "success", ...}
        ... }
        >>> save_message(log_document)
        True
    """
    # Check if MongoDB connection is available
    if conversations_collection is None:
        print("⚠️ MongoDB no disponible. No se guardará el mensaje.")
        return False
    
    try:
        # Ensure timestamp exists
        if 'timestamp' not in message_data:
            message_data['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Insert document into conversations collection
        result = conversations_collection.insert_one(message_data)
        
        # Log success with document ID
        print(f"💾 Mensaje guardado en MongoDB")
        print(f"   Document ID: {result.inserted_id}")
        print(f"   User: {message_data.get('user_id', 'unknown')}")
        print(f"   Intent: {message_data.get('nlu_response', {}).get('intent', 'N/A')}")
        
        return True
        
    except pymongo.errors.WriteError as e:
        print(f"❌ Error al escribir en MongoDB: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado al guardar mensaje: {str(e)}")
        return False


def get_user_history(user_id: str, limit: int = 10) -> list:
    """
    Retrieve conversation history for a specific user.
    
    This function fetches the most recent conversations for a given user,
    useful for context-aware responses and customer support.
    
    Args:
        user_id (str): Unique user identifier
        limit (int): Maximum number of messages to retrieve (default: 10)
    
    Returns:
        list: List of conversation documents, most recent first.
        
    Example:
        >>> history = get_user_history("+5491112345678", limit=5)
        >>> len(history)
        5
    """
    if conversations_collection is None:
        print("⚠️ MongoDB no disponible. No se puede obtener historial.")
        return []
    
    try:
        # Query for user messages, sorted by timestamp (newest first)
        cursor = conversations_collection.find(
            {"user_id": user_id}
        ).sort("timestamp", pymongo.DESCENDING).limit(limit)
        
        # Convert cursor to list
        history = list(cursor)
        
        print(f"📚 Historial recuperado: {len(history)} mensajes para usuario {user_id}")
        
        return history
        
    except Exception as e:
        print(f"❌ Error al recuperar historial: {str(e)}")
        return []


def get_conversation_stats() -> dict:
    """
    Get statistics about all conversations.
    
    Returns:
        dict: Statistics including total messages, unique users, etc.
        
    Example:
        >>> stats = get_conversation_stats()
        >>> print(stats['total_messages'])
        1250
    """
    if conversations_collection is None:
        print("⚠️ MongoDB no disponible.")
        return {}
    
    try:
        total_messages = conversations_collection.count_documents({})
        
        # Aggregate unique users
        unique_users = len(conversations_collection.distinct("user_id"))
        
        stats = {
            "total_messages": total_messages,
            "unique_users": unique_users,
            "collection": "conversations",
            "database": MONGO_DB_NAME
        }
        
        return stats
        
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {str(e)}")
        return {}


# ============================================
# Export Collection for Direct Access
# ============================================

# Export conversations_collection so other modules can query directly
__all__ = ['save_message', 'get_user_history', 'get_conversation_stats', 'conversations_collection']
