"""
NLU Service - Natural Language Understanding
=============================================
Main entry point for the NLU microservice.

This service analyzes text messages to extract intents and entities
using spaCy for Natural Language Processing.
"""

import re
import spacy
from fastapi import FastAPI
from pydantic import BaseModel

# Load Spanish language model at startup (singleton pattern)
# This ensures the model is loaded once and reused across all requests
nlp = spacy.load("es_core_news_sm")


# Initialize FastAPI application
app = FastAPI(
    title="ORION NLU Service",
    description="Natural Language Understanding service for intent and entity extraction",
    version="1.0.0"
)


class TextInput(BaseModel):
    """
    Schema for text input to be processed by the NLU service.
    
    Attributes:
        text (str): The text message to analyze.
        channel_user_id (str, optional): The user identifier for tracking purposes.
    """
    text: str
    channel_user_id: str = "unknown"  # Default for backwards compatibility


class NLUResponse(BaseModel):
    """
    Schema for NLU processing response.
    
    Attributes:
        intent (str): The detected user intent.
        entities (list): List of extracted entities from the text.
        original_text (str): The original input text.
        channel_user_id (str): The user identifier passed through for tracking.
        confidence (float): Confidence score of intent classification (0.0 to 1.0).
        normalized_text (str): Cleaned and normalized version of input text.
    """
    intent: str
    entities: list
    original_text: str
    channel_user_id: str
    confidence: float = 0.0
    normalized_text: str = ""


class NLUResponse(BaseModel):
    """
    Schema for NLU processing response.
    
    Attributes:
        intent (str): The detected user intent.
        entities (list): List of extracted entities from the text.
        original_text (str): The original input text.
        channel_user_id (str): The user identifier passed through for tracking.
        confidence (float): Confidence score of intent classification (0.0 to 1.0).
        normalized_text (str): Cleaned and normalized version of input text.
    """
    intent: str
    entities: list
    original_text: str
    channel_user_id: str
    confidence: float = 0.0
    normalized_text: str = ""


def normalize_text(text: str) -> str:
    """
    Normalize and clean text for better NLU processing.
    
    This function handles:
    - Common Spanish chat abbreviations and slang
    - Spelling corrections
    - Accent normalization
    - Whitespace cleanup
    
    Args:
        text (str): Raw input text
        
    Returns:
        str: Normalized text
        
    Examples:
        >>> normalize_text("qe onda xq no llega mi pedido???")
        'que onda porque no llega mi pedido'
        >>> normalize_text("hla    tenes stok?")
        'hola tienes stock'
    """
    # Convert to lowercase
    normalized = text.lower()
    
    # Common Spanish chat abbreviations
    replacements = {
        r'\bq\b': 'que',
        r'\bqe\b': 'que',
        r'\bxq\b': 'porque',
        r'\bporq\b': 'porque',
        r'\bpq\b': 'porque',
        r'\btb\b': 'también',
        r'\btmb\b': 'también',
        r'\bhla\b': 'hola',
        r'\bsta\b': 'esta',
        r'\bstok\b': 'stock',
        r'\bbnos\b': 'buenos',
        r'\bx\b': 'por',
        r'\bfav\b': 'favor',
        r'\bpls\b': 'por favor',
        r'\bpfa\b': 'por favor',
        r'\bgrax\b': 'gracias',
        r'\bgcs\b': 'gracias',
        r'\btq\b': 'te quiero',
        r'\baq\b': 'aquí',
        r'\bahi\b': 'ahí',
        r'\bd\b': 'de',
        r'\bpedio\b': 'pedido',
        r'\benvi[oó]\b': 'envío',
        r'\best[aá]\b': 'está',
    }
    
    for pattern, replacement in replacements.items():
        normalized = re.sub(pattern, replacement, normalized)
    
    # Remove excess punctuation
    normalized = re.sub(r'[?!]{2,}', '?', normalized)
    normalized = re.sub(r'\.{2,}', '.', normalized)
    
    # Remove excess whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    normalized = normalized.strip()
    
    return normalized


