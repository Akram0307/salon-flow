import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type { Booking, BookingStatus } from '../types';
import { BOOKING_ENDPOINTS } from '../api/endpoints';

// Query Keys
export const bookingKeys = {
  all: ['bookings'] as const,
  lists: () => [...bookingKeys.all, 'list'] as const,
  list: (params: BookingListParams) => [...bookingKeys.lists(), params] as const,
  detail: (id: string) => [...bookingKeys.all, 'detail', id] as const,
  byDate: (date: string) => [...bookingKeys.all, 'date', date] as const,
  byStaff: (staffId: string) => [...bookingKeys.all, 'staff', staffId] as const,
  byCustomer: (customerId: string) => [...bookingKeys.all, 'customer', customerId] as const,
};

// Types
export interface BookingListParams {
  status?: BookingStatus;
  staffId?: string;
  customerId?: string;
  date?: string;
  startDate?: string;
  endDate?: string;
  page?: number;
  limit?: number;
}

export interface CreateBookingData {
  customerId: string;
  staffId: string;
  date: string;
  startTime: string;
  services: Array<{
    serviceId: string;
    staffId: string;
    price: number;
    duration: number;
    gstRate?: number;
  }>;
  notes?: string;
}

export interface UpdateBookingData {
  id: string;
  data: Partial<CreateBookingData>;
}

export interface TimeSlot {
  startTime: string;
  endTime: string;
  available: boolean;
  staffId?: string;
  staffName?: string;
}

// Query Hooks

/**
 * Fetch bookings list with filters
 */
export const useBookings = (params: BookingListParams = {}) => {
  return useQuery<Booking[]>({
    queryKey: bookingKeys.list(params),
    queryFn: async () => {
      try {
        return await api.get<Booking[]>(BOOKING_ENDPOINTS.LIST, { params });
      } catch {
        return [];
      }
    },
  });
};

/**
 * Fetch single booking by ID
 */
export const useBooking = (id: string) => {
  return useQuery<Booking | null>({
    queryKey: bookingKeys.detail(id),
    queryFn: async () => {
      try {
        const response = await api.get<{ booking: Booking }>(BOOKING_ENDPOINTS.GET(id));
        return response.booking;
      } catch {
        return null;
      }
    },
    enabled: !!id,
  });
};

/**
 * Fetch bookings by date
 */
export const useBookingsByDate = (date: string) => {
  return useQuery<Booking[]>({
    queryKey: bookingKeys.byDate(date),
    queryFn: async () => {
      try {
        return await api.get<Booking[]>(BOOKING_ENDPOINTS.BY_DATE(date));
      } catch {
        return [];
      }
    },
    enabled: !!date,
  });
};

/**
 * Fetch bookings by staff
 */
export const useBookingsByStaff = (staffId: string) => {
  return useQuery<Booking[]>({
    queryKey: bookingKeys.byStaff(staffId),
    queryFn: async () => {
      try {
        return await api.get<Booking[]>(BOOKING_ENDPOINTS.BY_STAFF(staffId));
      } catch {
        return [];
      }
    },
    enabled: !!staffId,
  });
};

/**
 * Fetch bookings by customer
 */
export const useBookingsByCustomer = (customerId: string) => {
  return useQuery<Booking[]>({
    queryKey: bookingKeys.byCustomer(customerId),
    queryFn: async () => {
      try {
        return await api.get<Booking[]>(BOOKING_ENDPOINTS.BY_CUSTOMER(customerId));
      } catch {
        return [];
      }
    },
    enabled: !!customerId,
  });
};

/**
 * Fetch available time slots
 */
export const useAvailableSlots = (params: { date: string; staffId?: string; serviceId?: string }) => {
  return useQuery<TimeSlot[]>({
    queryKey: ['slots', params],
    queryFn: async () => {
      try {
        return await api.get<TimeSlot[]>(BOOKING_ENDPOINTS.CHECK_SLOTS, { params });
      } catch {
        return [];
      }
    },
    enabled: !!params.date,
  });
};

// Mutation Hooks

/**
 * Create new booking
 */
export const useCreateBooking = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateBookingData) => {
      const response = await api.post<{ booking: Booking }>(BOOKING_ENDPOINTS.CREATE, data);
      return response.booking;
    },
    onSuccess: (newBooking) => {
      queryClient.invalidateQueries({ queryKey: bookingKeys.lists() });
      if (newBooking?.date) {
        queryClient.invalidateQueries({ queryKey: bookingKeys.byDate(newBooking.date) });
      }
    },
  });
};

/**
 * Update booking
 */
export const useUpdateBooking = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: UpdateBookingData) => {
      const response = await api.patch<{ booking: Booking }>(BOOKING_ENDPOINTS.UPDATE(id), data);
      return response.booking;
    },
    onSuccess: (updatedBooking) => {
      if (updatedBooking?.id) {
        queryClient.setQueryData(bookingKeys.detail(updatedBooking.id), updatedBooking);
      }
      queryClient.invalidateQueries({ queryKey: bookingKeys.lists() });
    },
  });
};

/**
 * Delete booking
 */
export const useDeleteBooking = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(BOOKING_ENDPOINTS.DELETE(id));
    },
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: bookingKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: bookingKeys.lists() });
    },
  });
};

/**
 * Cancel booking
 */
export const useCancelBooking = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, reason }: { id: string; reason?: string }) => {
      const response = await api.post<{ booking: Booking }>(BOOKING_ENDPOINTS.CANCEL(id), { reason });
      return response.booking;
    },
    onSuccess: (cancelledBooking) => {
      if (cancelledBooking?.id) {
        queryClient.setQueryData(bookingKeys.detail(cancelledBooking.id), cancelledBooking);
      }
      queryClient.invalidateQueries({ queryKey: bookingKeys.lists() });
    },
  });
};

/**
 * Confirm booking
 */
export const useConfirmBooking = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.post<{ booking: Booking }>(BOOKING_ENDPOINTS.CONFIRM(id));
      return response.booking;
    },
    onSuccess: (confirmedBooking) => {
      if (confirmedBooking?.id) {
        queryClient.setQueryData(bookingKeys.detail(confirmedBooking.id), confirmedBooking);
      }
      queryClient.invalidateQueries({ queryKey: bookingKeys.lists() });
    },
  });
};

/**
 * Complete booking
 */
export const useCompleteBooking = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.post<{ booking: Booking }>(BOOKING_ENDPOINTS.COMPLETE(id));
      return response.booking;
    },
    onSuccess: (completedBooking) => {
      if (completedBooking?.id) {
        queryClient.setQueryData(bookingKeys.detail(completedBooking.id), completedBooking);
      }
      queryClient.invalidateQueries({ queryKey: bookingKeys.lists() });
    },
  });
};

/**
 * Fetch calendar events for date range
 */
export const useBookingCalendar = (startDate: string, endDate: string) => {
  return useQuery<Booking[]>({
    queryKey: ['bookings', 'calendar', startDate, endDate],
    queryFn: async () => {
      try {
        return await api.get<Booking[]>(BOOKING_ENDPOINTS.CALENDAR, { params: { startDate, endDate } });
      } catch {
        return [];
      }
    },
    enabled: !!startDate && !!endDate,
  });
};

/**
 * Get available slots helper
 */
export const getAvailableSlots = async (params: { date: string; staffId?: string; serviceId?: string; duration?: number }) => {
  try {
    return await api.get<TimeSlot[]>(BOOKING_ENDPOINTS.CHECK_SLOTS, { params });
  } catch {
    return [];
  }
};
