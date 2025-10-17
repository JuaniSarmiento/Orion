# ============================================
# NLU Service - Dockerfile
# ============================================
# Docker image for spaCy-based NLU service
# ============================================

# Use official Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required by spaCy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
# This includes spaCy and the Spanish language model
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY ./app ./app

# Expose port 8000 for the NLU service
EXPOSE 8000

# Command to run the NLU service
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/app"]
