#!/bin/bash
set -e

echo "Building and deploying Owner PWA to Cloud Run..."

cd /a0/usr/projects/salon_flow/apps/owner

# Build with production environment using CORRECT API URLs (with /api/v1 suffix)
echo "Building production bundle..."
VITE_API_URL=https://salon-flow-api-687369167038.asia-south1.run.app/api/v1 \
VITE_AI_URL=https://salon-flow-ai-1071648642857.asia-south1.run.app \
npm run build

# Create Cloud Run compatible Dockerfile if not exists
if [ ! -f Dockerfile.cloudrun ]; then
cat > Dockerfile.cloudrun << 'DOCKEREOF'
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY dist /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1
CMD ["nginx", "-g", "daemon off;"]
DOCKEREOF
fi

# Build and push to Cloud Run with CORRECT environment variables (with /api/v1 suffix)
echo "Deploying to Cloud Run..."
gcloud run deploy salon-flow-owner \
  --source . \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --concurrency 100 \
  --max-instances 10 \
  --set-env-vars VITE_API_URL=https://salon-flow-api-687369167038.asia-south1.run.app/api/v1 \
  --set-env-vars VITE_AI_URL=https://salon-flow-ai-1071648642857.asia-south1.run.app

echo "✓ Deployment complete!"
echo "Owner PWA URL: https://salon-flow-owner-687369167038.asia-south1.run.app"
