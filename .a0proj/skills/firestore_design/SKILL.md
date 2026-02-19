# Firestore Database Design Skill

## Overview
Design efficient Firestore schemas for the multi-tenant Salon SaaS platform.

## Collection Structure
```
salons/{salonId}
├── customers/{customerId}
├── staff/{staffId}
├── services/{serviceId}
├── appointments/{appointmentId}
├── memberships/{membershipId}
├── inventory/{itemId}
└── settings/{settingKey}

users/{userId}  # Global user profiles
```

## Document Schemas

### Customer
```typescript
interface Customer {
  id: string
  salonId: string
  name: string
  phone: string
  gender: 'male' | 'female'
  dob?: string
  loyaltyPoints: number
  membershipId?: string
  totalVisits: number
  totalSpent: number
  lastVisit?: Timestamp
}
```

### Appointment
```typescript
interface Appointment {
  id: string
  salonId: string
  customerId: string
  staffId: string
  serviceId: string
  date: string
  startTime: string
  endTime: string
  status: 'booked' | 'checked-in' | 'in-progress' | 'completed' | 'cancelled'
  price: number
}
```

## Security Rules
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /salons/{salonId} {
      allow read, write: if request.auth.token.salonId == salonId;
    }
  }
}
```