def classify_intent(text: str) -> tuple[str, float]:
    """
    Classify the user's intent with confidence scoring.
    
    Enhanced version with:
    - More comprehensive keyword patterns
    - Synonym support
    - Confidence scoring
    - Better context understanding
    
    Args:
        text (str): The input text to classify.
    
    Returns:
        tuple[str, float]: (intent, confidence_score)
        
    Supported Intents:
        - "trackear_pedido": Track order/shipment
        - "consultar_stock": Check product availability  
        - "consultar_precio": Ask about prices
        - "cambiar_pedido": Modify/cancel order
        - "queja_reclamo": Complaints or issues
        - "saludo": Greetings
        - "agradecimiento": Thanks/goodbye
        - "intencion_desconocida": Unknown intent
    """
    # Normalize text first
    text_normalized = normalize_text(text)
    text_lower = text_normalized.lower()
    
    confidence = 0.0
    detected_intent = "intencion_desconocida"
    
    # ============================================================
    # Intent: Trackear Pedido (Track Order)
    # ============================================================
    tracking_keywords = [
        'donde', 'dónde', 'está', 'esta', 'pedido', 'envío', 'envio',
        'rastrear', 'tracking', 'seguimiento', 'paquete', 'entrega',
        'llega', 'llegó', 'demora', 'tardanza', 'ubicación', 'ubicacion',
        'trayecto', 'camino', 'transito', 'tránsito', 'courier',
        'entregado', 'recibido', 'distribucion', 'distribución'
    ]
    
    tracking_score = sum(1 for kw in tracking_keywords if kw in text_lower)
    
    # Strong indicators (higher weight)
    if any(phrase in text_lower for phrase in [
        'donde esta', 'dónde está', 'donde esta mi', 'dónde está mi',
        'rastrear pedido', 'tracking', 'seguimiento', 'mi pedido',
        'mi envío', 'mi envio', 'numero de seguimiento', 'código de rastreo'
    ]):
        tracking_score += 3
    
    if tracking_score >= 2:
        detected_intent = "trackear_pedido"
        confidence = min(0.5 + (tracking_score * 0.15), 0.95)
    
    # ============================================================
    # Intent: Consultar Stock (Check Stock)
    # ============================================================
    stock_keywords = [
        'stock', 'disponible', 'hay', 'tienen', 'tenés', 'tenes',
        'queda', 'quedan', 'existencia', 'inventario', 'producto',
        'artículo', 'articulo', 'mercadería', 'mercaderia', 'disponibilidad'
    ]
    
    stock_score = sum(1 for kw in stock_keywords if kw in text_lower)
    
    if any(phrase in text_lower for phrase in [
        'tienen stock', 'hay stock', 'tiene stock', 'tenes stock',
        'stock del', 'stock de', 'disponible', 'en stock',
        'hay disponibilidad', 'disponibilidad de'
    ]):
        stock_score += 3
    
    if stock_score >= 2 and stock_score > tracking_score:
        detected_intent = "consultar_stock"
        confidence = min(0.5 + (stock_score * 0.15), 0.95)
    
    # ============================================================
    # Intent: Consultar Precio (Ask Price)
    # ============================================================
    price_keywords = [
        'precio', 'cuesta', 'vale', 'cuanto', 'cuánto', 'costo',
        'sale', 'cobran', 'pagar', 'barato', 'caro',
        'oferta', 'promoción', 'promocion', 'descuento', 'valor', 'estan'
    ]
    
    price_score = sum(1 for kw in price_keywords if kw in text_lower)
    
    if any(phrase in text_lower for phrase in [
        'cuanto cuesta', 'cuánto cuesta', 'cuanto sale', 'cuánto sale',
        'cual es el precio', 'cuál es el precio', 'que precio',
        'cual es el valor', 'cuál es el valor', 'a cuanto',
        'a cuánto', 'cuanto estan', 'cuánto están'
    ]):
        price_score += 3
    
    # Detect price confirmation patterns (e.g., "cuesta $5000?")
    if any(word in text_lower for word in ['cuesta', 'vale', 'precio']) and ('$' in text or any(char.isdigit() for char in text)):
        price_score += 2
    
    if price_score >= 2 and price_score > max(tracking_score, stock_score):
        detected_intent = "consultar_precio"
        confidence = min(0.5 + (price_score * 0.15), 0.95)
    
    # ============================================================
    # Intent: Cambiar/Cancelar Pedido (Modify Order)
    # ============================================================
    modify_keywords = [
        'cancelar', 'cambiar', 'devolver',
        'devolución', 'devolucion', 'equivocado', 'error', 'mal', 'modificar', 'anular'
    ]
    
    modify_score = sum(1 for kw in modify_keywords if kw in text_lower)
    
    if any(phrase in text_lower for phrase in [
        'quiero cancelar', 'cancelar pedido', 'cambiar pedido',
        'me equivoqué', 'pedido equivocado', 'no quiero', 'devolver',
        'modificar pedido', 'modificar el pedido', 'anular pedido'
    ]):
        modify_score += 3
    
    if modify_score >= 2:
        detected_intent = "cambiar_pedido"
        confidence = min(0.5 + (modify_score * 0.15), 0.95)
    
    # ============================================================
    # Intent: Queja/Reclamo (Complaint)
    # ============================================================
    complaint_keywords = [
        'queja', 'reclamo', 'problema', 'mal', 'mala', 'malo',
        'pésimo', 'pesimo', 'defectuoso', 'roto',
        'dañado', 'danado', 'enojado', 'molesto', 'indignado',
        'fraude', 'estafa', 'no llega', 'horrible', 'nunca'
    ]
    
    complaint_score = sum(1 for kw in complaint_keywords if kw in text_lower)
    
    if any(phrase in text_lower for phrase in [
        'tengo un problema', 'no funciona', 'mal servicio',
        'quiero reclamar', 'esto es un', 'no entiendo',
        'nunca me llega', 'nunca llega', 'esto es horrible'
    ]):
        complaint_score += 2
    
    if complaint_score >= 2:
        detected_intent = "queja_reclamo"
        confidence = min(0.5 + (complaint_score * 0.15), 0.95)
    
    # ============================================================
    # Intent: Saludo (Greeting)
    # ============================================================
    if any(phrase in text_lower for phrase in [
        'hola', 'buenos días', 'buenas tardes', 'buenas noches',
        'buen día', 'buenas', 'saludos', 'qué tal', 'que tal',
        'como estas', 'cómo estás', 'hey', 'ey'
    ]):
        # Only classify as greeting if no other strong intent
        if confidence < 0.5:
            detected_intent = "saludo"
            confidence = 0.85
    
    # ============================================================
    # Intent: Agradecimiento (Thanks/Goodbye)
    # ============================================================
    if any(phrase in text_lower for phrase in [
        'gracias', 'muchas gracias', 'muy amable', 'perfecto',
        'genial', 'excelente', 'chau', 'adiós', 'adios', 'hasta luego',
        'nos vemos', 'abrazo', 'saludos'
    ]):
        if confidence < 0.5:
            detected_intent = "agradecimiento"
            confidence = 0.85
    
    # Default confidence for unknown
    if detected_intent == "intencion_desconocida":
        confidence = 0.1
    
    return detected_intent, confidence


