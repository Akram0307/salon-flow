# Data Migration Skill

## Overview
Migrate existing CRM data (3,230 customers) from ReSpark to the new platform.

## Source Data Analysis

| Field | Type | Notes |
|-------|------|-------|
| mobileNo | string | Primary identifier |
| firstName | string | Customer name |
| gender | string | male/female |
| lastVisitedOn | date | Last appointment |
| orderCount | int | Total orders |
| loyalty | int | Loyalty points |
| membershipCount | int | Active memberships |
| dob | date | Date of birth |

## Migration Script
```python
import pandas as pd
from firebase_admin import firestore

def migrate_customers(excel_path: str, salon_id: str):
    df = pd.read_excel(excel_path)
    db = firestore.client()

    for _, row in df.iterrows():
        customer_data = {
            'salonId': salon_id,
            'phone': str(row['mobileNo']),
            'name': row['firstName'],
            'gender': row['gender'],
            'totalOrders': int(row['orderCount']),
            'loyaltyPoints': int(row['loyalty']) if row['loyalty'] != '-' else 0,
            'createdAt': firestore.SERVER_TIMESTAMP
        }

        doc_ref = db.collection('customers').document()
        doc_ref.set(customer_data)
```

## Migration Steps

1. Export data from ReSpark
2. Transform to new schema
3. Import to Firestore
4. Validate record counts
5. Verify data integrity
