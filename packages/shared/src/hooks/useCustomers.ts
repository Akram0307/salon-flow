import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type { Customer } from '../types';
import { CUSTOMER_ENDPOINTS } from '../api/endpoints';

// Query Keys
export const customerKeys = {
  all: ['customers'] as const,
  lists: () => [...customerKeys.all, 'list'] as const,
  list: (params: { search?: string; page?: number; limit?: number }) => [...customerKeys.lists(), params] as const,
  detail: (id: string) => [...customerKeys.all, 'detail', id] as const,
};

// Query Hooks

/**
 * Fetch customers list
 */
export const useCustomers = (params: { search?: string; page?: number; limit?: number } = {}) => {
  return useQuery<Customer[]>({
    queryKey: customerKeys.list(params),
    queryFn: async () => {
      try {
        return await api.get<Customer[]>(CUSTOMER_ENDPOINTS.LIST, { params });
      } catch {
        return [];
      }
    },
  });
};

/**
 * Fetch single customer by ID
 */
export const useCustomer = (id: string) => {
  return useQuery<Customer | null>({
    queryKey: customerKeys.detail(id),
    queryFn: async () => {
      try {
        const response = await api.get<{ customer: Customer }>(CUSTOMER_ENDPOINTS.GET(id));
        return response.customer;
      } catch {
        return null;
      }
    },
    enabled: !!id,
  });
};

/**
 * Fetch customer bookings
 */
export const useCustomerBookings = (customerId: string) => {
  return useQuery({
    queryKey: ['customer-bookings', customerId],
    queryFn: async () => {
      try {
        return await api.get(`/customers/${customerId}/bookings`);
      } catch {
        return [];
      }
    },
    enabled: !!customerId,
  });
};

// Mutation Hooks

export interface CreateCustomerData {
  firstName: string;
  lastName?: string;
  phone: string;
  email?: string;
  dateOfBirth?: string;
  gender?: 'male' | 'female' | 'other';
  address?: string;
  notes?: string;
}

/**
 * Create new customer
 */
export const useCreateCustomer = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateCustomerData) => {
      const response = await api.post<{ customer: Customer }>(CUSTOMER_ENDPOINTS.CREATE, data);
      return response.customer;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: customerKeys.lists() });
    },
  });
};

/**
 * Update customer
 */
export const useUpdateCustomer = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<CreateCustomerData> }) => {
      const response = await api.patch<{ customer: Customer }>(CUSTOMER_ENDPOINTS.UPDATE(id), data);
      return response.customer;
    },
    onSuccess: (updatedCustomer) => {
      if (updatedCustomer?.id) {
        queryClient.setQueryData(customerKeys.detail(updatedCustomer.id), updatedCustomer);
      }
      queryClient.invalidateQueries({ queryKey: customerKeys.lists() });
    },
  });
};

/**
 * Delete customer
 */
export const useDeleteCustomer = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(CUSTOMER_ENDPOINTS.DELETE(id));
    },
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: customerKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: customerKeys.lists() });
    },
  });
};
