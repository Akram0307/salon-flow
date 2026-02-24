#!/usr/bin/env python3
"""
Salon Flow - Production Database Seeding Script

Creates realistic test data for Jawed Habib Kurnool salon.
Includes salon, services, staff, customers, and bookings.
"""
import asyncio
import json
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "api"))

from google.cloud import firestore
from app.core.firebase import get_firestore_async
from app.core.config import settings


# ============================================================================
# Configuration
# ============================================================================

SALON_DATA = {
    "name": "Jawed Habib Hair & Beauty",
    "display_name": "Jawed Habib Kurnool",
    "address": {
        "street": "Shop No. 12, SV Complex",
        "area": "Budhawarpet",
        "city": "Kurnool",
        "state": "Andhra Pradesh",
        "pincode": "518003",
        "country": "India"
    },
    "contact": {
        "phone": "+918522123456",
        "email": "kurnool@jawedhabib.co.in",
        "website": "https://jawedhabib.co.in"
    },
    "gst_number": "37AABCH1234P1ZA",
    "pan_number": "AABCH1234P",
    "business_hours": {
        "monday": {"open": "09:00", "close": "21:00", "is_closed": False},
        "tuesday": {"open": "09:00", "close": "21:00", "is_closed": False},
        "wednesday": {"open": "09:00", "close": "21:00", "is_closed": False},
        "thursday": {"open": "09:00", "close": "21:00", "is_closed": False},
        "friday": {"open": "09:00", "close": "21:00", "is_closed": False},
        "saturday": {"open": "09:00", "close": "21:00", "is_closed": False},
        "sunday": {"open": "10:00", "close": "20:00", "is_closed": False}
    },
    "layout": {
        "mens_chairs": 6,
        "womens_chairs": 4,
        "service_rooms": 4,
        "bridal_room": 1,
        "spa_room": 1
    }
}

MEMBERSHIP_PLANS = [
    {
        "name": "Silver",
        "price": 999.0,
        "duration_months": 3,
        "discount_percent": 10.0,
        "benefits": ["10% discount on all services", "Priority booking"]
    },
    {
        "name": "Gold",
        "price": 2499.0,
        "duration_months": 6,
        "discount_percent": 15.0,
        "benefits": ["15% discount on all services", "Priority booking", "Free hair spa monthly"]
    },
    {
        "name": "Platinum",
        "price": 4999.0,
        "duration_months": 12,
        "discount_percent": 20.0,
        "benefits": ["20% discount on all services", "Priority booking", "Free hair spa monthly", "Birthday discount 30%", "Complimentary services"]
    }
]


# ============================================================================
# Helper Functions
# ============================================================================

def generate_id(length: int = 20) -> str:
    """Generate random ID."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_invite_code() -> str:
    """Generate salon invite code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def load_json_data(filename: str) -> List[Dict]:
    """Load JSON data from seed_data directory."""
    seed_dir = Path(__file__).parent / "seed_data"
    filepath = seed_dir / filename
    if filepath.exists():
        with open(filepath, 'r') as f:
            return json.load(f)
    return []


def random_date_in_past(days_back: int = 90) -> datetime:
    """Generate random datetime in past."""
    delta = timedelta(days=random.randint(0, days_back), 
                      hours=random.randint(0, 14),
                      minutes=random.choice([0, 15, 30, 45]))
    return datetime.utcnow() - delta


def random_future_date(days_ahead: int = 30) -> datetime:
    """Generate random datetime in future."""
    delta = timedelta(days=random.randint(1, days_ahead),
                      hours=random.randint(9, 20),
                      minutes=random.choice([0, 15, 30, 45]))
    return datetime.utcnow() + delta


# ============================================================================
# Seeding Functions
# ============================================================================

async def seed_salon(db: firestore.AsyncClient) -> str:
    """Create salon and return salon_id."""
    print("\n🏢 Creating salon...")
    
    salon_id = f"salon_{generate_id()}"
    invite_code = generate_invite_code()
    
    salon_doc = {
        **SALON_DATA,
        "id": salon_id,
        "invite_code": invite_code,
        "subscription_plan": "professional",
        "subscription_status": "active",
        "is_active": True,
        "onboarding_completed": True,
        "onboarding_step": 5,
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
        "settings": {
            "currency": "INR",
            "timezone": "Asia/Kolkata",
            "gst_enabled": True,
            "gst_rate": 5.0,
            "loyalty_rate": 0.1,  # 1 point per ₹10
            "loyalty_expiry_months": 12,
            "booking_buffer_minutes": 15,
            "late_arrival_grace_minutes": 15,
            "auto_confirm_bookings": True,
            "send_reminders": True,
            "reminder_hours_before": 2
        },
        "stats": {
            "total_customers": 0,
            "total_bookings": 0,
            "total_revenue": 0.0
        }
    }
    
    await db.collection("salons").document(salon_id).set(salon_doc)
    print(f"   ✓ Salon created: {SALON_DATA['name']}")
    print(f"   ✓ Salon ID: {salon_id}")
    print(f"   ✓ Invite Code: {invite_code}")
    
    return salon_id


