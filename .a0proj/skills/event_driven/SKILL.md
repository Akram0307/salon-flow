# Event-Driven Architecture Skill

## Overview
Implement event-driven communication between microservices using GCP Pub/Sub.

## Event Topics

| Topic | Publisher | Subscriber |
|-------|-----------|------------|
| appointment-created | Booking Service | Notification, Analytics |
| appointment-cancelled | Booking Service | Notification, Analytics |
| customer-registered | Auth Service | Marketing, Analytics |
| service-completed | Staff App | Notification, Loyalty |

## Event Schema
```typescript
interface SalonEvent {
  eventId: string
  eventType: string
  salonId: string
  timestamp: string
  data: any
}
```

## Publisher Example
```python
from google.cloud import pubsub_v1

def publish_event(topic_name: str, event: dict):
    topic_path = publisher.topic_path(project_id, topic_name)
    message_data = json.dumps(event).encode('utf-8')
    publisher.publish(topic_path, message_data, salon_id=event['salonId'])
```

## Event Flow
```
Appointment Created
    ↓
[appointment-created] Topic
    ↓
┌──────────────┬──────────────┐
│ Notification │  Analytics   │
└──────────────┴──────────────┘
```
