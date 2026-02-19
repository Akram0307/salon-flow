# State Management Skill

## Overview
Implement efficient state management for React PWAs using Zustand.

## Store Structure
```typescript
interface AppointmentState {
  appointments: Appointment[]
  selectedAppointment: Appointment | null
  loading: boolean

  // Actions
  fetchAppointments: (salonId: string) => Promise<void>
  createAppointment: (data: AppointmentData) => Promise<void>
  updateAppointment: (id: string, data: Partial<Appointment>) => Promise<void>
}

export const useAppointmentStore = create<AppointmentState>()(
  persist(
    (set, get) => ({
      appointments: [],
      selectedAppointment: null,
      loading: false,

      fetchAppointments: async (salonId) => {
        set({ loading: true })
        const data = await api.getAppointments(salonId)
        set({ appointments: data, loading: false })
      }
    }),
    { name: 'appointment-store' }
  )
)
```

## Store Categories

| Store | Purpose |
|-------|--------|
| authStore | User authentication state |
| salonStore | Current salon data |
| appointmentStore | Appointments management |
| customerStore | Customer data |
| uiStore | UI state (modals, toasts) |
