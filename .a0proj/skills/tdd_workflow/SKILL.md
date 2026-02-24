# TDD Workflow Skill

## Overview
Test-Driven Development workflow for Salon_Flow. Write tests first, then implement. Enforce the RED-GREEN-REFACTOR cycle.

## Philosophy
> "Tests are not about finding bugs. They're about designing code that works."

## The RED-GREEN-REFACTOR Cycle

```
    ┌─────────────────────────────────────────┐
    │                                         │
    ▼                                         │
┌────────┐    ┌────────┐    ┌──────────┐     │
│  RED   │───▶│ GREEN  │───▶│ REFACTOR │─────┘
└────────┘    └────────┘    └──────────┘
    │              │              │
    │              │              │
    ▼              ▼              ▼
Write         Write         Improve
test first    minimal       design
(fails)       code (passes) without
                            breaking
```

## Phase 1: RED 🔴

### Write a Failing Test

**Before writing any implementation code:**

1. **Understand the requirement** - What should this code do?
2. **Write the test** - Express the requirement as a test
3. **Run the test** - Confirm it fails for the right reason
4. **Commit the test** - Version control the failing test

**Example: Booking Availability**

```python
# tests/api/test_bookings.py

def test_get_available_slots_returns_correct_times(client, auth_headers):
    """Test that available slots are returned for a given date."""
    # Arrange
    salon_id = "salon_123"
    staff_id = "staff_456"
    date = "2024-01-20"
    
    # Act
    response = client.get(
        f"/api/v1/bookings/available-slots?salon_id={salon_id}&staff_id={staff_id}&date={date}",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "slots" in data
    assert len(data["slots"]) > 0
    # Each slot should have time and availability
    for slot in data["slots"]:
        assert "time" in slot
        assert "available" in slot
```

**Run and confirm failure:**
```bash
pytest tests/api/test_bookings.py::test_get_available_slots_returns_correct_times -v
# FAILED - endpoint doesn't exist yet
```

## Phase 2: GREEN 🟢

### Write Minimal Code to Pass

**Write only enough code to make the test pass:**

1. **Implement the minimum** - Don't add extra features
2. **Run the test** - Confirm it passes
3. **No refactoring yet** - Just make it work

**Example Implementation:**

```python
# services/api/app/routers/bookings.py

@router.get("/available-slots")
async def get_available_slots(
    salon_id: str,
    staff_id: str,
    date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available booking slots for a staff member on a date."""
    # Minimal implementation to pass test
    slots = generate_time_slots(date)
    return {"slots": [{"time": slot, "available": True} for slot in slots]}


def generate_time_slots(date: str) -> list[str]:
    """Generate 30-minute slots from 9 AM to 5 PM."""
    slots = []
    for hour in range(9, 17):
        slots.append(f"{hour:02d}:00")
        slots.append(f"{hour:02d}:30")
    return slots
```

**Run and confirm pass:**
```bash
pytest tests/api/test_bookings.py::test_get_available_slots_returns_correct_times -v
# PASSED
```

## Phase 3: REFACTOR 🔵

### Improve the Design

**Now improve the code without changing behavior:**

1. **Clean up the code** - Better names, structure
2. **Remove duplication** - DRY principle
3. **Run tests after each change** - Ensure nothing breaks
4. **Commit working refactored code**

**Example Refactoring:**

```python
# services/api/app/routers/bookings.py

from services.booking import BookingService

@router.get("/available-slots")
async def get_available_slots(
    salon_id: str,
    staff_id: str,
    date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available booking slots for a staff member on a date."""
    service = BookingService(db)
    available_slots = await service.get_available_slots(
        tenant_id=current_user.tenant_id,
        staff_id=staff_id,
        date=date
    )
    return {"slots": available_slots}


# services/api/app/services/booking.py

class BookingService:
    """Service for booking operations."""
    
    SALON_HOURS = (9, 17)  # 9 AM to 5 PM
    SLOT_DURATION_MINUTES = 30
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_available_slots(
        self,
        tenant_id: str,
        staff_id: str,
        date: str
    ) -> list[dict]:
        """Get available time slots, excluding booked times."""
        all_slots = self._generate_time_slots()
        booked_slots = await self._get_booked_slots(tenant_id, staff_id, date)
        
        return [
            {"time": slot, "available": slot not in booked_slots}
            for slot in all_slots
        ]
    
    def _generate_time_slots(self) -> list[str]:
        """Generate time slots based on salon hours."""
        slots = []
        for hour in range(*self.SALON_HOURS):
            slots.append(f"{hour:02d}:00")
            slots.append(f"{hour:02d}:30")
        return slots
    
    async def _get_booked_slots(
        self,
        tenant_id: str,
        staff_id: str,
        date: str
    ) -> set[str]:
        """Get set of booked time slots."""
        bookings = self.db.query(Booking).filter(
            Booking.tenant_id == tenant_id,
            Booking.staff_id == staff_id,
            Booking.date == date
        ).all()
        return {b.time for b in bookings}
```

