# NLU Service

Natural Language Understanding microservice for the ORION project.

## Purpose

This service analyzes text messages to extract:
- User intents
- Named entities
- Semantic information

## Technology Stack

- **FastAPI**: Web framework
- **spaCy**: NLP engine
- **Spanish Model**: es_core_news_sm

## Running the Service

```bash
docker-compose up nlu
```

The service will be available at: http://localhost:8001
