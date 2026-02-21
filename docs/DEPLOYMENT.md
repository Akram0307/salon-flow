# Deployment Guide

This guide covers deploying Salon Flow to Google Cloud Platform (GCP).

## Prerequisites

- GCP Account with billing enabled
- `gcloud` CLI installed and authenticated
- Docker installed locally
- GitHub account (for CI/CD)

## Initial Setup

### 1. Enable GCP APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  firestore.googleapis.com \
  pubsub.googleapis.com \
  artifactregistry.googleapis.com
```

### 2. Create Artifact Registry

```bash
gcloud artifacts repositories create salon-flow \
  --repository-format=docker \
  --location=asia-south1 \
  --description="Salon Flow Docker images"
```

### 3. Create Secrets

```bash
# OpenRouter API Key
echo -n "your-openrouter-key" | gcloud secrets create openrouter-api-key --data-file=-

# Upstash Redis
echo -n "https://your-redis.upstash.io" | gcloud secrets create upstash-redis-url --data-file=-
echo -n "your-token" | gcloud secrets create upstash-redis-token --data-file=-

# Twilio
echo -n "your-account-sid" | gcloud secrets create twilio-account-sid --data-file=-
echo -n "your-auth-token" | gcloud secrets create twilio-auth-token --data-file=-
```

## Deploy Services

### Deploy API Service

```bash
cd /a0/usr/projects/salon_flow

gcloud builds submit \
  --config cloudbuild.yaml \
  --region asia-south1
```

### Deploy AI Service

```bash
gcloud builds submit \
  --config cloudbuild-ai.yaml \
  --region asia-south1
```

### Deploy Notification Service

```bash
gcloud builds submit \
  --config cloudbuild-notification.yaml \
  --region asia-south1
```

## Configure Cloud Run

### Set Environment Variables

```bash
# API Service
gcloud run services update salon-flow-api \
  --region=asia-south1 \
  --set-env-vars="GCP_PROJECT_ID=salon-saas-487508" \
  --set-secrets="OPENROUTER_API_KEY=openrouter-api-key:latest,UPSTASH_REDIS_REST_URL=upstash-redis-url:latest,UPSTASH_REDIS_REST_TOKEN=upstash-redis-token:latest"
```

### Grant Permissions

```bash
# Allow public access
gcloud run services add-iam-policy-binding salon-flow-api \
  --region=asia-south1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

## Verify Deployment

```bash
# Check service health
curl https://salon-flow-api-rgvcleapsa-el.a.run.app/health

# Check AI service
curl https://salon-flow-ai-rgvcleapsa-el.a.run.app/health
```

## CI/CD Pipeline

The project uses GitHub Actions for automated deployment:

1. Push to `main` branch triggers deployment
2. Pull requests run tests and linting
3. Tags create releases

### Required GitHub Secrets

- `GCP_PROJECT_ID`
- `GCP_SA_KEY` (Service Account JSON)
- `OPENROUTER_API_KEY`
- `UPSTASH_REDIS_REST_URL`
- `UPSTASH_REDIS_REST_TOKEN`

## Monitoring

### View Logs

```bash
gcloud logging read "resource.type=cloud_run_revision" --limit=50
```

### Check Metrics

Visit Cloud Console > Cloud Run > salon-flow-api > Metrics

## Troubleshooting

### Common Issues

1. **Cold Start Timeout**: First request may take 10-30 seconds
2. **Secret Not Found**: Verify secret names match exactly
3. **Permission Denied**: Check IAM roles for service account

### Useful Commands

```bash
# List services
gcloud run services list --region=asia-south1

# View service details
gcloud run services describe salon-flow-api --region=asia-south1

# View logs
gcloud logging tail "resource.type=cloud_run_revision"
```
