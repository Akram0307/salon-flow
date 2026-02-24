# Database Schema - Salon_Flow

## Overview
Multi-tenant SaaS database using Supabase PostgreSQL with RLS (Row Level Security) policies.

## Core Tables

### tenants
- `id` (UUID, PK)
- `name` (text)
- `slug` (text, unique)
- `status` (enum: active, suspended, trial)
- `subscription_tier` (enum: basic, pro, enterprise)
- `settings` (JSONB)
- `created_at`, `updated_at` (timestamps)

### users
- `id` (UUID, PK)
- `tenant_id` (UUID, FK → tenants.id)
- `email` (text, unique per tenant)
- `role` (enum: owner, manager, staff, client)
- `status` (enum: active, inactive, invited)
- `profile` (JSONB)
- `last_login_at` (timestamp)

### staff
- `id` (UUID, PK)
- `tenant_id` (UUID, FK)
- `user_id` (UUID, FK → users.id)
- `skills` (text[])
- `schedule_type` (enum: full_time, part_time, contract)
- `commission_rate` (decimal)
- `bio`, `photo_url`

### services
- `id` (UUID, PK)
- `tenant_id` (UUID, FK)
- `name`, `description`
- `duration` (minutes)
- `base_price` (decimal)
- `category` (enum)
- `color` (for calendar display)
- `is_active` (boolean)

### bookings
- `id` (UUID, PK)
- `tenant_id` (UUID, FK)
- `customer_id` (UUID, FK → customers.id)
- `staff_id` (UUID, FK → staff.id)
- `service_ids` (UUID[])
- `start_time`, `end_time` (timestamps)
- `status` (enum: pending, confirmed, in_progress, completed, cancelled, no_show)
- `notes`, `total_price`

### customers
- `id` (UUID, PK)
- `tenant_id` (UUID, FK)
- `user_id` (UUID, FK → users.id, nullable)
- `phone`, `email`
- `preferences` (JSONB)
- `visit_count`, `last_visit_at`

### business_hours
- `id` (UUID, PK)
- `tenant_id` (UUID, FK)
- `day_of_week` (0-6)
- `open_time`, `close_time` (time)
- `is_open` (boolean)
- `is_special` (boolean) - for holidays

## RLS Policies

### Tenant Isolation
All tables have `tenant_id` with RLS enabled:
```sql
CREATE POLICY "Tenant isolation" ON table_name
FOR ALL USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

### Owner Access
Owners can access all data within their tenant:
```sql
CREATE POLICY "Owner full access" ON table_name
FOR ALL USING (
  EXISTS (
    SELECT 1 FROM users 
    WHERE users.id = auth.uid() 
    AND users.role = 'owner'
  )
);
```

## Indexes

### Performance
- `bookings(start_time, end_time)`
- `bookings(staff_id, start_time)`
- `bookings(customer_id)`
- `staff(tenant_id)`
- `services(tenant_id)`
- `customers(phone)` - for quick lookup

## Relationships

```
tenants
├── users (1:N)
├── staff (1:N) → users (1:1)
├── services (1:N)
├── bookings (1:N) → customers, staff
├── customers (1:N)
└── business_hours (1:N)
```

## Common Queries

### Get staff with bookings today
```sql
SELECT s.*, COUNT(b.id) as booking_count
FROM staff s
LEFT JOIN bookings b ON b.staff_id = s.id
AND DATE(b.start_time) = CURRENT_DATE
WHERE s.tenant_id = :tenant_id
GROUP BY s.id;
```

### Get available slots
```sql
SELECT generate_series(
  :start_time,
  :end_time,
  '30 minutes'::interval
) as slot_time
WHERE NOT EXISTS (
  SELECT 1 FROM bookings b
  WHERE b.staff_id = :staff_id
  AND b.start_time <= slot_time
  AND b.end_time > slot_time
  AND b.status NOT IN ('cancelled', 'no_show')
);
```
