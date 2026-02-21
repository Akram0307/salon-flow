# Salon Flow API Documentation

## Base URL

- **Production**: `https://salon-flow-api-rgvcleapsa-el.a.run.app`
- **Local**: `http://localhost:8000`

## Authentication

All API requests require JWT authentication via Firebase:

```bash
Authorization: Bearer <firebase_jwt_token>
```

## Rate Limits

- **Standard endpoints**: 100 requests/minute
- **AI endpoints**: 20 requests/minute
- **Auth endpoints**: 10 requests/minute

## Response Format

All responses follow this structure:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

Error responses:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": { ... }
  }
}
```

## Modules

- [Authentication](./authentication.md)
- [Tenants](./tenants.md)
- [Customers](./customers.md)
- [Bookings](./bookings.md)
- [Staff](./staff.md)
- [Services](./services.md)
- [AI](./ai.md)

## Interactive Documentation

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`
