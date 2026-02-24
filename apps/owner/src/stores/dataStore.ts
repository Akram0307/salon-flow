import { create } from 'zustand';
import type { Customer, Staff, Booking, Service } from '@salon-flow/shared';

export interface DataCache {
  customers: Customer[];
  staff: Staff[];
  bookings: Booking[];
  services: Service[];
  lastUpdated: {
    customers: number | null;
    staff: number | null;
    bookings: number | null;
    services: number | null;
  };
}

export interface DataState extends DataCache {
  isLoading: {
    customers: boolean;
    staff: boolean;
    bookings: boolean;
    services: boolean;
  };
  error: {
    customers: string | null;
    staff: string | null;
    bookings: string | null;
    services: string | null;
  };
}

export interface DataActions {
  // Setters
  setCustomers: (customers: Customer[]) => void;
  setStaff: (staff: Staff[]) => void;
  setBookings: (bookings: Booking[]) => void;
  setServices: (services: Service[]) => void;
  
  // Add single items
  addCustomer: (customer: Customer) => void;
  addStaff: (staff: Staff) => void;
  addBooking: (booking: Booking) => void;
  addService: (service: Service) => void;
  
  // Update items
  updateCustomer: (id: string, updates: Partial<Customer>) => void;
  updateStaff: (id: string, updates: Partial<Staff>) => void;
  updateBooking: (id: string, updates: Partial<Booking>) => void;
  updateService: (id: string, updates: Partial<Service>) => void;
  
  // Remove items
  removeCustomer: (id: string) => void;
  removeStaff: (id: string) => void;
  removeBooking: (id: string) => void;
  removeService: (id: string) => void;
  
  // Loading states
  setLoading: (key: keyof DataState['isLoading'], isLoading: boolean) => void;
  
  // Error states
  setError: (key: keyof DataState['error'], error: string | null) => void;
  clearError: (key: keyof DataState['error']) => void;
  
  // Cache management
  clearCache: () => void;
  isStale: (key: keyof DataCache['lastUpdated'], maxAgeMs?: number) => boolean;
}

export type DataStore = DataState & DataActions;

const initialState: DataState = {
  customers: [],
  staff: [],
  bookings: [],
  services: [],
  lastUpdated: {
    customers: null,
    staff: null,
    bookings: null,
    services: null,
  },
  isLoading: {
    customers: false,
    staff: false,
    bookings: false,
    services: false,
  },
  error: {
    customers: null,
    staff: null,
    bookings: null,
    services: null,
  },
};

export const useDataStore = create<DataStore>()((set, get) => ({
  ...initialState,
  
  // Setters
  setCustomers: (customers) => set({
    customers,
    lastUpdated: { ...get().lastUpdated, customers: Date.now() },
    error: { ...get().error, customers: null },
  }),
  
  setStaff: (staff) => set({
    staff,
    lastUpdated: { ...get().lastUpdated, staff: Date.now() },
    error: { ...get().error, staff: null },
  }),
  
  setBookings: (bookings) => set({
    bookings,
    lastUpdated: { ...get().lastUpdated, bookings: Date.now() },
    error: { ...get().error, bookings: null },
  }),
  
  setServices: (services) => set({
    services,
    lastUpdated: { ...get().lastUpdated, services: Date.now() },
    error: { ...get().error, services: null },
  }),
  
  // Add single items
  addCustomer: (customer) => set((state) => ({
    customers: [...state.customers, customer],
  })),
  
  addStaff: (staff) => set((state) => ({
    staff: [...state.staff, staff],
  })),
  
  addBooking: (booking) => set((state) => ({
    bookings: [...state.bookings, booking],
  })),
  
  addService: (service) => set((state) => ({
    services: [...state.services, service],
  })),
  
  // Update items
  updateCustomer: (id, updates) => set((state) => ({
    customers: state.customers.map((c) =>
      c.id === id ? { ...c, ...updates } : c
    ),
  })),
  
  updateStaff: (id, updates) => set((state) => ({
    staff: state.staff.map((s) =>
      s.id === id ? { ...s, ...updates } : s
    ),
  })),
  
  updateBooking: (id, updates) => set((state) => ({
    bookings: state.bookings.map((b) =>
      b.id === id ? { ...b, ...updates } : b
    ),
  })),
  
  updateService: (id, updates) => set((state) => ({
    services: state.services.map((s) =>
      s.id === id ? { ...s, ...updates } : s
    ),
  })),
  
  // Remove items
  removeCustomer: (id) => set((state) => ({
    customers: state.customers.filter((c) => c.id !== id),
  })),
  
  removeStaff: (id) => set((state) => ({
    staff: state.staff.filter((s) => s.id !== id),
  })),
  
  removeBooking: (id) => set((state) => ({
    bookings: state.bookings.filter((b) => b.id !== id),
  })),
  
  removeService: (id) => set((state) => ({
    services: state.services.filter((s) => s.id !== id),
  })),
  
  // Loading states
  setLoading: (key, isLoading) => set((state) => ({
    isLoading: { ...state.isLoading, [key]: isLoading },
  })),
  
  // Error states
  setError: (key, error) => set((state) => ({
    error: { ...state.error, [key]: error },
  })),
  
  clearError: (key) => set((state) => ({
    error: { ...state.error, [key]: null },
  })),
  
  // Cache management
  clearCache: () => set({
    ...initialState,
    isLoading: initialState.isLoading,
    error: initialState.error,
  }),
  
  isStale: (key, maxAgeMs = 5 * 60 * 1000) => {
    const lastUpdated = get().lastUpdated[key];
    if (!lastUpdated) return true;
    return Date.now() - lastUpdated > maxAgeMs;
  },
}));

export default useDataStore;
