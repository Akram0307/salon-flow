import { useCallback, useEffect } from 'react';
import { useTenantStore } from '@/stores';
import { api } from '@salon-flow/shared';
import type { Salon, SalonSettings } from '@/stores';

export interface UseTenantReturn {
  currentSalon: Salon | null;
  salons: Salon[];
  isLoading: boolean;
  error: string | null;
  setCurrentSalon: (salon: Salon | null) => void;
  updateSettings: (settings: Partial<SalonSettings>) => void;
  fetchSalons: () => Promise<void>;
  createSalon: (salonData: Omit<Salon, 'id'>) => Promise<Salon>;
  updateSalon: (salonId: string, updates: Partial<Salon>) => Promise<void>;
  switchSalon: (salonId: string) => void;
}

/**
 * Hook for managing multi-tenant salon context
 * Handles salon switching, settings management, and API integration
 */
export const useTenant = (): UseTenantReturn => {
  const store = useTenantStore();

  // Fetch salons on mount if not loaded
  useEffect(() => {
    if (store.salons.length === 0 && !store.isLoading) {
      fetchSalons();
    }
  }, []);

  const fetchSalons = useCallback(async () => {
    try {
      store.setLoading(true);
      store.setError(null);
      
      // Fetch from API
      const response = await api.get<{ salons: Salon[] }>('/tenants/salons');
      store.setSalons(response.salons);
      
      // Set first salon as current if none selected
      if (!store.currentSalon && response.salons.length > 0) {
        store.setCurrentSalon(response.salons[0]);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch salons';
      store.setError(message);
    } finally {
      store.setLoading(false);
    }
  }, [store]);

  const createSalon = useCallback(async (salonData: Omit<Salon, 'id'>) => {
    try {
      store.setLoading(true);
      store.setError(null);
      
      const response = await api.post<{ salon: Salon }>('/tenants/salons', salonData);
      store.addSalon(response.salon);
      
      return response.salon;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create salon';
      store.setError(message);
      throw error;
    } finally {
      store.setLoading(false);
    }
  }, [store]);

  const updateSalon = useCallback(async (salonId: string, updates: Partial<Salon>) => {
    try {
      store.setLoading(true);
      store.setError(null);
      
      await api.put(`/tenants/salons/${salonId}`, updates);
      store.updateSalon(salonId, updates);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update salon';
      store.setError(message);
      throw error;
    } finally {
      store.setLoading(false);
    }
  }, [store]);

  const switchSalon = useCallback((salonId: string) => {
    const salon = store.salons.find((s) => s.id === salonId);
    if (salon) {
      store.setCurrentSalon(salon);
      // Store in localStorage for API client to use
      localStorage.setItem('salon_id', salonId);
    }
  }, [store]);

  const updateSettings = useCallback((settings: Partial<SalonSettings>) => {
    store.updateSettings(settings);
    
    // Sync to API if we have a current salon
    if (store.currentSalon) {
      updateSalon(store.currentSalon.id, {
        settings: { ...store.currentSalon.settings, ...settings },
      }).catch(console.error);
    }
  }, [store]);

  return {
    currentSalon: store.currentSalon,
    salons: store.salons,
    isLoading: store.isLoading,
    error: store.error,
    setCurrentSalon: store.setCurrentSalon,
    updateSettings,
    fetchSalons,
    createSalon,
    updateSalon,
    switchSalon,
  };
};

export default useTenant;