**Run tests after each refactor step:**
```bash
pytest tests/api/test_bookings.py -v
# All tests still passing
```

## Test Categories

### Unit Tests
```python
# Test a single function/method
def test_generate_time_slots():
    service = BookingService(mock_db)
    slots = service._generate_time_slots()
    assert len(slots) == 16  # 8 hours * 2 slots
    assert "09:00" in slots
    assert "16:30" in slots
```

### Integration Tests
```python
# Test multiple components together
def test_booking_flow_creates_appointment(client, auth_headers):
    # Get available slots
    slots_resp = client.get("/api/v1/bookings/available-slots?...")
    slot = slots_resp.json()["slots"][0]
    
    # Book the slot
    booking_resp = client.post(
        "/api/v1/bookings",
        json={"slot": slot["time"], ...},
        headers=auth_headers
    )
    
    # Verify booking created
    assert booking_resp.status_code == 201
```

### E2E Tests
```typescript
// Test complete user workflow
import { test, expect } from '@playwright/test';

test('client can book an appointment', async ({ page }) => {
  await page.goto('/booking');
  await page.getByRole('button', { name: /select service/i }).click();
  await page.getByText('Haircut').click();
  await page.getByRole('button', { name: /select time/i }).click();
  await page.getByText('10:00 AM').click();
  await page.getByRole('button', { name: /confirm booking/i }).click();
  
  await expect(page.getByText('Booking confirmed')).toBeVisible();
});
```

## Testing Anti-Patterns

### ❌ Don't Do This

```python
# Testing implementation details
def test_internal_method():
    service = BookingService(db)
    assert service._internal_cache == {}  # Bad: tests private state

# Testing without assertions
def test_something():
    result = do_something()
    # No assertions - test always passes!

# Over-mocking
def test_with_too_many_mocks():
    mock_a = Mock()
    mock_b = Mock()
    mock_c = Mock()
    # Testing mocks, not real code

# Brittle selectors
await page.locator('#btn-submit-123').click()  # ID might change
```

### ✅ Do This Instead

```python
# Test behavior, not implementation
def test_booking_is_created():
    service = BookingService(db)
    booking = service.create_booking(...)
    assert booking.id is not None
    assert booking.status == "confirmed"

# Clear assertions
def test_something():
    result = do_something()
    assert result.status == "success"
    assert result.data is not None

# Minimal mocking
def test_with_focused_mocks():
    mock_db = Mock()
    service = BookingService(mock_db)
    # Only mock external dependencies

# Resilient selectors
await page.getByRole('button', { name: /confirm/i }).click()
```

## TDD Workflow Commands

```bash
# Run specific test (RED phase)
pytest tests/api/test_bookings.py::test_name -v

# Run all tests in file
pytest tests/api/test_bookings.py -v

# Run with coverage
pytest --cov=app tests/

# Run E2E tests
npx playwright test --project=chromium

# Watch mode for development
pytest -x --tb=short tests/
```

## Salon Context Test Examples

### Multi-Tenant Isolation
```python
def test_tenant_isolation(client):
    """Ensure users can only see their own tenant's data."""
    # Create booking for tenant A
    headers_a = auth_headers_for_tenant("tenant_a")
    booking_a = client.post("/api/v1/bookings", json={...}, headers=headers_a)
    
    # Try to access from tenant B
    headers_b = auth_headers_for_tenant("tenant_b")
    response = client.get(f"/api/v1/bookings/{booking_a.json()['id']}", headers=headers_b)
    
    assert response.status_code == 404  # Not found, not 403 (no info leak)
```

### Timezone Handling
```python
def test_booking_timezone_aware():
    """Bookings should be stored in UTC, displayed in local time."""
    # Book in local time (EST)
    booking = create_booking(time="14:00", timezone="America/New_York")
    
    # Stored in UTC
    assert booking.time_utc == "19:00"  # 14:00 EST = 19:00 UTC
```

## Best Practices

✅ Write the test first, always
✅ Test behavior, not implementation
✅ One assertion per test (when possible)
✅ Use descriptive test names
✅ Keep tests independent
✅ Run tests frequently
✅ Maintain test coverage > 80%

## Anti-Patterns

❌ Writing tests after the code
❌ Skipping tests to "save time"
❌ Testing private methods directly
❌ Over-mocking to the point of testing mocks
❌ Ignoring failing tests
❌ Committing without running tests
