# Monitoring and Observability Skill

## Overview
Set up comprehensive monitoring and observability for the Salon SaaS platform.

## Monitoring Stack

| Component | Tool | Purpose |
|-----------|------|--------|
| Metrics | Cloud Monitoring | Performance metrics |
| Logs | Cloud Logging | Application logs |
| Traces | Cloud Trace | Request tracing |
| Alerts | Cloud Alerting | Incident notification |

## Key Metrics

### Application Metrics
- Request latency (p50, p95, p99)
- Error rate
- Requests per second
- Active connections

### Business Metrics
- Bookings per hour
- Active users
- Revenue per day
- AI cache hit rate

### Cost Metrics
- Cloud Run instances
- Firestore reads/writes
- AI API calls
- Storage usage

## Alert Policies
```hcl
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High Error Rate"
  conditions {
    condition_threshold {
      threshold_value = 5
      duration = "300s"
    }
  }
}
```
