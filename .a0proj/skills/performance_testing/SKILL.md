# Performance Testing Skill

## Overview
Implement performance testing to ensure optimal user experience.

## Performance Targets

| Metric | Target |
|--------|--------|
| First Contentful Paint | < 1.5s |
| Largest Contentful Paint | < 2.5s |
| Time to Interactive | < 3.5s |
| Cumulative Layout Shift | < 0.1 |
| API Response Time | < 200ms |

## Lighthouse CI
```yaml
- name: Run Lighthouse
  uses: treosh/lighthouse-ci-action@v10
  with:
    urls: |
      https://client.salonsaas.com
      https://staff.salonsaas.com
```

## Load Testing
```python
from locust import HttpUser, task, between

class SalonUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_appointments(self):
        self.client.get("/api/v1/appointments")
```

## Performance Optimization
- Code splitting by route
- Image optimization
- Service worker caching
- Lazy loading components