def extract_entities(doc) -> list:
    """
    Extract relevant entities from a spaCy processed document.
    
    Enhanced version with:
    - Product name extraction
    - Multiple ID format support
    - Better number detection
    - Price extraction
    
    Args:
        doc: A spaCy Doc object that has been processed by the NLP pipeline.
    
    Returns:
        list: A list of dictionaries with extracted entities
    """
    entities = []
    found_identifiers = set()
    text = doc.text
    
    # ============================================================
    # PRIORITY 1: Complex Tracking IDs
    # ============================================================
    tracking_id_pattern = r'\b(?:TRK|ID|PEDIDO|ORDEN|ORD|PKG|ENV)[\w-]+\b'
    tracking_matches = re.finditer(tracking_id_pattern, text, re.IGNORECASE)
    
    for match in tracking_matches:
        tracking_id = match.group()
        if tracking_id not in found_identifiers:
            found_identifiers.add(tracking_id)
            entities.append({
                "label": "tracking_id",
                "value": tracking_id
            })
    
    # ============================================================
    # PRIORITY 2: Numeric Order Numbers
    # ============================================================
    if not entities:
        # spaCy NER for numbers
        for ent in doc.ents:
            if ent.label_ in ['CARDINAL', 'QUANTITY']:
                clean_number = re.sub(r'\D', '', ent.text)
                if clean_number and len(clean_number) >= 3:
                    if clean_number not in found_identifiers:
                        found_identifiers.add(clean_number)
                        entities.append({
                            "label": "numero_pedido",
                            "value": clean_number
                        })
        
        # Regex fallback
        number_pattern = r'\b\d{3,}\b'
        number_matches = re.finditer(number_pattern, text)
        
        for match in number_matches:
            number = match.group()
            if number not in found_identifiers:
                found_identifiers.add(number)
                entities.append({
                    "label": "numero_pedido",
                    "value": number
                })
    
    # ============================================================
    # PRIORITY 3: Product Names (after product/articulo/item keywords)
    # ============================================================
    product_patterns = [
        r'(?:producto|artículo|articulo|item|código|codigo|sku)\s+([A-Z0-9-]+)',
        r'(?:producto|artículo|articulo)\s+(["\']?)([^"\']+)\1',
    ]
    
    for pattern in product_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Get the last captured group (the product name/code)
            product = match.groups()[-1].strip()
            if product and len(product) > 1:
                entities.append({
                    "label": "producto",
                    "value": product
                })
    
    # ============================================================
    # PRIORITY 4: Prices
    # ============================================================
    price_pattern = r'\$\s*(\d+(?:[.,]\d{1,2})?)|(\d+(?:[.,]\d{1,2})?)\s*(?:pesos|dolares|dólares|usd|ars)'
    price_matches = re.finditer(price_pattern, text, re.IGNORECASE)
    
    for match in price_matches:
        price = match.group(1) or match.group(2)
        if price:
            entities.append({
                "label": "precio",
                "value": price
            })
    
    return entities


