# ============================================
# ORION Project - Dockerfile
# ============================================
# Multi-stage optimized Docker image for FastAPI application
# ============================================

# Use official Python 3.11 slim image as base
# Slim variant provides a good balance between size and functionality
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Set environment variables
# Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONUNBUFFERED=1

# Install system dependencies (if needed in the future)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     && rm -rf /var/lib/apt/lists/*

# Copy requirements file first for better Docker layer caching
# This way, dependencies are only reinstalled if requirements.txt changes
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir reduces image size by not caching pip packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
# This comes AFTER installing dependencies to leverage Docker cache
COPY ./app ./app

# Expose port 8000 for the application
EXPOSE 8000

# Command to run the application
# --reload: Auto-reload on code changes (development mode)
# --host 0.0.0.0: Make server accessible from outside the container
# --port 8000: Listen on port 8000
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/app"]
