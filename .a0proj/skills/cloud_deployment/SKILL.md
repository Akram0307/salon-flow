# Cloud Deployment Skill

## Overview
Deploy services to GCP Cloud Run with cost-optimized configuration.

## Service Configuration
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: salon-api
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containers:
      - image: gcr.io/PROJECT_ID/salon-api
        resources:
          limits:
            cpu: "1000m"
            memory: "512Mi"
```

## Deployment Commands
```bash
gcloud run deploy salon-api   --source ./api   --region asia-south1   --allow-unauthenticated   --min-instances 0   --max-instances 10   --memory 512Mi   --cpu 1
```

## Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
```
