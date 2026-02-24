// Types
export * from './types';
// Additional exports
export type { CreateBookingData, BookingFormData } from './types';

// API
export { api } from './api/client';
export { API_BASE_URL, AUTH_ENDPOINTS, TENANT_ENDPOINTS, BOOKING_ENDPOINTS, CUSTOMER_ENDPOINTS, STAFF_ENDPOINTS, SERVICE_ENDPOINTS, PAYMENT_ENDPOINTS, ANALYTICS_ENDPOINTS, AI_ENDPOINTS } from './api/endpoints';

// Hooks
export { useAuth } from './hooks/useAuth';
export { useSalon, useUpdateSalon } from './hooks/useSalon';
export { useServices, useCreateService, useUpdateService, useDeleteService } from './hooks/useServices';
export { useStaff, useStaffList, useCreateStaff, useUpdateStaff, useDeleteStaff } from './hooks/useStaff';
export { useBookings, useBooking, useCreateBooking, useUpdateBooking, useCancelBooking, useDeleteBooking, useBookingCalendar, getAvailableSlots } from './hooks/useBookings';
export { useCustomers, useCustomer, useCreateCustomer, useUpdateCustomer, useDeleteCustomer } from './hooks/useCustomers';
export { usePayments, usePayment } from './hooks/usePayments';

// Utils
export { formatCurrency, formatDate, formatTime, formatPhone, formatName, getInitials, formatDuration, formatSmartDate, formatDateTime, formatRelativeTime } from './utils/formatters';

// Validators
export { 
  isValidEmail, 
  isValidPhone, 
  isValidGst, 
  isValidPincode, 
  isValidPrice, 
  isValidTime, 
  isValidDate,
  validateField,
  validateForm,
  getErrorMessage,
  loginFormSchema,
  registerFormSchema,
  forgotPasswordFormSchema,
  customerFormSchema,
  staffFormSchema,
  serviceFormSchema,
  bookingFormSchema,
  salonProfileFormSchema,
  workingHoursSchema,
} from './utils/validators';
