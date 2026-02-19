# React PWA Development Skill

## Overview
Build Progressive Web Apps for the Salon SaaS platform with offline-first architecture.

## Tech Stack
- React 18 with TypeScript
- Vite for build tooling
- Workbox for service workers
- shadcn/ui for components

## PWA Structure
```
src/
├── components/
│   ├── ui/           # shadcn components
│   ├── layout/       # Layout components
│   └── features/     # Feature components
├── hooks/
├── services/
├── store/            # Zustand stores
├── workers/
│   └── sw.ts         # Service worker
└── main.tsx
```

## Service Worker Configuration
```typescript
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    VitePWA({
      strategies: 'injectManifest',
      srcDir: 'src/workers',
      filename: 'sw.ts',
      manifest: {
        name: 'Salon SaaS',
        short_name: 'Salon',
        theme_color: '#1a1a2e'
      }
    })
  ]
})
```

## Offline Strategies

### Cache First (Static Assets)
```typescript
registerRoute(
  ({ request }) => request.destination === 'style',
  new CacheFirst({ cacheName: 'styles' })
)
```

### Network First (API Calls)
```typescript
registerRoute(
  /\/api\//,
  new NetworkFirst({ cacheName: 'api-cache' })
)
```
