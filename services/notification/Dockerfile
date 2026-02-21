# Salon Flow Notification Service
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PORT=8002

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
