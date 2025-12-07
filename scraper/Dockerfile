# Dockerfile for Scraper Service
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RUN_MODE=schedule

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY ../shared /app/shared

# Copy scraper source code
COPY scraper.py /app/

# Create necessary directories
RUN mkdir -p /app/logs

# Health check (check if process is running)
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD pgrep -f scraper.py || exit 1

# Run the scraper
CMD ["python", "scraper.py"]
