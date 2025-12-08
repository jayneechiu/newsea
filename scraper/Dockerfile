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

# Copy scraper package and templates
COPY scraper /app/scraper
COPY templates /app/templates

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r scraper/requirements.txt

# Create necessary directories
RUN mkdir -p /app/data/logs /app/data/database

# Health check (check if process is running)
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD pgrep -f "python -m scraper.main" || exit 1

# Run the scraper
CMD ["python", "-m", "scraper.main"]
