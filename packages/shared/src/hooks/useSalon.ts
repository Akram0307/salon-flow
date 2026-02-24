import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type { Salon, SalonUpdate } from '../types';

export interface UseSalonReturn {
  salon: Salon | null;
  isLoading: boolean;
  error: string | null;
  updateSalon: (data: SalonUpdate) => Promise<void>;
}

export function useSalon(): UseSalonReturn {
  const queryClient = useQueryClient();

  const { data: salon, isLoading, error } = useQuery<Salon | null>({
    queryKey: ['salon'],
    queryFn: async () => {
      try {
        // api.get already returns the data directly (not AxiosResponse)
        return await api.get<Salon>('/tenants/me');
      } catch (err) {
        console.error('Failed to fetch salon:', err);
        return null;
      }
    },
  });

  const updateMutation = useMutation({
    mutationFn: async (data: SalonUpdate) => {
      // api.patch already returns the data directly
      return await api.patch<Salon>('/tenants/me', data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['salon'] });
    },
  });

  const updateSalon = async (data: SalonUpdate) => {
    await updateMutation.mutateAsync(data);
  };

  return {
    salon: salon ?? null,
    isLoading,
    error: error?.message ?? null,
    updateSalon,
  };
}

export function useUpdateSalon() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: SalonUpdate) => {
      return await api.patch<Salon>('/tenants/me', data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['salon'] });
    },
  });
}