@app.post("/process", response_model=NLUResponse)
async def process_text(input_data: TextInput) -> NLUResponse:
    """
    Process incoming text to extract intent and entities.
    
    This endpoint receives a text message and analyzes it using NLP
    techniques to determine the user's intent and extract relevant entities.
    The spaCy model is used for linguistic analysis and entity recognition,
    and intent classification is performed using keyword-based rules.
    
    Args:
        input_data (TextInput): JSON payload containing the text to process.
    
    Returns:
        NLUResponse: Structured response with intent, entities, and original text.
        
    Example Request:
        {
            "text": "Hola, ¿tienen stock de la camiseta titular?"
        }
        
    Example Response:
        {
            "intent": "consultar_stock",
            "entities": [],
            "original_text": "Hola, ¿tienen stock de la camiseta titular?"
        }
        
    Example with Entities:
        Request: {"text": "¿Dónde está mi pedido 481516?"}
        Response: {
            "intent": "trackear_pedido",
            "entities": [{"label": "numero_pedido", "value": "481516"}],
            "original_text": "¿Dónde está mi pedido 481516?"
        }
    """
    # Extract the text from the input
    text = input_data.text
    channel_user_id = input_data.channel_user_id
    
    # Normalize text for better processing
    normalized_text = normalize_text(text)
    
    # Classify the intent using enhanced classifier (returns intent + confidence)
    detected_intent, confidence = classify_intent(text)
    
    # Process text with spaCy for entity extraction
    doc = nlp(text)
    
    # Extract entities using enhanced extraction
    extracted_entities = extract_entities(doc)
    
    # Log the classification and extraction results for debugging
    print(f"📥 Texto recibido: {text}")
    print(f"🧹 Texto normalizado: {normalized_text}")
    print(f"👤 Usuario: {channel_user_id}")
    print(f"🎯 Intención detectada: {detected_intent} (confianza: {confidence:.2f})")
    print(f"🧠 Entidades detectadas: {extracted_entities}")
    
    # Return structured NLU response
    return NLUResponse(
        intent=detected_intent,
        entities=extracted_entities,
        original_text=text,
        channel_user_id=channel_user_id,
        confidence=confidence,
        normalized_text=normalized_text
    )


@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint for service monitoring.
    
    Returns:
        dict: Service status information including loaded model details.
    """
    return {
        "status": "healthy",
        "service": "nlu",
        "version": "1.0.0",
        "model_loaded": nlp.meta.get("name", "unknown"),
        "model_version": nlp.meta.get("version", "unknown")
    }
