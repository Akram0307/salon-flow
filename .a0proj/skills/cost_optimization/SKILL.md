# Cost Optimization Skill

## Overview
Implement cost optimization strategies to keep monthly costs under Rs 15,000 per salon.

## Target Budget
- **Maximum**: Rs 15,000/month per salon
- **Target**: Rs 3,000-5,000/month per salon

## Cost Breakdown

| Component | Target Cost | Strategy |
|-----------|-------------|----------|
| Cloud Run | Rs 0-1,800 | Scale-to-zero |
| Firestore | Rs 50 | Free tier |
| Storage | Rs 100 | CDN caching |
| Twilio | Rs 2,300 | Message batching |
| OpenRouter | Rs 750 | Response caching |

## Optimization Strategies

### 1. Scale-to-Zero
```yaml
annotations:
  autoscaling.knative.dev/minScale: "0"
  autoscaling.knative.dev/maxScale: "10"
```

### 2. AI Response Caching
- L1: In-memory cache (5 min TTL)
- L2: Firestore cache (24 hour TTL)
- Target: 70% cache hit rate

### 3. Free Tier Maximization
- Cloud Run: 2M requests/month free
- Firestore: 50K reads/day free
- Storage: 5GB free

## Monitoring
- Set up Cloud Billing alerts
- Review costs weekly
- Optimize based on usage patterns
