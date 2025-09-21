# Use official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set workdir
WORKDIR /app

# Copy requirements and install in one layer
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy frontend (static files)
COPY frontend/ ../frontend/

# Expose Flask port
EXPOSE 5000

# Start with Gunicorn (production-ready)
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