async def seed_resources(db: firestore.AsyncClient, salon_id: str) -> Dict[str, List[str]]:
    """Create salon resources (chairs, rooms)."""
    print("\n🪑 Creating resources...")
    
    resources = {
        "mens_chairs": [],
        "womens_chairs": [],
        "service_rooms": [],
        "bridal_room": [],
        "spa_room": []
    }
    
    # Men's chairs
    for i in range(SALON_DATA["layout"]["mens_chairs"]):
        resource_id = f"res_{generate_id()}"
        resource_doc = {
            "id": resource_id,
            "salon_id": salon_id,
            "name": f"Men's Chair {i + 1}",
            "type": "mens_chair",
            "is_active": True,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        await db.collection("salons").document(salon_id).collection("resources").document(resource_id).set(resource_doc)
        resources["mens_chairs"].append(resource_id)
    print(f"   ✓ Created {len(resources['mens_chairs'])} men's chairs")
    
    # Women's chairs
    for i in range(SALON_DATA["layout"]["womens_chairs"]):
        resource_id = f"res_{generate_id()}"
        resource_doc = {
            "id": resource_id,
            "salon_id": salon_id,
            "name": f"Women's Chair {i + 1}",
            "type": "womens_chair",
            "is_active": True,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        await db.collection("salons").document(salon_id).collection("resources").document(resource_id).set(resource_doc)
        resources["womens_chairs"].append(resource_id)
    print(f"   ✓ Created {len(resources['womens_chairs'])} women's chairs")
    
    # Service rooms
    for i in range(SALON_DATA["layout"]["service_rooms"]):
        resource_id = f"res_{generate_id()}"
        resource_doc = {
            "id": resource_id,
            "salon_id": salon_id,
            "name": f"Service Room {i + 1}",
            "type": "service_room",
            "is_active": True,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        await db.collection("salons").document(salon_id).collection("resources").document(resource_id).set(resource_doc)
        resources["service_rooms"].append(resource_id)
    print(f"   ✓ Created {len(resources['service_rooms'])} service rooms")
    
    # Bridal room
    for i in range(SALON_DATA["layout"]["bridal_room"]):
        resource_id = f"res_{generate_id()}"
        resource_doc = {
            "id": resource_id,
            "salon_id": salon_id,
            "name": "Bridal Room",
            "type": "bridal_room",
            "is_active": True,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        await db.collection("salons").document(salon_id).collection("resources").document(resource_id).set(resource_doc)
        resources["bridal_room"].append(resource_id)
    print(f"   ✓ Created {len(resources['bridal_room'])} bridal room")
    
    # Spa room
    for i in range(SALON_DATA["layout"]["spa_room"]):
        resource_id = f"res_{generate_id()}"
        resource_doc = {
            "id": resource_id,
            "salon_id": salon_id,
            "name": "Spa Room",
            "type": "spa_room",
            "is_active": True,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        await db.collection("salons").document(salon_id).collection("resources").document(resource_id).set(resource_doc)
        resources["spa_room"].append(resource_id)
    print(f"   ✓ Created {len(resources['spa_room'])} spa room")
    
    return resources


async def seed_services(db: firestore.AsyncClient, salon_id: str) -> Dict[str, str]:
    """Import services from templates."""
    print("\n💅 Importing services...")
    
    # Import service templates
    from app.services.service_templates import get_service_templates
    
    services = get_service_templates("salon")
    service_map = {}  # name -> id mapping
    
    for idx, service in enumerate(services):
        service_id = f"svc_{generate_id()}"
        
        service_doc = {
            "id": service_id,
            "salon_id": salon_id,
            "name": service["name"],
            "description": service.get("description", ""),
            "category": service["category"],
            "pricing": service["pricing"],
            "duration": service["duration"],
            "resource_requirement": service.get("resource_requirement", {"resource_type": "any"}),
            "gender_preference": service.get("gender_preference"),
            "is_active": True,
            "is_popular": service.get("is_popular", False),
            "display_order": idx,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        await db.collection("salons").document(salon_id).collection("services").document(service_id).set(service_doc)
        service_map[service["name"]] = service_id
    
    print(f"   ✓ Imported {len(services)} services")
    
    # Print category breakdown
    categories = {}
    for s in services:
        cat = s["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        print(f"      - {cat}: {count} services")
    
    return service_map


async def seed_staff(db: firestore.AsyncClient, salon_id: str, service_map: Dict[str, str]) -> Dict[str, str]:
    """Create staff members."""
    print("\n👥 Creating staff members...")
    
    staff_data = load_json_data("staff.json")
    staff_map = {}  # name -> id mapping
    
    for staff in staff_data:
        staff_id = f"staff_{generate_id()}"
        
        # Map specializations to service IDs
        skill_service_ids = []
        for spec in staff.get("specializations", []):
            # Find matching services
            for name, sid in service_map.items():
                if spec in name.lower() or spec in name.lower().replace(" ", "_"):
                    skill_service_ids.append(sid)
        
        staff_doc = {
            "id": staff_id,
            "salon_id": salon_id,
            "name": staff["name"],
            "email": staff["email"],
            "phone": staff["phone"],
            "role": staff["role"],
            "specializations": staff.get("specializations", []),
            "skill_service_ids": list(set(skill_service_ids)),
            "experience_years": staff.get("experience_years", 0),
            "is_active": staff.get("is_active", True),
            "rating": round(random.uniform(4.0, 5.0), 1),
            "total_bookings": random.randint(50, 500),
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "availability": {
                "monday": {"start": "09:00", "end": "21:00", "is_off": False},
                "tuesday": {"start": "09:00", "end": "21:00", "is_off": False},
                "wednesday": {"start": "09:00", "end": "21:00", "is_off": False},
                "thursday": {"start": "09:00", "end": "21:00", "is_off": False},
                "friday": {"start": "09:00", "end": "21:00", "is_off": False},
                "saturday": {"start": "09:00", "end": "21:00", "is_off": False},
                "sunday": {"start": "10:00", "end": "20:00", "is_off": False}
            }
        }
        
        await db.collection("salons").document(salon_id).collection("staff").document(staff_id).set(staff_doc)
        staff_map[staff["name"]] = staff_id
        print(f"   ✓ Created: {staff['name']} ({staff['role']})")
    
    return staff_map


async def seed_customers(db: firestore.AsyncClient, salon_id: str) -> Dict[str, str]:
    """Create customers."""
    print("\n👤 Creating customers...")
    
    customer_data = load_json_data("customers.json")
    customer_map = {}  # name -> id mapping
    
    for customer in customer_data:
        customer_id = f"cust_{generate_id()}"
        
        # Calculate membership expiry if applicable
        membership_expiry = None
        if customer.get("membership_type"):
            membership_expiry = (datetime.utcnow() + timedelta(days=random.randint(30, 365))).isoformat()
        
        customer_doc = {
            "id": customer_id,
            "salon_id": salon_id,
            "name": customer["name"],
            "phone": customer["phone"],
            "email": customer.get("email"),
            "gender": customer.get("gender"),
            "loyalty_points": customer.get("loyalty_points", 0),
            "total_visits": random.randint(1, 20),
            "total_spent": float(random.randint(1000, 50000)),
            "membership_type": customer.get("membership_type"),
            "membership_expiry": membership_expiry,
            "first_visit": random_date_in_past(180).isoformat(),
            "last_visit": random_date_in_past(30).isoformat(),
            "notes": "",
            "preferences": {
                "preferred_stylist": None,
                "preferred_services": [],
                "notifications": {
                    "sms": True,
                    "whatsapp": True,
                    "email": True
                }
            },
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        await db.collection("salons").document(salon_id).collection("customers").document(customer_id).set(customer_doc)
        customer_map[customer["name"]] = customer_id
    
    print(f"   ✓ Created {len(customer_data)} customers")
    
    # Membership breakdown
    memberships = {}
    for c in customer_data:
        mtype = c.get("membership_type") or "none"
        memberships[mtype] = memberships.get(mtype, 0) + 1
    
    for mtype, count in sorted(memberships.items()):
        print(f"      - {mtype}: {count} customers")
    
    return customer_map


async def seed_bookings(
    db: firestore.AsyncClient, 
    salon_id: str,
    service_map: Dict[str, str],
    staff_map: Dict[str, str],
    customer_map: Dict[str, str]
) -> None:
    """Create bookings with various statuses."""
    print("\n📅 Creating bookings...")
    
    service_names = list(service_map.keys())
    staff_names = list(staff_map.keys())
    customer_names = list(customer_map.keys())
    
    statuses = ["completed", "completed", "completed", "confirmed", "confirmed", "pending", "cancelled", "no_show"]
    
    bookings_created = 0
    
    for i in range(30):
        booking_id = f"book_{generate_id()}"
        
        # Random selections
        service_name = random.choice(service_names)
        staff_name = random.choice(staff_names)
        customer_name = random.choice(customer_names)
        status = random.choice(statuses)
        
        # Determine date based on status
        if status in ["completed", "cancelled", "no_show"]:
            booking_date = random_date_in_past(60)
        else:
            booking_date = random_future_date(14)
        
        # Get service details for pricing
        service_id = service_map[service_name]
        staff_id = staff_map[staff_name]
        customer_id = customer_map[customer_name]
        
        # Calculate price with variation
        base_price = random.randint(200, 3000)
        final_price = base_price
        
        # Apply discount for members
        discount = 0
        if random.random() > 0.7:  # 30% chance of discount
            discount = int(base_price * random.choice([0.1, 0.15, 0.2]))
            final_price = base_price - discount
        
        booking_doc = {
            "id": booking_id,
            "salon_id": salon_id,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "staff_id": staff_id,
            "staff_name": staff_name,
            "service_id": service_id,
            "service_name": service_name,
            "booking_date": booking_date.strftime("%Y-%m-%d"),
            "start_time": booking_date.strftime("%H:%M"),
            "end_time": (booking_date + timedelta(minutes=random.randint(30, 90))).strftime("%H:%M"),
            "status": status,
            "payment_status": "paid" if status == "completed" else "pending",
            "base_price": float(base_price),
            "discount": float(discount),
            "final_price": float(final_price),
            "gst_amount": round(final_price * 0.05, 2),
            "total_amount": round(final_price * 1.05, 2),
            "loyalty_points_earned": int(final_price / 10),
            "notes": "",
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        await db.collection("salons").document(salon_id).collection("bookings").document(booking_id).set(booking_doc)
        bookings_created += 1
    
    print(f"   ✓ Created {bookings_created} bookings")
    
    # Status breakdown
    status_counts = {}
    for _ in range(30):
        s = random.choice(statuses)
        status_counts[s] = status_counts.get(s, 0) + 1
    
    for status, count in sorted(status_counts.items()):
        print(f"      - {status}: {count} bookings")


async def seed_membership_plans(db: firestore.AsyncClient, salon_id: str) -> None:
    """Create membership plans."""
    print("\n💳 Creating membership plans...")
    
    for plan in MEMBERSHIP_PLANS:
        plan_id = f"plan_{generate_id()}"
        
        plan_doc = {
            "id": plan_id,
            "salon_id": salon_id,
            "name": plan["name"],
            "price": plan["price"],
            "duration_months": plan["duration_months"],
            "discount_percent": plan["discount_percent"],
            "benefits": plan["benefits"],
            "is_active": True,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        await db.collection("salons").document(salon_id).collection("membership_plans").document(plan_id).set(plan_doc)
        print(f"   ✓ Created: {plan['name']} plan (₹{plan['price']})")


# ============================================================================
# Main Seeding Function
# ============================================================================

async def seed_database():
    """Main seeding function."""
    print("\n" + "="*60)
    print("🌱 Salon Flow - Production Database Seeding")
    print("="*60)
    
    # Initialize Firebase
    db = get_firestore_async()
    
    # Run seeding steps
    salon_id = await seed_salon(db)
    resources = await seed_resources(db, salon_id)
    service_map = await seed_services(db, salon_id)
    staff_map = await seed_staff(db, salon_id, service_map)
    customer_map = await seed_customers(db, salon_id)
    await seed_bookings(db, salon_id, service_map, staff_map, customer_map)
    await seed_membership_plans(db, salon_id)
    
    print("\n" + "="*60)
    print("✅ Seeding completed successfully!")
    print("="*60)
    print(f"\nSalon ID: {salon_id}")
    print(f"Services: {len(service_map)}")
    print(f"Staff: {len(staff_map)}")
    print(f"Customers: {len(customer_map)}")
    print(f"Bookings: 30")
    print("\n")


if __name__ == "__main__":
    asyncio.run(seed_database())
