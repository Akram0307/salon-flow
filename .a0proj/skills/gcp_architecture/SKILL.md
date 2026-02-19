# GCP Architecture Skill

## Overview
Expert guidance for designing cost-optimized Google Cloud Platform architectures for the Salon SaaS project.

## Core Services

### Compute
- **Cloud Run**: Serverless containers with scale-to-zero
- **Cloud Functions**: Event-triggered lightweight compute
- **Cloud Build**: CI/CD pipeline execution

### Database
- **Firestore**: Native mode for real-time sync
- **Cloud Storage**: File and media storage

### Authentication
- **Firebase Auth**: Multi-provider authentication
- **Identity Platform**: Advanced identity management

### Messaging
- **Pub/Sub**: Event bus for microservices
- **Eventarc**: Cloud event routing

## Cost Optimization Strategies

1. **Scale-to-Zero**: Set minScale: 0 for Cloud Run
2. **Free Tier Maximization**: Stay within free tier limits
3. **Regional Deployment**: Single region (asia-south1) for lower costs
4. **Committed Use**: Consider committed use discounts for production

## Architecture Patterns

### Multi-Tenant Isolation
```
Collection: salons/{salonId}
Subcollections: customers, appointments, staff, services
```

### Event-Driven Flow
```
Service → Pub/Sub Topic → Subscriber Services
```

## Best Practices
- Use service accounts with minimal permissions
- Enable Cloud Audit Logs for compliance
- Set up budget alerts at 80% threshold
- Use Cloud CDN for static assets
