# Offline-First Architecture Skill

## Overview
Design PWAs that work seamlessly offline with automatic synchronization.

## Data Flow
```
User Action → Local Store → Background Sync → Server
                ↓
            UI Update
```

## Local Storage Strategy

### IndexedDB Schema
```typescript
const db = new Dexie('SalonDB')
db.version(1).stores({
  customers: 'id, phone, name',
  appointments: 'id, date, status',
  services: 'id, category, price',
  staff: 'id, name, role',
  pendingSync: '++id, action, data, timestamp'
})
```

## Background Sync
```typescript
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-appointments') {
    event.waitUntil(syncAppointments())
  }
})
```

## Conflict Resolution
- Last-write-wins for simple fields
- Merge strategy for complex objects
- Manual resolution for critical conflicts

## UI Indicators
- Online/offline status banner
- Sync progress indicator
- Pending changes counter
