# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planeado
- Integración con LLMs (GPT-4, Claude)
- Soporte multiidioma (inglés, portugués)
- Dashboard analítico con Grafana
- Auto-escalado con Kubernetes

---

## [1.0.0] - 2025-10-17

### 🎉 Lanzamiento Inicial

Primera versión estable de ORION, sistema inteligente de atención al cliente para e-commerce.

### Added ✨

#### NLU Service
- Sistema de clasificación de intenciones con 7 intents:
  - `trackear_pedido` - Rastreo de pedidos
  - `consultar_stock` - Consulta de disponibilidad
  - `consultar_precio` - Consulta de precios
  - `cambiar_pedido` - Modificación/cancelación
  - `queja_reclamo` - Quejas y reclamos
  - `saludo` - Saludos
  - `agradecimiento` - Agradecimientos y despedidas
- Normalización de texto con 25+ patrones
- Extracción de entidades (números de pedido, tracking IDs, precios, productos)
- Confidence scoring (0.0-1.0) para cada clasificación
- Modelo spaCy `es_core_news_sm` para procesamiento de lenguaje natural
- **Precisión: 97.8%** en suite de 46 tests

#### API Gateway
- Endpoint `/webhook/message` para recepción de mensajes
- Dashboard web en `/dashboard` para visualización de conversaciones
- Health checks en `/health`
- Integración con WhatsApp Business API
- Rate limiting y validación de webhooks
- Persistencia de conversaciones en MongoDB

#### Core Service
- Sistema de estrategias por intent (Strategy Pattern)
- 7 estrategias implementadas con respuestas contextuales
- Orquestación de llamadas a servicios externos
- Manejo de errores y fallbacks
- Logging estructurado

#### Integrations Service
- Mock de APIs de logística (Andreani, OCA)
- Sistema de notificaciones por email
- Endpoints de tracking, stock y precios
- Health checks y monitoring

#### Infrastructure
- Docker Compose para orquestación de 5 servicios
- MongoDB 8.0 para persistencia
- Arquitectura de microservicios escalable
- Hot-reload para desarrollo
- Health checks automáticos

#### Testing
- Suite estándar: 46 tests (97.8% success rate)
- Stress test: 59 casos extremos (100% uptime)
- Tests de integración end-to-end
- Coverage >80% en componentes críticos

#### Documentation
- README.md completo con diagramas de arquitectura
- CONTRIBUTING.md con guías de contribución
- LICENSE (MIT)
- Documentación de API con ejemplos
- Docstrings en todos los módulos principales

### Security 🔒
- Validación de inputs con Pydantic
- Sanitización contra SQL injection y XSS
- Timeouts configurables en todas las peticiones
- Manejo seguro de excepciones
- Variables de entorno para secretos

---

## [0.3.0] - 2025-10-15

### Added
- Estrategias para 5 nuevos intents
- Confidence scoring en clasificación
- Normalización de texto informal

### Fixed
- Template path en dashboard (500 → 200)
- Import errors en estrategias (Strategy → IntentStrategy)

---

## [0.2.0] - 2025-10-10

### Added
- NLU service con clasificación básica (2 intents)
- Integración con spaCy
- Extracción de entidades básica

### Changed
- Refactorización de arquitectura a microservicios

---

## [0.1.0] - 2025-10-01

### Added
- API Gateway inicial
- Estructura de proyecto con Docker
- MongoDB para persistencia
- Health checks básicos

---

## Formato de Versiones

### [Major.Minor.Patch]

- **Major**: Cambios incompatibles con versiones anteriores
- **Minor**: Nuevas funcionalidades compatibles hacia atrás
- **Patch**: Bug fixes compatibles hacia atrás

### Tipos de Cambios

- `Added` - Nuevas funcionalidades
- `Changed` - Cambios en funcionalidades existentes
- `Deprecated` - Funcionalidades que serán removidas
- `Removed` - Funcionalidades removidas
- `Fixed` - Bug fixes
- `Security` - Vulnerabilidades y parches de seguridad

---

## Links

- [Repositorio](https://github.com/tu-usuario/orion)
- [Issues](https://github.com/tu-usuario/orion/issues)
- [Pull Requests](https://github.com/tu-usuario/orion/pulls)
- [Releases](https://github.com/tu-usuario/orion/releases)
