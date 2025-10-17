"""
🧪 ORION NLU - Suite de Pruebas Exhaustivas
============================================
Test suite completo para validar el NLU mejorado en todos los escenarios posibles.

Este script prueba:
- Clasificación de intents
- Extracción de entidades
- Normalización de texto
- Manejo de ortografía informal
- Edge cases y situaciones límite
- Confidence scoring
"""

import asyncio
import httpx
from datetime import datetime
from typing import Dict, List
import json


# ============================================
# CONFIGURACIÓN
# ============================================

NLU_URL = "http://localhost:8001/process"
API_URL = "http://localhost:8080/webhook/message"

# Colores para output en consola
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


# ============================================
# CASOS DE PRUEBA
# ============================================

TEST_CASES = {
    "TRACKEAR_PEDIDO": [
        # Casos básicos
        {
            "text": "¿Dónde está mi pedido 12345?",
            "expected_intent": "trackear_pedido",
            "expected_entities": ["numero_pedido"],
            "min_confidence": 0.7,
            "description": "Pregunta estándar de tracking"
        },
        {
            "text": "mi pedido es el 98765, ¿cuando llega?",
            "expected_intent": "trackear_pedido",
            "expected_entities": ["numero_pedido"],
            "min_confidence": 0.6,
            "description": "Orden con pregunta de llegada"
        },
        {
            "text": "necesito rastrear el envío TRK-123456",
            "expected_intent": "trackear_pedido",
            "expected_entities": ["tracking_id"],
            "min_confidence": 0.7,
            "description": "Tracking con ID alfanumérico"
        },
        # Ortografía informal
        {
            "text": "qe onda donde sta mi pedio 777",
            "expected_intent": "trackear_pedido",
            "expected_entities": ["numero_pedido"],
            "min_confidence": 0.5,
            "description": "Ortografía muy informal"
        },
        {
            "text": "ola, m podes decir xq no llega mi envio 555?",
            "expected_intent": "trackear_pedido",
            "expected_entities": ["numero_pedido"],
            "min_confidence": 0.5,
            "description": "Abreviaciones y faltas de ortografía"
        },
        # Variaciones de lenguaje
        {
            "text": "che me figura como entregado el pedido 999 pero no lo recibí",
            "expected_intent": "trackear_pedido",
            "expected_entities": ["numero_pedido"],
            "min_confidence": 0.6,
            "description": "Tracking con contexto de problema"
        },
        {
            "text": "hola quiero saber en que parte del trayecto esta mi paquete 44444",
            "expected_intent": "trackear_pedido",
            "expected_entities": ["numero_pedido"],
            "min_confidence": 0.7,
            "description": "Pregunta sobre ubicación en tránsito"
        },
        # IDs complejos
        {
            "text": "tracking ID-delivered-987, donde esta?",
            "expected_intent": "trackear_pedido",
            "expected_entities": ["tracking_id"],
            "min_confidence": 0.7,
            "description": "ID con formato complejo"
        },
        {
            "text": "mi código de seguimiento es ORDEN-2025-001",
            "expected_intent": "trackear_pedido",
            "expected_entities": ["tracking_id"],
            "min_confidence": 0.7,
            "description": "Código de orden estructurado"
        },
        # Edge cases
        {
            "text": "mi pedido 123 nunca llego y ya pasaron 3 semanas",
            "expected_intent": "trackear_pedido",
            "expected_entities": ["numero_pedido"],
            "min_confidence": 0.6,
            "description": "Tracking con queja implícita"
        },
    ],
    
    "CONSULTAR_STOCK": [
        # Casos básicos
        {
            "text": "¿Tienen stock del producto 12345?",
            "expected_intent": "consultar_stock",
            "expected_entities": ["numero_pedido"],
            "min_confidence": 0.7,
            "description": "Consulta estándar de stock"
        },
        {
            "text": "hay disponibilidad de zapatillas?",
            "expected_intent": "consultar_stock",
            "expected_entities": [],
            "min_confidence": 0.6,
            "description": "Pregunta de disponibilidad genérica"
        },
        {
            "text": "hola, tenes stok de remeras?",
            "expected_intent": "consultar_stock",
            "expected_entities": [],
            "min_confidence": 0.6,
            "description": "Consulta informal con error ortográfico"
        },
        # Variaciones
        {
            "text": "me queda alguna en existencia del artículo 999?",
            "expected_intent": "consultar_stock",
            "expected_entities": ["numero_pedido"],
            "min_confidence": 0.5,
            "description": "Pregunta con sinónimos (existencia)"
        },
        {
            "text": "tienen mercadería del producto XYZ123?",
            "expected_intent": "consultar_stock",
            "expected_entities": [],
            "min_confidence": 0.6,
            "description": "Pregunta con término formal (mercadería)"
        },
        # Edge cases
        {
            "text": "necesito saber si hay stock antes de comprar",
            "expected_intent": "consultar_stock",
            "expected_entities": [],
            "min_confidence": 0.6,
            "description": "Consulta con contexto de compra"
        },
    ],
    
    "CONSULTAR_PRECIO": [
        # Casos básicos
        {
            "text": "¿Cuánto cuesta el producto 12345?",
            "expected_intent": "consultar_precio",
            "expected_entities": ["numero_pedido"],
            "min_confidence": 0.7,
            "description": "Pregunta directa de precio"
        },
        {
            "text": "cuanto sale enviar a Córdoba?",
            "expected_intent": "consultar_precio",
            "expected_entities": [],
            "min_confidence": 0.6,
            "description": "Pregunta sobre costo de envío"
        },
        {
            "text": "cual es el valor de este artículo?",
            "expected_intent": "consultar_precio",
            "expected_entities": [],
            "min_confidence": 0.6,
            "description": "Pregunta con sinónimo (valor)"
        },
        # Variaciones informales
        {
            "text": "a cuanto estan las zapatillas?",
            "expected_intent": "consultar_precio",
            "expected_entities": [],
            "min_confidence": 0.5,
            "description": "Pregunta informal de precio"
        },
        {
            "text": "me decis qe precio tiene esto?",
            "expected_intent": "consultar_precio",
            "expected_entities": [],
            "min_confidence": 0.5,
            "description": "Pregunta muy informal"
        },
        # Con menciones de precio
        {
            "text": "este producto cuesta $5000?",
            "expected_intent": "consultar_precio",
            "expected_entities": ["precio"],
            "min_confidence": 0.6,
            "description": "Pregunta confirmando precio específico"
        },
    ],
    
    "CAMBIAR_PEDIDO": [
        # Casos básicos
        {
            "text": "quiero cancelar mi pedido 12345",
            "expected_intent": "cambiar_pedido",
            "expected_entities": ["numero_pedido"],
            "min_confidence": 0.7,
            "description": "Solicitud de cancelación"
        },
        {
            "text": "necesito modificar el pedido 999",
            "expected_intent": "cambiar_pedido",
            "expected_entities": ["numero_pedido"],
            "min_confidence": 0.7,
            "description": "Solicitud de modificación"
        },
        {
            "text": "me equivoqué en mi orden, puedo cambiarla?",
            "expected_intent": "cambiar_pedido",
            "expected_entities": [],
            "min_confidence": 0.6,
            "description": "Cambio por error"
        },
        # Edge cases
        {
            "text": "quiero devolver el producto que compré",
            "expected_intent": "cambiar_pedido",
            "expected_entities": [],
            "min_confidence": 0.6,
            "description": "Solicitud de devolución"
        },
        {
            "text": "anular pedido TRK-555 urgente",
            "expected_intent": "cambiar_pedido",
            "expected_entities": ["tracking_id"],
            "min_confidence": 0.7,
            "description": "Anulación urgente"
        },
    ],
    
    "QUEJA_RECLAMO": [
        # Casos básicos
        {
            "text": "tengo un problema con mi pedido",
            "expected_intent": "queja_reclamo",
            "expected_entities": [],
            "min_confidence": 0.6,
            "description": "Reporte de problema"
        },
        {
            "text": "esto es horrible, nunca me llega nada!",
            "expected_intent": "queja_reclamo",
            "expected_entities": [],
            "min_confidence": 0.7,
            "description": "Queja emocional"
        },
        {
            "text": "el producto llegó dañado y roto",
            "expected_intent": "queja_reclamo",
            "expected_entities": [],
            "min_confidence": 0.7,
            "description": "Reporte de daño"
        },
        # Casos intensos
        {
            "text": "pésimo servicio, quiero reclamar",
            "expected_intent": "queja_reclamo",
            "expected_entities": [],
            "min_confidence": 0.8,
            "description": "Queja fuerte"
        },
        {
            "text": "estoy muy enojado, esto es una estafa",
            "expected_intent": "queja_reclamo",
            "expected_entities": [],
            "min_confidence": 0.7,
            "description": "Queja muy fuerte con acusación"
        },
    ],
    
    "SALUDO": [
        # Casos básicos
        {
            "text": "Hola",
            "expected_intent": "saludo",
            "expected_entities": [],
            "min_confidence": 0.8,
            "description": "Saludo simple"
        },
        {
            "text": "Buenos días, ¿cómo están?",
            "expected_intent": "saludo",
            "expected_entities": [],
            "min_confidence": 0.8,
            "description": "Saludo formal"
        },
        {
            "text": "hla qe tal",
            "expected_intent": "saludo",
            "expected_entities": [],
            "min_confidence": 0.7,
            "description": "Saludo informal"
        },
        {
            "text": "buenas tardes",
            "expected_intent": "saludo",
            "expected_entities": [],
            "min_confidence": 0.8,
            "description": "Saludo de tarde"
        },
    ],
    
    "AGRADECIMIENTO": [
        # Casos básicos
        {
            "text": "Muchas gracias",
            "expected_intent": "agradecimiento",
            "expected_entities": [],
            "min_confidence": 0.8,
            "description": "Agradecimiento simple"
        },
        {
            "text": "Perfecto, gracias!",
            "expected_intent": "agradecimiento",
            "expected_entities": [],
            "min_confidence": 0.8,
            "description": "Agradecimiento con confirmación"
        },
        {
            "text": "Chau, hasta luego",
            "expected_intent": "agradecimiento",
            "expected_entities": [],
            "min_confidence": 0.8,
            "description": "Despedida"
        },
        {
            "text": "muy amable, nos vemos",
            "expected_intent": "agradecimiento",
            "expected_entities": [],
            "min_confidence": 0.8,
            "description": "Despedida cordial"
        },
    ],
    
    "EDGE_CASES": [
        # Casos ambiguos o complejos
        {
            "text": "hola, tienen stock del 12345? cuanto cuesta?",
            "expected_intent": "consultar_stock",  # Debería priorizar el primero
            "expected_entities": ["numero_pedido"],
            "min_confidence": 0.5,
            "description": "Múltiples intents en una frase"
        },
        {
            "text": "???",
            "expected_intent": "intencion_desconocida",
            "expected_entities": [],
            "min_confidence": 0.0,
            "description": "Solo símbolos"
        },
        {
            "text": "",
            "expected_intent": "intencion_desconocida",
            "expected_entities": [],
            "min_confidence": 0.0,
            "description": "Texto vacío"
        },
        {
            "text": "asdfghjklñ",
            "expected_intent": "intencion_desconocida",
            "expected_entities": [],
            "min_confidence": 0.0,
            "description": "Gibberish"
        },
        {
            "text": "hola buenos dias como estas todo bien? gracias chau",
            "expected_intent": "saludo",
            "expected_entities": [],
            "min_confidence": 0.5,
            "description": "Mezcla de saludos y despedidas"
        },
        {
            "text": "PEDIDO 111 TRACKING 222 ORDEN 333",
            "expected_intent": "trackear_pedido",
            "expected_entities": ["numero_pedido", "tracking_id"],
            "min_confidence": 0.6,
            "description": "Múltiples IDs en mayúsculas"
        },
    ]
}


