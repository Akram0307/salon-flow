# API Reference - Salon_Flow

## Authentication

### POST /api/auth/login
- Login with email/password
- Returns: `{ access_token, token_type, user }`

### POST /api/auth/register
- Register new tenant owner
- Creates tenant and admin user
- Returns: `{ access_token, token_type, user, tenant }`

### POST /api/auth/refresh
- Refresh access token
- Returns: `{ access_token, token_type }`

## Tenants

### GET /api/tenants
- List all tenants (admin only)

### GET /api/tenants/{tenant_id}
- Get tenant details

### POST /api/tenants
- Create new tenant

### PUT /api/tenants/{tenant_id}
- Update tenant

## Staff Management

### GET /api/staff
- List all staff for tenant

### POST /api/staff
- Add new staff member
- Creates user account

### GET /api/staff/{staff_id}
- Get staff details

### PUT /api/staff/{staff_id}
- Update staff information

### DELETE /api/staff/{staff_id}
- Deactivate staff member

## Services

### GET /api/services
- List all services for tenant

### POST /api/services
- Create new service

### PUT /api/services/{service_id}
- Update service

### DELETE /api/services/{service_id}
- Delete service

## Bookings

### GET /api/bookings
- List bookings with filters
- Query params: `start_date`, `end_date`, `staff_id`, `status`

### POST /api/bookings
- Create new booking
- Validates conflicts and availability

### GET /api/bookings/{booking_id}
- Get booking details

### PUT /api/bookings/{booking_id}
- Update booking
- Handles rescheduling logic

### DELETE /api/bookings/{booking_id}
- Cancel booking

## Customers

### GET /api/customers
- List all customers

### POST /api/customers
- Create customer

### GET /api/customers/{customer_id}
- Get customer with booking history

### PUT /api/customers/{customer_id}
- Update customer

## Onboarding

### POST /api/onboarding
- Complete onboarding wizard
- Creates salon, services, staff, hours

### GET /api/onboarding/status
- Check onboarding completion status

## Analytics

### GET /api/analytics/dashboard
- Get dashboard metrics

### GET /api/analytics/revenue
- Revenue reports
- Query params: `period`, `start_date`, `end_date`

### GET /api/analytics/staff-performance
- Staff performance metrics

## AI Service

### POST /api/ai/chat
- AI assistant chat endpoint

### POST /api/ai/analytics
- Generate AI insights

### POST /api/ai/forecast
- Revenue forecasting
