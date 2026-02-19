# Automated Testing Skill

## Overview
Implement comprehensive automated testing for the Salon SaaS platform.

## Testing Pyramid
```
        /\
       /  \  E2E Tests (Playwright)
      /────\
     /      \  Integration Tests
    /────────\
   /          \  Unit Tests (Jest/Pytest)
  /────────────\
```

## Unit Tests

### Frontend (Jest)
```typescript
describe('BookingService', () => {
  it('should create appointment', async () => {
    const booking = await BookingService.create({
      serviceId: 'haircut',
      date: '2024-01-20',
      time: '15:00'
    })
    expect(booking.id).toBeDefined()
  })
})
```

### Backend (Pytest)
```python
def test_create_appointment(client, auth_headers):
    response = client.post(
        "/api/v1/appointments",
        json={"service_id": "haircut", "date": "2024-01-20"},
        headers=auth_headers
    )
    assert response.status_code == 201
```

## Coverage Target
- Unit Tests: 80%+
- Integration Tests: 60%+
- E2E Tests: Critical paths
