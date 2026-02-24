# Salon Flow - Onboarding Flow Documentation

## Overview

The onboarding system allows salon owners to set up their salon and configure initial data through a step-by-step process.

## API Endpoints

### Base URL: `/api/v1/onboarding`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/create-salon` | POST | Create a new salon with owner |
| `/join-salon` | POST | Join existing salon with invite code |
| `/status` | GET | Get current onboarding status |
| `/complete` | POST | Mark onboarding as complete |
| `/service-templates` | GET | Get available service templates |
| `/import-services` | POST | Import services from templates |
| `/layout` | POST | Configure salon layout |
| `/staff` | POST | Add staff member |
| `/business-hours` | POST | Set business hours |
| `/invite-codes` | GET | Get salon invite codes |

## Onboarding Steps

### Step 1: Create Salon

**Endpoint:** `POST /api/v1/onboarding/create-salon`

**Request Body:**
```json
{
  "name": "Jawed Habib Hair & Beauty",
  "address": {
    "street": "Shop No. 12, SV Complex",
    "area": "Budhawarpet",
    "city": "Kurnool",
    "state": "Andhra Pradesh",
    "pincode": "518003",
    "country": "India"
  },
  "phone": "+918522123456",
  "email": "kurnool@jawedhabib.co.in",
  "gst_number": "37AABCH1234P1ZA"
}
```

**Response:**
```json
{
  "salon_id": "salon_i21hfzhdue4418t1sw2m",
  "invite_code": "T2SGFX18",
  "message": "Salon created successfully"
}
```

### Step 2: Configure Layout

**Endpoint:** `POST /api/v1/onboarding/layout`

**Request Body:**
```json
{
  "mens_chairs": 6,
  "womens_chairs": 4,
  "service_rooms": 4,
  "bridal_room": 1,
  "spa_room": 1
}
```

### Step 3: Import Services

**Endpoint:** `POST /api/v1/onboarding/import-services`

**Request Body:**
```json
{
  "template_type": "salon",
  "categories": ["hair_cuts", "hair_color", "hair_treatments"]
}
```

**Available Categories:**
- `hair_cuts` - Men's, Women's, Kids hair cuts
- `hair_color` - Coloring, highlights, balayage
- `hair_treatments` - Keratin, spa, treatments
- `styling` - Blow dry, curling, party styling
- `facial_skin` - Facials, cleanups, skin treatments
- `spa` - Massage, manicure, pedicure, waxing
- `bridal` - Bridal makeup and packages
- `groom` - Groom packages

### Step 4: Add Staff

**Endpoint:** `POST /api/v1/onboarding/staff`

**Request Body:**
```json
{
  "name": "Priya Sharma",
  "email": "priya@salon.com",
  "phone": "+919876543211",
  "role": "stylist",
  "specializations": ["hair_color", "hair_treatments"]
}
```

**Available Roles:**
- `owner` - Full access to all features
- `manager` - Operations and staff management
- `stylist` - Service delivery
- `receptionist` - Booking and customer management

### Step 5: Set Business Hours

**Endpoint:** `POST /api/v1/onboarding/business-hours`

**Request Body:**
```json
{
  "monday": {"open": "09:00", "close": "21:00", "is_closed": false},
  "tuesday": {"open": "09:00", "close": "21:00", "is_closed": false},
  "wednesday": {"open": "09:00", "close": "21:00", "is_closed": false},
  "thursday": {"open": "09:00", "close": "21:00", "is_closed": false},
  "friday": {"open": "09:00", "close": "21:00", "is_closed": false},
  "saturday": {"open": "09:00", "close": "21:00", "is_closed": false},
  "sunday": {"open": "10:00", "close": "20:00", "is_closed": false}
}
```

### Complete Onboarding

**Endpoint:** `POST /api/v1/onboarding/complete`

Marks the onboarding process as complete and activates the salon.

## Join Existing Salon

Staff members can join an existing salon using an invite code.

**Endpoint:** `POST /api/v1/onboarding/join-salon`

**Request Body:**
```json
{
  "invite_code": "T2SGFX18",
  "role": "stylist"
}
```

## Service Templates

The system includes 59+ predefined service templates organized by category:

### Hair Cuts (16 services)
- Men's Hair Cut - ₹250
- Men's Hair Cut + Wash - ₹350
- Women's Hair Cut - ₹350
- Women's Hair Cut + Wash - ₹500
- Kids Hair Cuts - ₹150-200

### Hair Color (10 services)
- Root Touch Up - ₹500
- Full Hair Color - ₹1,500
- Highlights - ₹2,000-4,000
- Balayage - ₹5,000
- Ombre - ₹4,500

### Hair Treatments (8 services)
- Keratin Treatment - ₹5,000
- Hair Spa - ₹800
- Hair Botox - ₹4,000
- Olaplex Treatment - ₹2,500

### Styling (6 services)
- Blow Dry - ₹300
- Ironing/Straightening - ₹400
- Party Styling - ₹800
- Bridal Hair Styling - ₹3,000

### Facial & Skin (10 services)
- Basic Cleanup - ₹400
- Diamond Facial - ₹1,500
- Gold Facial - ₹2,000
- Anti-Aging Facial - ₹2,500

### Spa Services (16 services)
- Head Massage - ₹300
- Full Body Massage - ₹1,500
- Manicure - ₹500
- Pedicure - ₹600
- Waxing services
- Threading services

### Bridal Packages (6 services)
- Bridal Makeup Basic - ₹8,000
- Bridal Makeup Premium - ₹15,000
- Bridal Makeup Luxury - ₹25,000
- Complete Bridal Package - ₹35,000

### Groom Packages (3 services)
- Groom Package Basic - ₹3,000
- Groom Package Premium - ₹5,000
- Groom Package Luxury - ₹8,000

## Data Models

### OnboardingStatus
```python
class OnboardingStatus(BaseModel):
    salon_id: Optional[str]
    salon_name: Optional[str]
    onboarding_completed: bool
    current_step: int
    steps_completed: List[int]
    invite_code: Optional[str]
```

### SalonCreate
```python
class SalonCreate(BaseModel):
    name: str
    address: AddressSchema
    phone: str
    email: str
    gst_number: Optional[str]
    pan_number: Optional[str]
```

## Error Handling

| Status Code | Description |
|-------------|-------------|
| 400 | Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Salon not found |
| 409 | Conflict - Salon already exists for user |
| 422 | Validation error |

## Testing

Run the onboarding tests:
```bash
pytest tests/api/test_onboarding.py -v
```

## Seeding Production Data

Use the seed script to populate the database with realistic test data:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
python scripts/seed_production.py
```

This creates:
- 1 Salon (Jawed Habib Kurnool)
- 16 Resources (chairs, rooms)
- 59 Services
- 9 Staff Members
- 50 Customers
- 30 Bookings
- 3 Membership Plans

## Security Considerations

1. **Authentication**: All endpoints require Firebase Authentication
2. **Authorization**: Role-based access control (RBAC)
3. **Multi-tenancy**: Data isolation by salon_id
4. **Invite Codes**: Unique 8-character codes for salon joining

## Future Enhancements

1. **Document Upload**: GST certificate, business license
2. **Payment Setup**: Configure payment gateways
3. **Integration Setup**: WhatsApp, SMS, email providers
4. **Custom Branding**: Logo, colors, themes
5. **Training Module**: Staff onboarding tutorials
