# INTEGRATIONS Service

External API abstraction layer for the ORION project.

## Purpose

This service provides a unified interface for all external system integrations:
- Inventory/Stock management systems (Franco's system)
- Logistics and shipping APIs
- Payment gateways
- CRM systems
- Any third-party service

## Benefits

- **Abstraction**: CORE service doesn't need to know API details
- **Maintainability**: Changes to external APIs only affect this service
- **Reusability**: Multiple services can use these integrations
- **Testability**: Easy to mock external API responses
- **Monitoring**: Centralized logging of external API calls

## Technology Stack

- **FastAPI**: Web framework
- **HTTPX**: Async HTTP client for external API calls
- **Pydantic**: Data validation

## Running the Service

```bash
docker-compose up integrations
```

The service will be available at: http://localhost:8003

## Available Endpoints

### Stock Management
- `GET /stock/{product_id}` - Check product availability

### Health Check
- `GET /health` - Service status
