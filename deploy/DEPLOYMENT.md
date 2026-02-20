# Salon Flow API - Cloud Run Deployment Guide

Complete deployment guide for Salon Flow Backend on Google Cloud Run with cost optimization targeting **under ₹15,000/month**.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Step-by-Step Deployment](#step-by-step-deployment)
5. [CI/CD Setup](#cicd-setup)
6. [Cost Breakdown](#cost-breakdown)
7. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
8. [Security Best Practices](#security-best-practices)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Google Cloud Platform                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     │
│  │   Cloud Run  │────▶│   Firestore  │     │Secret Manager│     │
│  │  (API Service)│     │   (Database) │     │   (Secrets)  │     │
│  └──────────────┘     └──────────────┘     └──────────────┘     │
│         │                                          │             │
│         │                                          │             │
│         ▼                                          │             │
│  ┌──────────────┐                                  │             │
│  │   Firebase   │                                  │             │
│  │     Auth     │                                  │             │
│  └──────────────┘                                  │             │
│                                                    │             │
└────────────────────────────────────────────────────┼─────────────┘
                                                     │
                    ┌────────────────────────────────┘
                    │
                    ▼
           ┌──────────────┐
           │   Upstash    │
           │    Redis     │ (External - Serverless)
           └──────────────┘
```

### Components

| Component | Service | Purpose | Cost Impact |
|-----------|---------|---------|-------------|
| API Service | Cloud Run | FastAPI backend | Pay per request |
| Database | Firestore | Primary data store | Free tier + overages |
| Cache | Upstash Redis | Session & data caching | Free tier available |
| Auth | Firebase Auth | User authentication | Free |
| Secrets | Secret Manager | API keys, credentials | ~₹50/month |
| CI/CD | Cloud Build | Automated deployments | Free tier |

---

## Prerequisites

### Required Tools

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Install Docker
# Ubuntu/Debian
sudo apt-get install docker.io

# Verify installations
gcloud --version
docker --version
```

### Required Accounts

1. **GCP Project**: `salon-saas-487508` (already exists)
2. **Upstash Account**: [Sign up free](https://upstash.com)
3. **OpenRouter Account**: [Sign up](https://openrouter.ai)

### Required Permissions

Your GCP account needs these roles:
- `roles/run.admin`
- `roles/cloudbuild.builds.editor`
- `roles/iam.serviceAccountAdmin`
- `roles/secretmanager.admin`
- `roles/artifactregistry.admin`

---

## Quick Start

```bash
# 1. Navigate to project
cd /a0/usr/projects/salon_flow

# 2. Set environment variables
export GCP_JSON_KEY='$(cat services/api/gcp_credentials.json)'
export OPENROUTER_API_KEY='your-openrouter-key'
export UPSTASH_REDIS_URL='rediss://default:xxx@xxx.upstash.io:6379'

# 3. Run setup (first time only)
./deploy/deploy.sh --setup

# 4. Deploy
./deploy/deploy.sh --deploy
```

---

## Step-by-Step Deployment

### Step 1: Create Upstash Redis (Free Tier)

1. Go to [Upstash Console](https://console.upstash.io)
2. Create a new Redis database:
   - Name: `salon-flow-cache`
   - Region: `ap-south-1` (Mumbai - closest to GCP asia-south1)
   - Enable TLS: Yes
3. Copy the connection URL (format: `rediss://default:xxx@xxx.upstash.io:6379`)

```bash
# Save for later
export UPSTASH_REDIS_URL="rediss://default:YOUR_PASSWORD@YOUR_HOST.upstash.io:6379"
```

### Step 2: Configure GCP Secrets

```bash
# Create secrets in Secret Manager
echo "$GCP_JSON_KEY" | gcloud secrets create gcp-json-key \
    --data-file=- \
    --project=salon-saas-487508

echo "$OPENROUTER_API_KEY" | gcloud secrets create openrouter-api-key \
    --data-file=- \
    --project=salon-saas-487508

echo "$UPSTASH_REDIS_URL" | gcloud secrets create upstash-redis-url \
    --data-file=- \
    --project=salon-saas-487508
```

### Step 3: Enable GCP APIs

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    firestore.googleapis.com \
    --project=salon-saas-487508
```

### Step 4: Create Artifact Registry

```bash
gcloud artifacts repositories create salon-flow-images \
    --repository-format=docker \
    --location=asia-south1 \
    --description="Salon Flow Docker images" \
    --project=salon-saas-487508
```

### Step 5: Grant Service Account Permissions

```bash
PROJECT_NUMBER=$(gcloud projects describe salon-saas-487508 --format="value(projectNumber)")
SA_EMAIL="${PROJECT_NUMBER}@appspot.gserviceaccount.com"

# Grant required roles
gcloud projects add-iam-policy-binding salon-saas-487508 \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding salon-saas-487508 \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/datastore.user"

gcloud projects add-iam-policy-binding salon-saas-487508 \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.invoker"
```

### Step 6: Build and Deploy

```bash
# Configure Docker for Artifact Registry
gcloud auth configure-docker asia-south1-docker.pkg.dev

# Build image
docker build \
    -t asia-south1-docker.pkg.dev/salon-saas-487508/salon-flow-images/salon-flow-api:latest \
    -f services/api/Dockerfile.cloudrun \
    services/api

# Push image
docker push asia-south1-docker.pkg.dev/salon-saas-487508/salon-flow-images/salon-flow-api:latest

# Deploy to Cloud Run
gcloud run deploy salon-flow-api \
    --image=asia-south1-docker.pkg.dev/salon-saas-487508/salon-flow-images/salon-flow-api:latest \
    --region=asia-south1 \
    --platform=managed \
    --memory=512Mi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=300 \
    --set-env-vars="ENVIRONMENT=production,FIREBASE_PROJECT_ID=salon-saas-487508" \
    --set-secrets="GCP_JSON_KEY=gcp-json-key:latest,OPENROUTER_API_KEY=openrouter-api-key:latest,UPSTASH_REDIS_URL=upstash-redis-url:latest" \
    --allow-unauthenticated \
    --project=salon-saas-487508
```

### Step 7: Verify Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe salon-flow-api \
    --region=asia-south1 \
    --format="value(status.url)" \
    --project=salon-saas-487508)

# Test health endpoint
curl "${SERVICE_URL}/health"

# Expected response:
# {"status":"healthy","service":"api-service","version":"0.1.0","environment":"production","services":{"redis":"connected","firebase":"initialized"}}
```

---

## CI/CD Setup

### GitHub Actions (Recommended)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  PROJECT_ID: salon-saas-487508
  REGION: asia-south1
  SERVICE_NAME: salon-flow-api

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker
        run: gcloud auth configure-docker ${{ env.REGION }}-docker.pkg.dev

      - name: Build and Push
        run: |
          docker build \
            -t ${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/salon-flow-images/${{ env.SERVICE_NAME }}:${{ github.sha }} \
            -f services/api/Dockerfile.cloudrun \
            services/api
          docker push ${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/salon-flow-images/${{ env.SERVICE_NAME }}:${{ github.sha }}

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy ${{ env.SERVICE_NAME }} \
            --image=${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/salon-flow-images/${{ env.SERVICE_NAME }}:${{ github.sha }} \
            --region=${{ env.REGION }} \
            --platform=managed \
            --memory=512Mi \
            --cpu=1 \
            --min-instances=0 \
            --max-instances=10 \
            --set-env-vars="ENVIRONMENT=production,FIREBASE_PROJECT_ID=${{ env.PROJECT_ID }}" \
            --set-secrets="GCP_JSON_KEY=gcp-json-key:latest,OPENROUTER_API_KEY=openrouter-api-key:latest,UPSTASH_REDIS_URL=upstash-redis-url:latest" \
            --project=${{ env.PROJECT_ID }}
```

### Cloud Build (Alternative)

```bash
# Trigger build
gcloud builds submit \
    --config=cloudbuild.yaml \
    --project=salon-saas-487508
```

---

## Cost Breakdown

### Monthly Cost Estimate (₹)

| Service | Configuration | Free Tier | Estimated Cost |
|---------|--------------|-----------|----------------|
| **Cloud Run** | 512Mi, 1 CPU, Scale-to-zero | 2M requests, 360K GB-seconds | ₹0 - ₹500 |
| **Firestore** | Native mode | 50K reads, 20K writes/day | ₹0 - ₹200 |
| **Upstash Redis** | 10K commands/day | 10K commands/day free | ₹0 |
| **Secret Manager** | 4 secrets | 6 secret versions free | ₹0 - ₹50 |
| **Cloud Build** | 120 min/day | 120 min/day free | ₹0 |
| **Artifact Registry** | < 1GB | 500MB storage free | ₹0 - ₹100 |
| **Firebase Auth** | Unlimited | Free | ₹0 |
| **Network Egress** | < 1GB | 1GB free | ₹0 - ₹100 |
| **Total** | | | **₹0 - ₹950/month** |

### Cost Optimization Tips

1. **Scale to Zero**: `--min-instances=0` saves costs during idle periods
2. **Right-size Memory**: Start with 512Mi, increase only if needed
3. **Use Free Tiers**: Upstash, Firestore, Cloud Run all have generous free tiers
4. **Compress Responses**: GZip middleware reduces bandwidth costs
5. **Cache Aggressively**: Redis caching reduces Firestore reads

### Scaling Costs

| Requests/Day | Estimated Monthly Cost |
|--------------|----------------------|
| < 10,000 | ₹0 - ₹500 |
| 10,000 - 50,000 | ₹500 - ₹2,000 |
| 50,000 - 100,000 | ₹2,000 - ₹5,000 |
| 100,000+ | ₹5,000 - ₹15,000 |

---

## Monitoring & Troubleshooting

### View Logs

```bash
# Cloud Run logs
gcloud run logs read \
    --service=salon-flow-api \
    --region=asia-south1 \
    --project=salon-saas-487508

# Real-time logs
gcloud run logs tail \
    --service=salon-flow-api \
    --region=asia-south1 \
    --project=salon-saas-487508
```

### Check Service Status

```bash
# Service details
gcloud run services describe salon-flow-api \
    --region=asia-south1 \
    --project=salon-saas-487508

# Revisions list
gcloud run revisions list \
    --service=salon-flow-api \
    --region=asia-south1 \
    --project=salon-saas-487508
```

### Common Issues

#### 1. Cold Start Latency
**Symptom**: First request takes > 5 seconds
**Solution**: Enable CPU boost or set min-instances=1

```bash
gcloud run services update salon-flow-api \
    --region=asia-south1 \
    --min-instances=1 \
    --project=salon-saas-487508
```

#### 2. Redis Connection Failed
**Symptom**: "Redis connection failed" in logs
**Solution**: Check Upstash URL format and TLS

```bash
# Verify secret
gcloud secrets versions access latest \
    --secret=upstash-redis-url \
    --project=salon-saas-487508
```

#### 3. Permission Denied
**Symptom**: "Permission denied" accessing secrets
**Solution**: Verify service account roles

```bash
PROJECT_NUMBER=$(gcloud projects describe salon-saas-487508 --format="value(projectNumber)")
gcloud projects add-iam-policy-binding salon-saas-487508 \
    --member="serviceAccount:${PROJECT_NUMBER}@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

#### 4. Memory Exceeded
**Symptom**: Container terminated (OOMKilled)
**Solution**: Increase memory allocation

```bash
gcloud run services update salon-flow-api \
    --region=asia-south1 \
    --memory=1Gi \
    --project=salon-saas-487508
```

---

## Security Best Practices

### 1. Secret Management
- Never commit secrets to Git
- Use Secret Manager for all sensitive data
- Rotate secrets regularly

### 2. Network Security
- Use `--no-allow-unauthenticated` for internal APIs
- Add authentication middleware
- Validate JWT tokens on every request

### 3. IAM Least Privilege
- Grant minimum required roles
- Use service accounts with limited scope
- Audit permissions regularly

### 4. Container Security
- Run as non-root user (already configured)
- Use minimal base images
- Scan for vulnerabilities

```bash
# Enable Cloud Armor (optional)
gcloud compute security-policies create salon-flow-policy \
    --project=salon-saas-487508
```

---

## Rollback Procedure

```bash
# List revisions
gcloud run revisions list \
    --service=salon-flow-api \
    --region=asia-south1 \
    --project=salon-saas-487508

# Rollback to previous revision
gcloud run services update-traffic salon-flow-api \
    --to-revisions=salon-flow-api-00001-abc=100 \
    --region=asia-south1 \
    --project=salon-saas-487508
```

---

## Support

For issues or questions:
1. Check the [troubleshooting section](#monitoring--troubleshooting)
2. Review Cloud Run logs
3. Contact the development team

---

**Last Updated**: February 2026
**Version**: 1.0.0
