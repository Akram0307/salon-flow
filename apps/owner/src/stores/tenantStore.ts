import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface SalonSettings {
  theme: 'light' | 'dark' | 'system';
  currency: string;
  timezone: string;
  dateFormat: string;
  timeFormat: '12h' | '24h';
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
}

export interface Salon {
  id: string;
  name: string;
  address?: string;
  phone?: string;
  email?: string;
  gstNumber?: string;
  logo?: string;
  settings: SalonSettings;
}

export interface TenantState {
  currentSalon: Salon | null;
  salons: Salon[];
  isLoading: boolean;
  error: string | null;
}

export interface TenantActions {
  setCurrentSalon: (salon: Salon | null) => void;
  setSalons: (salons: Salon[]) => void;
  addSalon: (salon: Salon) => void;
  updateSalon: (salonId: string, updates: Partial<Salon>) => void;
  removeSalon: (salonId: string) => void;
  updateSettings: (settings: Partial<SalonSettings>) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

export type TenantStore = TenantState & TenantActions;

const initialState: TenantState = {
  currentSalon: null,
  salons: [],
  isLoading: false,
  error: null,
};

export const useTenantStore = create<TenantStore>()(
  persist(
    (set) => ({
      ...initialState,
      
      setCurrentSalon: (salon) => set({ 
        currentSalon: salon,
        error: null,
      }),
      
      setSalons: (salons) => set({ salons }),
      
      addSalon: (salon) => set((state) => ({
        salons: [...state.salons, salon],
        currentSalon: state.currentSalon || salon,
      })),
      
      updateSalon: (salonId, updates) => set((state) => {
        const updatedSalons = state.salons.map((salon) =>
          salon.id === salonId ? { ...salon, ...updates } : salon
        );
        const updatedCurrent = state.currentSalon?.id === salonId
          ? { ...state.currentSalon, ...updates }
          : state.currentSalon;
        
        return {
          salons: updatedSalons,
          currentSalon: updatedCurrent,
        };
      }),
      
      removeSalon: (salonId) => set((state) => {
        const filteredSalons = state.salons.filter((salon) => salon.id !== salonId);
        return {
          salons: filteredSalons,
          currentSalon: state.currentSalon?.id === salonId
            ? filteredSalons[0] || null
            : state.currentSalon,
        };
      }),
      
      updateSettings: (settings) => set((state) => {
        if (!state.currentSalon) return state;
        
        const updatedSalon = {
          ...state.currentSalon,
          settings: { ...state.currentSalon.settings, ...settings },
        };
        
        return {
          currentSalon: updatedSalon,
          salons: state.salons.map((salon) =>
            salon.id === updatedSalon.id ? updatedSalon : salon
          ),
        };
      }),
      
      setLoading: (isLoading) => set({ isLoading }),
      
      setError: (error) => set({ error }),
      
      clearError: () => set({ error: null }),
    }),
    {
      name: 'salon-flow-tenant-storage',
      partialize: (state) => ({
        currentSalon: state.currentSalon,
        salons: state.salons,
      }),
    }
  )
);

export default useTenantStore;
