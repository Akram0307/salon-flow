# API Design Skill

## Overview
Design RESTful APIs for the Salon SaaS platform following industry best practices.

## API Structure

### Base URL
```
https://api.salonsaas.com/v1
```

### Resource Endpoints
```
/salons/{salonId}
/salons/{salonId}/customers
/salons/{salonId}/appointments
/salons/{salonId}/staff
/salons/{salonId}/services
/salons/{salonId}/analytics
```

## Request/Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "abc-123"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid phone number format",
    "details": { ... }
  }
}
```

## Authentication
- Bearer token in Authorization header
- Firebase ID Token for user requests
- Service Account for internal services

## Rate Limiting
- 100 requests/minute per user
- 1000 requests/minute per salon
