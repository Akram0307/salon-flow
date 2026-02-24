import httpx
import json

API_URL = "https://salon-flow-api-687369167038.asia-south1.run.app/api/v1"

def run():
    token = None
    emails_to_try = ["owner@jawedhabib-kurnool.com", "owner@salonflow.com", "rajesh@jawedhabib.com", "e2e_test@salonflow.com"]
    
    for email in emails_to_try:
        try:
            resp = httpx.post(f"{API_URL}/auth/login", json={"email": email, "password": "TestPass123!"})
            if resp.status_code == 200:
                token = resp.json()["access_token"]
                print(f"Logged in as {email}")
                
                # Check if user has a salon
                me_resp = httpx.get(f"{API_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
                if me_resp.status_code == 200 and me_resp.json().get("salon_id"):
                    print(f"User {email} is associated with salon: {me_resp.json().get('salon_id')}")
                    break
                else:
                    print(f"User {email} has no salon associated. Trying next...")
                    token = None
            else:
                print(f"Failed to login as {email}: {resp.status_code}")
        except Exception as e:
            print(f"Error logging in as {email}: {e}")
    
    if not token:
        print("Failed to find a user with an associated salon.")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    with open('/a0/usr/projects/salon_flow/scripts/seed_data/staff.json', 'r') as f:
        staff_data = json.load(f)
        
    for staff in staff_data:
        role = staff['role']
        if role == 'senior_stylist': role = 'stylist'
        if role == 'owner': continue # Skip owner as they are already created
        
        payload = {
            "name": staff["name"],
            "email": staff["email"],
            "phone": staff["phone"],
            "role": role,
            "specializations": staff.get("specializations", [])
        }
        print(f"Adding {staff['name']}...")
        try:
            res = httpx.post(f"{API_URL}/onboarding/staff", json=payload, headers=headers)
            print(res.status_code, res.text)
        except Exception as e:
            print(f"Error adding {staff['name']}: {e}")

run()
