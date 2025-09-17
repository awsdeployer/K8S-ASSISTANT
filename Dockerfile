# Use lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (curl, etc.)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY backend/ ./backend/

# Copy frontend static files
COPY frontend/ ./frontend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Expose Flask app port
EXPOSE 5000

# Run Flask backend (which also serves frontend files)
CMD ["python", "backend/app.py"]

