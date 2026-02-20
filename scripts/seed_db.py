#!/usr/bin/env python3
"""
Salon Flow - Database Seeding Script
Seeds Firestore with test data for development
"""
import os
import sys
import json
import random
from datetime import datetime, timedelta
from faker import Faker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

fake = Faker('en_IN')  # Indian locale for realistic data

# ===========================================
# Configuration
# ===========================================
SALON_ID = "salon_001"
SALON_NAME = "Jawed Habib Hair & Beauty - Kurnool"

# Service categories from the Excel data
SERVICE_CATEGORIES = {
    "Haircuts": ["Men's Haircut", "Women's Haircut", "Kids Haircut", "Bang Trim", "Layer Cut"],
    "Hair Color": ["Global Color", "Highlights", "Root Touch Up", "Balayage", "Ombre"],
    "Hair Treatment": ["Keratin Treatment", "Smoothening", "Deep Conditioning", "Scalp Treatment"],
    "Facial & Skincare": ["Cleanup", "Facial", "Bleach", "De-tan", "Cleanup + Bleach"],
    "Bridal & Groom": ["Bridal Makeup", "Groom Package", "Pre-Bridal Package", "Mehndi"],
    "Spa & Massage": ["Head Massage", "Body Massage", "Foot Massage", "Aromatherapy"],
    "Waxing": ["Full Body Waxing", "Half Arms", "Full Arms", "Half Legs", "Full Legs"],
    "Threading": ["Eyebrows", "Upper Lip", "Full Face", "Forehead"],
    "Manicure & Pedicure": ["Classic Manicure", "Classic Pedicure", "Gel Manicure", "Spa Pedicure"],
    "Special Packages": ["Bridal Package", "Groom Package", "Party Ready", "Weekly Spa"]
}

STAFF_ROLES = ["stylist", "senior_stylist", "colorist", "therapist", "receptionist", "manager"]

# ===========================================
# Data Generators
# ===========================================

def generate_salon():
    """Generate salon document"""
    return {
        "id": SALON_ID,
        "name": SALON_NAME,
        "address": {
            "street": fake.street_address(),
            "city": "Kurnool",
            "state": "Andhra Pradesh",
            "pincode": fake.postcode(),
            "country": "India"
        },
        "contact": {
            "phone": "+91" + fake.msisdn()[3:13],
            "email": f"info@{SALON_NAME.lower().replace(' ', '').replace('-', '')}.com",
            "whatsapp": "+91" + fake.msisdn()[3:13]
        },
        "layout": {
            "mens_chairs": 6,
            "womens_chairs": 4,
            "service_rooms": 4,
            "rooms": [
                {"id": "room_1", "name": "Bridal Room", "type": "exclusive"},
                {"id": "room_2", "name": "Treatment Room 1", "type": "shared"},
                {"id": "room_3", "name": "Treatment Room 2", "type": "shared"},
                {"id": "room_4", "name": "Spa Room", "type": "exclusive"}
            ]
        },
        "operating_hours": {
            "weekday": {"open": "09:00", "close": "21:00"},
            "weekend": {"open": "09:00", "close": "22:00"}
        },
        "settings": {
            "gst_rate": 5,
            "loyalty_rate": 1,  # 1 point per ₹10
            "loyalty_expiry_months": 12,
            "membership_renewal_days": 15,
            "late_arrival_grace_minutes": 15
        },
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }


def generate_services():
    """Generate services from categories"""
    services = []
    service_id = 1
    
    for category, items in SERVICE_CATEGORIES.items():
        for item in items:
            base_price = random.randint(100, 5000)
            duration = random.choice([15, 30, 45, 60, 90, 120])
            
            # Determine resource type
            if category in ["Bridal & Groom", "Spa & Massage"]:
                resource_type = "room"
            else:
                resource_type = "chair"
            
            services.append({
                "id": f"service_{service_id:03d}",
                "salon_id": SALON_ID,
                "name": item,
                "category": category,
                "description": f"Professional {item.lower()} service",
                "base_price": base_price,
                "duration_minutes": duration,
                "resource_type": resource_type,
                "gst_rate": 5,
                "active": True,
                "created_at": datetime.utcnow().isoformat()
            })
            service_id += 1
    
    return services


def generate_staff(count=15):
    """Generate staff members"""
    staff = []
    
    for i in range(count):
        role = random.choice(STAFF_ROLES)
        skills = random.sample(list(SERVICE_CATEGORIES.keys()), k=random.randint(2, 5))
        
        staff.append({
            "id": f"staff_{i+1:03d}",
            "salon_id": SALON_ID,
            "name": fake.name(),
            "phone": "+91" + fake.msisdn()[3:13],
            "email": fake.email(),
            "role": role,
            "skills": skills,
            "expertise_level": random.choice(["junior", "mid", "senior", "expert"]),
            "availability": {
                "monday": {"available": True, "shift": "morning"},
                "tuesday": {"available": True, "shift": "morning"},
                "wednesday": {"available": True, "shift": "evening"},
                "thursday": {"available": True, "shift": "evening"},
                "friday": {"available": True, "shift": "full"},
                "saturday": {"available": True, "shift": "full"},
                "sunday": {"available": random.choice([True, False]), "shift": "morning"}
            },
            "active": True,
            "created_at": datetime.utcnow().isoformat()
        })
    
    return staff


