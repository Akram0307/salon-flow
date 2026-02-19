# Analytics Pipeline Skill

## Overview
Build analytics pipelines to generate business insights for salon owners.

## Key Metrics

### Revenue Metrics
- Daily/Weekly/Monthly revenue
- Revenue by service category
- Revenue by staff member
- Average ticket value

### Customer Metrics
- New vs returning customers
- Customer lifetime value
- Churn rate
- NPS score

### Operational Metrics
- Utilization rate
- Peak hours
- Average service time
- No-show rate

## Data Pipeline
```
Raw Events → Pub/Sub → Cloud Function → Analytics Collection
```

## Event Tracking
```python
def track_event(salon_id: str, event_type: str, data: dict):
    event = {
        'salonId': salon_id,
        'eventType': event_type,
        'timestamp': firestore.SERVER_TIMESTAMP,
        'data': data
    }
    db.collection('analytics_events').add(event)
```

## Aggregation
```python
async def aggregate_daily_metrics(salon_id: str, date: str):
    appointments = await get_appointments(salon_id, date)

    metrics = {
        'date': date,
        'totalBookings': len(appointments),
        'revenue': sum_revenue(appointments),
        'utilizationRate': calculate_utilization(appointments)
    }

    await db.collection('daily_metrics').doc(f"{salon_id}_{date}").set(metrics)
```
