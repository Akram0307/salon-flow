# Security Testing Skill

## Overview
Implement security testing to protect the platform and user data.

## Security Checklist

### Authentication
- Strong password policy
- MFA support
- Session timeout
- Secure token storage

### Authorization
- Role-based access control
- Resource-level permissions
- API rate limiting
- Input validation

### Data Protection
- Encryption at rest
- Encryption in transit
- PII handling
- Data retention policies

## OWASP Top 10 Tests
```python
def test_sql_injection(client):
    response = client.get("/api/customers?id=1' OR '1'='1")
    assert response.status_code == 400

def test_xss(client):
    response = client.post("/api/customers", json={
        "name": "<script>alert('xss')</script>"
    })
    assert "<script>" not in response.json()["data"]["name"]
```

## Dependency Scanning
```yaml
- name: Security Scan
  uses: snyk/actions/python@master
```
