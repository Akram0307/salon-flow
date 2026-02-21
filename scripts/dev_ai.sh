#!/bin/bash
# Start AI service locally connected to live backend

echo "🚀 Starting Salon Flow AI Service (Local Development)"
echo "================================================"
echo ""

# Check if .env.local exists
if [ ! -f "services/ai/.env.local" ]; then
    echo "❌ Error: services/ai/.env.local not found"
    echo "Please create it from .env.local.example"
    exit 1
fi

echo "✅ Environment file found"
echo "✅ Connecting to live backend: https://salon-flow-api-687369167038.asia-south1.run.app"
echo ""

# Start the service
cd services/ai
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
