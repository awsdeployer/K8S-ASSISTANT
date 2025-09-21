# Use official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set workdir
WORKDIR /app

# Copy requirements and install in one layer
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy frontend (static files)
COPY frontend/ ../frontend/

# Change to non-root user
USER appuser

# Expose Flask port
EXPOSE 5000

# Start with Gunicorn (production-ready)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--worker-class", "gevent", "app:app"]
