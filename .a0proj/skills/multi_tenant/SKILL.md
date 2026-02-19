# Multi-Tenant Architecture Skill

## Overview
Implement secure multi-tenant data isolation for the Salon SaaS platform.

## Tenant Isolation Strategy

### Shared Database, Logical Isolation
- All salons share the same Firestore database
- Each document includes salonId field
- Security rules enforce access control

### Data Access Pattern
```python
class TenantService:
    def __init__(self, salon_id: str):
        self.salon_id = salon_id

    def get_customers(self):
        return db.collection('customers').where('salonId', '==', self.salon_id).stream()
```

## Authentication Flow
```
1. User logs in via Firebase Auth
2. Custom claims set: { salonId: "xxx", role: "owner" }
3. All API calls include salonId from token
4. Firestore rules validate salonId matches
```

## Role-Based Access

| Role | Permissions |
|------|-------------|
| owner | Full access to salon |
| manager | Operations, staff management |
| receptionist | Bookings, customers |
| stylist | Own appointments, availability |
| customer | Own bookings, profile |
