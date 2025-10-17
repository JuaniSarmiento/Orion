# ============================================
# CORE Service - Dockerfile
# ============================================
# Docker image for business logic orchestration
# ============================================

# Use official Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy requirements file first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY ./app ./app

# Expose port 8000 for the CORE service
EXPOSE 8000

# Command to run the CORE service
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/app"]
