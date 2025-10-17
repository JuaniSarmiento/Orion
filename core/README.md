# CORE Service

Business logic orchestration layer for the ORION project.

## Purpose

This service acts as the central orchestrator that:
- Receives NLU-processed data (intents + entities)
- Executes appropriate business logic strategies
- Coordinates actions across different systems
- Routes requests to specialized handlers

## Technology Stack

- **FastAPI**: Web framework
- **Pydantic**: Data validation

## Running the Service

```bash
docker-compose up core
```

The service will be available at: http://localhost:8002

## Architecture Role

```
API Gateway → NLU Service → CORE Service → External APIs/Services
```

The CORE service is the decision maker and action executor.
