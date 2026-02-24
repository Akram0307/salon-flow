import asyncio
import sys
from pathlib import Path

# Add the api directory to the path so we can import app modules
sys.path.insert(0, '/a0/usr/projects/salon_flow/services/api')

from app.core.firebase import get_firestore_async

async def run():
    db = get_firestore_async()
    salons = await db.collection('salons').where('name', '==', 'Jawed Habib Hair & Beauty').get()
    for s in salons:
        print(f"Salon ID: {s.id}")
        users = await db.collection('users').where('salon_id', '==', s.id).get()
        for u in users:
            print(f"User Email: {u.to_dict().get('email')}")

asyncio.run(run())