def generate_customers(count=100):
    """Generate customers"""
    customers = []
    
    for i in range(count):
        customers.append({
            "id": f"customer_{i+1:04d}",
            "salon_id": SALON_ID,
            "name": fake.name(),
            "phone": "+91" + fake.msisdn()[3:13],
            "email": fake.email() if random.random() > 0.3 else None,
            "gender": random.choice(["male", "female"]),
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=65).isoformat() if random.random() > 0.5 else None,
            "address": fake.address(),
            "loyalty_points": random.randint(0, 500),
            "membership": {
                "active": random.random() > 0.7,
                "type": random.choice(["silver", "gold", "platinum"]) if random.random() > 0.7 else None,
                "expiry": (datetime.utcnow() + timedelta(days=random.randint(30, 365))).isoformat() if random.random() > 0.7 else None
            },
            "preferences": {
                "preferred_stylist": f"staff_{random.randint(1, 15):03d}" if random.random() > 0.5 else None,
                "preferred_services": random.sample(list(SERVICE_CATEGORIES.keys()), k=random.randint(1, 3))
            },
            "total_visits": random.randint(0, 50),
            "total_spent": random.randint(0, 100000),
            "created_at": datetime.utcnow().isoformat(),
            "last_visit": (datetime.utcnow() - timedelta(days=random.randint(1, 90))).isoformat() if random.random() > 0.3 else None
        })
    
    return customers


def generate_bookings(customers, staff, services, count=50):
    """Generate bookings"""
    bookings = []
    statuses = ["booked", "confirmed", "in_progress", "completed", "cancelled", "no_show"]
    
    for i in range(count):
        customer = random.choice(customers)
        service = random.choice(services)
        staff_member = random.choice(staff)
        status = random.choice(statuses)
        
        booking_date = datetime.utcnow() + timedelta(days=random.randint(-30, 30))
        start_time = booking_date.replace(
            hour=random.randint(9, 20),
            minute=random.choice([0, 15, 30, 45]),
            second=0
        )
        end_time = start_time + timedelta(minutes=service["duration_minutes"])
        
        bookings.append({
            "id": f"booking_{i+1:04d}",
            "salon_id": SALON_ID,
            "customer_id": customer["id"],
            "customer_name": customer["name"],
            "customer_phone": customer["phone"],
            "service_id": service["id"],
            "service_name": service["name"],
            "staff_id": staff_member["id"],
            "staff_name": staff_member["name"],
            "date": booking_date.strftime("%Y-%m-%d"),
            "start_time": start_time.strftime("%H:%M"),
            "end_time": end_time.strftime("%H:%M"),
            "duration": service["duration_minutes"],
            "base_price": service["base_price"],
            "gst_amount": round(service["base_price"] * 0.05, 2),
            "total_price": round(service["base_price"] * 1.05, 2),
            "status": status,
            "source": random.choice(["walk_in", "phone", "whatsapp", "online"]),
            "notes": fake.sentence() if random.random() > 0.7 else None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        })
    
    return bookings


# ===========================================
# Firestore Operations
# ===========================================

def seed_firestore():
    """Seed Firestore with test data"""
    try:
        import firebase_admin
        from firebase_admin import firestore
        
        # Initialize Firebase
        if not firebase_admin._apps:
            os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
            os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = "localhost:9099"
            firebase_admin.initialize_app(options={"projectId": "salon-flow-dev"})
        
        db = firestore.client()
        
        print("🌱 Seeding Firestore database...")
        
        # Generate data
        salon = generate_salon()
        services = generate_services()
        staff = generate_staff()
        customers = generate_customers()
        bookings = generate_bookings(customers, staff, services)
        
        # Write salon
        db.collection("salons").document(salon["id"]).set(salon)
        print(f"  ✅ Salon: {salon['name']}")
        
        # Write services
        batch = db.batch()
        for service in services:
            ref = db.collection("salons").document(SALON_ID).collection("services").document(service["id"])
            batch.set(ref, service)
        batch.commit()
        print(f"  ✅ Services: {len(services)}")
        
        # Write staff
        batch = db.batch()
        for member in staff:
            ref = db.collection("salons").document(SALON_ID).collection("staff").document(member["id"])
            batch.set(ref, member)
        batch.commit()
        print(f"  ✅ Staff: {len(staff)}")
        
        # Write customers
        batch = db.batch()
        for customer in customers:
            ref = db.collection("salons").document(SALON_ID).collection("customers").document(customer["id"])
            batch.set(ref, customer)
        batch.commit()
        print(f"  ✅ Customers: {len(customers)}")
        
        # Write bookings
        batch = db.batch()
        for booking in bookings:
            ref = db.collection("salons").document(SALON_ID).collection("bookings").document(booking["id"])
            batch.set(ref, booking)
        batch.commit()
        print(f"  ✅ Bookings: {len(bookings)}")
        
        print("\n🎉 Database seeding complete!")
        print(f"\n📊 Summary:")
        print(f"   Salon: {salon['name']}")
        print(f"   Services: {len(services)}")
        print(f"   Staff: {len(staff)}")
        print(f"   Customers: {len(customers)}")
        print(f"   Bookings: {len(bookings)}")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise


if __name__ == "__main__":
    seed_firestore()
