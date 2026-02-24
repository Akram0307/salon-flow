import asyncio
import sys
from pathlib import Path

sys.path.insert(0, '/a0/usr/projects/salon_flow/services/api')
from app.core.firebase import get_firestore_async

async def run():
    db = get_firestore_async()
    print("--- SALONS ---")
    salons = await db.collection('salons').get()
    for s in salons:
        data = s.to_dict()
        print(f"ID: {s.id}, Name: {data.get('name')}")
        
    print("\n--- USERS ---")
    users = await db.collection('users').get()
    for u in users:
        data = u.to_dict()
        print(f"Email: {data.get('email')}, Role: {data.get('role')}, Salon ID: {data.get('salon_id')}")

asyncio.run(run())
