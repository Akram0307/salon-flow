FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Cloud Run provides PORT environment variable (default 8080)
# The app must listen on the port provided by Cloud Run
ENV PORT=8080

# Run the application using the PORT environment variable
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
