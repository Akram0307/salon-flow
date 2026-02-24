import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type { Staff, StaffCreate, StaffUpdate } from '../types';

export function useStaff(staffId: string) {
  return useQuery<Staff | null>({
    queryKey: ['staff', staffId],
    queryFn: async () => {
      try {
        return await api.get<Staff>(`/staff/${staffId}`);
      } catch {
        return null;
      }
    },
    enabled: !!staffId,
  });
}

export function useStaffList() {
  return useQuery<Staff[]>({
    queryKey: ['staff'],
    queryFn: async () => {
      try {
        return await api.get<Staff[]>('/staff');
      } catch {
        return [];
      }
    },
  });
}

export function useCreateStaff() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: StaffCreate) => {
      return await api.post<Staff>('/staff', data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff'] });
    },
  });
}

export function useUpdateStaff() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: StaffUpdate }) => {
      return await api.patch<Staff>(`/staff/${id}`, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff'] });
    },
  });
}

export function useDeleteStaff() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/staff/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff'] });
    },
  });
}