# ============================================
# FUNCIONES DE PRUEBA
# ============================================

async def test_nlu_endpoint(text: str, user_id: str) -> Dict:
    """
    Prueba el endpoint NLU directamente.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                NLU_URL,
                json={
                    "text": text,
                    "channel_user_id": user_id
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


async def test_full_pipeline(text: str, user_id: str) -> Dict:
    """
    Prueba el pipeline completo (API -> NLU -> CORE).
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                API_URL,
                json={
                    "channel": "whatsapp",
                    "user_id": user_id,
                    "text": text
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


def evaluate_test_case(test_case: Dict, nlu_result: Dict, full_result: Dict) -> Dict:
    """
    Evalúa un caso de prueba contra los resultados obtenidos.
    """
    results = {
        "passed": True,
        "failures": [],
        "warnings": []
    }
    
    if "error" in nlu_result:
        results["passed"] = False
        results["failures"].append(f"NLU Error: {nlu_result['error']}")
        return results
    
    # Verificar intent
    actual_intent = nlu_result.get("intent", "")
    expected_intent = test_case["expected_intent"]
    
    if actual_intent != expected_intent:
        results["passed"] = False
        results["failures"].append(
            f"Intent incorrecto: esperado '{expected_intent}', obtenido '{actual_intent}'"
        )
    
    # Verificar confidence
    actual_confidence = nlu_result.get("confidence", 0.0)
    min_confidence = test_case["min_confidence"]
    
    if actual_confidence < min_confidence:
        results["warnings"].append(
            f"Confidence bajo: esperado ≥{min_confidence:.2f}, obtenido {actual_confidence:.2f}"
        )
    
    # Verificar entidades
    actual_entities = nlu_result.get("entities", [])
    expected_entity_labels = test_case["expected_entities"]
    actual_entity_labels = [e.get("label", "") for e in actual_entities]
    
    for expected_label in expected_entity_labels:
        if expected_label not in actual_entity_labels:
            results["warnings"].append(
                f"Entidad esperada '{expected_label}' no encontrada"
            )
    
    # Verificar que el pipeline completo funcione
    if "error" in full_result:
        results["warnings"].append(f"Pipeline completo falló: {full_result['error']}")
    elif full_result.get("status") == "error" and expected_intent not in ["intencion_desconocida", "queja_reclamo"]:
        results["warnings"].append("Pipeline devolvió error")
    
    return results


def print_test_result(category: str, test_case: Dict, nlu_result: Dict, evaluation: Dict):
    """
    Imprime el resultado de una prueba con formato colorido.
    """
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if evaluation["passed"] else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    
    print(f"\n{status} [{category}] {test_case['description']}")
    print(f"  📝 Input: {Colors.CYAN}{test_case['text']}{Colors.RESET}")
    print(f"  🎯 Intent: {Colors.YELLOW}{nlu_result.get('intent', 'N/A')}{Colors.RESET} (confidence: {nlu_result.get('confidence', 0.0):.2f})")
    
    if nlu_result.get('normalized_text'):
        print(f"  🧹 Normalizado: {nlu_result.get('normalized_text')}")
    
    if nlu_result.get("entities"):
        print(f"  🧠 Entidades: {nlu_result.get('entities')}")
    
    if evaluation["failures"]:
        for failure in evaluation["failures"]:
            print(f"    {Colors.RED}❌ {failure}{Colors.RESET}")
    
    if evaluation["warnings"]:
        for warning in evaluation["warnings"]:
            print(f"    {Colors.YELLOW}⚠️  {warning}{Colors.RESET}")


async def run_all_tests():
    """
    Ejecuta todos los casos de prueba.
    """
    print(f"{Colors.BOLD}{Colors.MAGENTA}")
    print("=" * 80)
    print("🧪 ORION NLU - SUITE DE PRUEBAS EXHAUSTIVAS")
    print("=" * 80)
    print(f"{Colors.RESET}\n")
    print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Objetivo: Probar el NLU mejorado en todos los escenarios posibles\n")
    
    total_tests = sum(len(cases) for cases in TEST_CASES.values())
    passed_tests = 0
    failed_tests = 0
    
    results_by_category = {}
    
    for category, test_cases in TEST_CASES.items():
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}")
        print(f"📂 CATEGORÍA: {category}")
        print(f"{'=' * 80}{Colors.RESET}")
        
        category_passed = 0
        category_failed = 0
        
        for i, test_case in enumerate(test_cases, 1):
            user_id = f"test_{category.lower()}_{i}"
            
            # Ejecutar pruebas
            nlu_result = await test_nlu_endpoint(test_case["text"], user_id)
            full_result = await test_full_pipeline(test_case["text"], user_id)
            
            # Evaluar
            evaluation = evaluate_test_case(test_case, nlu_result, full_result)
            
            # Imprimir resultado
            print_test_result(category, test_case, nlu_result, evaluation)
            
            # Contabilizar
            if evaluation["passed"]:
                passed_tests += 1
                category_passed += 1
            else:
                failed_tests += 1
                category_failed += 1
            
            # Pausa breve para no saturar
            await asyncio.sleep(0.1)
        
        results_by_category[category] = {
            "total": len(test_cases),
            "passed": category_passed,
            "failed": category_failed
        }
    
    # Resumen final
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}")
    print("=" * 80)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 80)
    print(f"{Colors.RESET}")
    
    for category, stats in results_by_category.items():
        success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        color = Colors.GREEN if success_rate >= 80 else Colors.YELLOW if success_rate >= 60 else Colors.RED
        
        print(f"\n{Colors.BOLD}{category}{Colors.RESET}")
        print(f"  Total: {stats['total']} | {Colors.GREEN}Pasados: {stats['passed']}{Colors.RESET} | {Colors.RED}Fallados: {stats['failed']}{Colors.RESET}")
        print(f"  {color}Tasa de éxito: {success_rate:.1f}%{Colors.RESET}")
    
    overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{Colors.BOLD}{'=' * 80}")
    print(f"RESULTADO FINAL")
    print(f"{'=' * 80}{Colors.RESET}")
    print(f"Total de pruebas: {total_tests}")
    print(f"{Colors.GREEN}✓ Pasadas: {passed_tests}{Colors.RESET}")
    print(f"{Colors.RED}✗ Falladas: {failed_tests}{Colors.RESET}")
    
    if overall_success_rate >= 90:
        verdict_color = Colors.GREEN
        verdict = "🎉 EXCELENTE - Sistema listo para producción"
    elif overall_success_rate >= 75:
        verdict_color = Colors.YELLOW
        verdict = "✅ BUENO - Sistema funcional con ajustes menores recomendados"
    elif overall_success_rate >= 60:
        verdict_color = Colors.YELLOW
        verdict = "⚠️  ACEPTABLE - Requiere mejoras antes de producción"
    else:
        verdict_color = Colors.RED
        verdict = "❌ INSUFICIENTE - Requiere trabajo significativo"
    
    print(f"\n{Colors.BOLD}{verdict_color}")
    print(f"Tasa de éxito general: {overall_success_rate:.1f}%")
    print(f"{verdict}")
    print(f"{Colors.RESET}")
    
    print(f"\n⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print("\n🚀 Iniciando suite de pruebas...\n")
    print("⚙️  Verificando servicios...")
    print("   - NLU Service: http://localhost:8001")
    print("   - API Gateway: http://localhost:8080")
    print("\n⏳ Ejecutando pruebas (esto puede tardar 1-2 minutos)...\n")
    
    asyncio.run(run_all_tests())
