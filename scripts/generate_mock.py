#!/usr/bin/env python3
"""
Salon Flow - Mock Data Generator
Generates mock data for testing and development
"""
import json
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('en_IN')


def generate_mock_customer():
    """Generate a single mock customer"""
    return {
        "id": fake.uuid4(),
        "name": fake.name(),
        "phone": "+91" + fake.msisdn()[3:13],
        "email": fake.email(),
        "gender": random.choice(["male", "female"]),
        "loyalty_points": random.randint(0, 500),
        "total_visits": random.randint(0, 50),
        "total_spent": random.randint(0, 100000),
        "created_at": datetime.utcnow().isoformat()
    }


def generate_mock_booking(customer_id: str = None):
    """Generate a single mock booking"""
    statuses = ["booked", "confirmed", "in_progress", "completed", "cancelled"]
    services = ["Men's Haircut", "Women's Haircut", "Hair Color", "Facial", "Spa"]
    
    booking_date = datetime.utcnow() + timedelta(days=random.randint(-7, 7))
    
    return {
        "id": fake.uuid4(),
        "customer_id": customer_id or fake.uuid4(),
        "service_name": random.choice(services),
        "date": booking_date.strftime("%Y-%m-%d"),
        "time": f"{random.randint(9, 20):02d}:{random.choice([0, 15, 30, 45]):02d}",
        "status": random.choice(statuses),
        "price": random.randint(100, 5000),
        "created_at": datetime.utcnow().isoformat()
    }


def generate_mock_staff():
    """Generate a single mock staff member"""
    roles = ["stylist", "senior_stylist", "colorist", "therapist", "receptionist"]
    
    return {
        "id": fake.uuid4(),
        "name": fake.name(),
        "phone": "+91" + fake.msisdn()[3:13],
        "email": fake.email(),
        "role": random.choice(roles),
        "active": True,
        "created_at": datetime.utcnow().isoformat()
    }


def generate_mock_service():
    """Generate a single mock service"""
    categories = ["Haircuts", "Hair Color", "Hair Treatment", "Facial", "Spa", "Waxing"]
    
    return {
        "id": fake.uuid4(),
        "name": fake.word().title() + " Service",
        "category": random.choice(categories),
        "duration_minutes": random.choice([15, 30, 45, 60, 90]),
        "base_price": random.randint(100, 5000),
        "active": True,
        "created_at": datetime.utcnow().isoformat()
    }


def generate_mock_data(data_type: str, count: int = 10):
    """Generate mock data of specified type"""
    generators = {
        "customers": generate_mock_customer,
        "bookings": generate_mock_booking,
        "staff": generate_mock_staff,
        "services": generate_mock_service
    }
    
    if data_type not in generators:
        raise ValueError(f"Unknown data type: {data_type}")
    
    generator = generators[data_type]
    return [generator() for _ in range(count)]


def save_mock_data(data_type: str, count: int = 10, output_dir: str = "./tests/fixtures"):
    """Generate and save mock data to JSON file"""
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    
    data = generate_mock_data(data_type, count)
    
    output_file = os.path.join(output_dir, f"{data_type}.json")
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Generated {count} {data_type} -> {output_file}")
    return output_file


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate mock data for Salon Flow")
    parser.add_argument("type", choices=["customers", "bookings", "staff", "services", "all"],
                        help="Type of data to generate")
    parser.add_argument("-c", "--count", type=int, default=10,
                        help="Number of items to generate")
    parser.add_argument("-o", "--output", default="./tests/fixtures",
                        help="Output directory")
    
    args = parser.parse_args()
    
    if args.type == "all":
        for data_type in ["customers", "bookings", "staff", "services"]:
            save_mock_data(data_type, args.count, args.output)
    else:
        save_mock_data(args.type, args.count, args.output)
