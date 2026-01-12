# Dockerfile for V2 API Service (flattened under backend/api)
FROM python:3.11-slim

WORKDIR /app

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# System deps
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy backend and templates
COPY backend /app/backend
COPY templates /app/templates
COPY .env /app/.env

# Install Python deps
COPY backend/api/requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create logs dir
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
