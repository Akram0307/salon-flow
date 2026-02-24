import { z } from 'zod';

// ============== Common Validation Schemas ==============

/**
 * Email validation schema
 */
export const emailSchema = z
  .string()
  .min(1, 'Email is required')
  .email('Invalid email address')
  .transform((email) => email.toLowerCase().trim());

/**
 * Password validation schema (min 8 chars, 1 uppercase, 1 lowercase, 1 number)
 */
export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number');

/**
 * Simple password schema (just min length)
 */
export const simplePasswordSchema = z
  .string()
  .min(6, 'Password must be at least 6 characters');

/**
 * Phone validation schema (Indian numbers)
 */
export const phoneSchema = z
  .string()
  .min(10, 'Phone number must be at least 10 digits')
  .max(13, 'Phone number must be at most 13 digits')
  .regex(/^[+]?[0-9]{10,13}$/, 'Invalid phone number')
  .transform((phone) => phone.replace(/\D/g, ''));

/**
 * Indian phone validation (10 digits or with +91)
 */
export const indianPhoneSchema = z
  .string()
  .transform((phone) => phone.replace(/\D/g, ''))
  .refine(
    (phone) => {
      // 10 digits or 12 digits starting with 91
      return (phone.length === 10) || (phone.length === 12 && phone.startsWith('91'));
    },
    { message: 'Invalid Indian phone number' }
  );

/**
 * Name validation schema
 */
export const nameSchema = z
  .string()
  .min(2, 'Name must be at least 2 characters')
  .max(50, 'Name must be at most 50 characters')
  .regex(/^[a-zA-Z\s'-]+$/, 'Name can only contain letters, spaces, hyphens, and apostrophes')
  .transform((name) => name.trim());

/**
 * GST number validation schema
 */
export const gstSchema = z
  .string()
  .regex(
    /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/i,
    'Invalid GST number format'
  )
  .transform((gst) => gst.toUpperCase())
  .optional()
  .or(z.literal(''));

/**
 * Pincode validation schema (Indian)
 */
export const pincodeSchema = z
  .string()
  .regex(/^[1-9][0-9]{5}$/, 'Invalid pincode')
  .transform((pin) => pin.trim());

/**
 * Price validation schema
 */
export const priceSchema = z
  .number()
  .min(0, 'Price cannot be negative')
  .max(1000000, 'Price exceeds maximum limit');

/**
 * Duration validation schema (in minutes)
 */
export const durationSchema = z
  .number()
  .int('Duration must be a whole number')
  .min(5, 'Minimum duration is 5 minutes')
  .max(480, 'Maximum duration is 8 hours');

/**
 * Time validation schema (HH:MM format)
 */
export const timeSchema = z
  .string()
  .regex(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/, 'Invalid time format (use HH:MM)');

/**
 * Date validation schema (ISO format)
 */
export const dateSchema = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}$/, 'Invalid date format (use YYYY-MM-DD)')
  .refine(
    (date) => !isNaN(Date.parse(date)),
    { message: 'Invalid date' }
  );

/**
 * ID validation schema
 */
export const idSchema = z.string().min(1, 'ID is required');

// ============== Form Validation Schemas ==============

/**
 * Login form schema
 */
export const loginFormSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
  rememberMe: z.boolean().optional(),
});

/**
 * Registration form schema
 */
export const registerFormSchema = z.object({
  firstName: nameSchema,
  lastName: nameSchema,
  email: emailSchema,
  phone: indianPhoneSchema,
  salonName: z.string().min(1, 'Salon name is required'),
  password: passwordSchema,
  confirmPassword: z.string(),
  acceptTerms: z.boolean().refine((val) => val === true, {
    message: 'You must accept the terms and conditions',
  }),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

/**
 * Forgot password form schema
 */
export const forgotPasswordFormSchema = z.object({
  email: emailSchema,
});

/**
 * Reset password form schema
 */
export const resetPasswordFormSchema = z.object({
  password: passwordSchema,
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

/**
 * Customer form schema
 */
export const customerFormSchema = z.object({
  firstName: nameSchema,
  lastName: nameSchema.optional().or(z.literal('')),
  email: emailSchema.optional().or(z.literal('')),
  phone: indianPhoneSchema,
  gender: z.enum(['male', 'female', 'other']).optional(),
  dateOfBirth: z.string().optional().or(z.literal('')),
  anniversary: z.string().optional().or(z.literal('')),
  address: z.string().max(500).optional().or(z.literal('')),
  notes: z.string().max(1000).optional().or(z.literal('')),
});

/**
 * Staff form schema
 */
export const staffFormSchema = z.object({
  firstName: nameSchema,
  lastName: nameSchema.optional().or(z.literal('')),
  email: emailSchema,
  phone: indianPhoneSchema,
  role: z.enum(['owner', 'manager', 'receptionist', 'stylist', 'senior_stylist', 'colorist', 'therapist']),
  specialization: z.array(z.string()).optional(),
  commission: z.number().min(0).max(100).optional(),
  isActive: z.boolean(),
});

/**
 * Service form schema
 */
export const serviceFormSchema = z.object({
  name: z.string().min(2, 'Service name is required').max(100),
  description: z.string().max(500).optional().or(z.literal('')),
  category: z.enum(['hair', 'skin', 'nails', 'makeup', 'bridal', 'spa', 'treatment']),
  duration: durationSchema,
  price: priceSchema,
  gstRate: z.number().min(0).max(28).default(5),
  isActive: z.boolean(),
});

/**
 * Booking form schema
 */
export const bookingFormSchema = z.object({
  customerId: idSchema,
  staffId: idSchema,
  date: dateSchema,
  startTime: timeSchema,
  services: z.array(z.object({
    serviceId: idSchema,
    staffId: idSchema,
  price: priceSchema,
  duration: durationSchema,
  gstRate: z.number().min(0).max(28).default(5),
  })).min(1, 'At least one service is required'),
  notes: z.string().max(500).optional().or(z.literal('')),
});

/**
 * Salon profile form schema
 */
export const salonProfileFormSchema = z.object({
  name: z.string().min(2, 'Salon name is required').max(100),
  logo: z.string().url().optional().or(z.literal('')),
  address: z.string().min(5, 'Address is required').max(500),
  city: z.string().min(2, 'City is required').max(100),
  state: z.string().min(2, 'State is required').max(100),
  pincode: pincodeSchema,
  phone: indianPhoneSchema,
  email: emailSchema,
  gstNumber: gstSchema,
});

/**
 * Working hours schema
 */
export const workingHoursSchema = z.object({
  monday: z.object({ open: timeSchema, close: timeSchema }).nullable(),
  tuesday: z.object({ open: timeSchema, close: timeSchema }).nullable(),
  wednesday: z.object({ open: timeSchema, close: timeSchema }).nullable(),
  thursday: z.object({ open: timeSchema, close: timeSchema }).nullable(),
  friday: z.object({ open: timeSchema, close: timeSchema }).nullable(),
  saturday: z.object({ open: timeSchema, close: timeSchema }).nullable(),
  sunday: z.object({ open: timeSchema, close: timeSchema }).nullable(),
});

/**
 * Payment form schema
 */
export const paymentFormSchema = z.object({
  bookingId: idSchema.optional(),
  customerId: idSchema,
  amount: priceSchema,
  method: z.enum(['cash', 'card', 'upi', 'wallet', 'membership']),
  notes: z.string().max(500).optional().or(z.literal('')),
});

// ============== Validation Helper Functions ==============

/**
 * Validate a single field value
 */
export const validateField = <T>(
  schema: z.ZodSchema<T>,
  value: unknown
): { success: boolean; error?: string } => {
  const result = schema.safeParse(value);
  if (result.success) {
    return { success: true };
  }
  return {
    success: false,
    error: result.error.errors[0]?.message || 'Validation failed',
  };
};

/**
 * Validate form data
 */
export const validateForm = <T>(
  schema: z.ZodSchema<T>,
  data: unknown
): { success: boolean; data?: T; errors?: Record<string, string> } => {
  const result = schema.safeParse(data);
  if (result.success) {
    return { success: true, data: result.data };
  }
  
  const errors: Record<string, string> = {};
  result.error.errors.forEach((error) => {
    const path = error.path.join('.');
    errors[path] = error.message;
  });
  
  return { success: false, errors };
};

/**
 * Get validation error message
 */
export const getErrorMessage = (error: unknown): string => {
  if (error instanceof z.ZodError) {
    return error.errors[0]?.message || 'Validation failed';
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
};

/**
 * Check if value is valid email
 */
export const isValidEmail = (email: string): boolean => {
  return emailSchema.safeParse(email).success;
};

/**
 * Check if value is valid phone
 */
export const isValidPhone = (phone: string): boolean => {
  return indianPhoneSchema.safeParse(phone).success;
};

/**
 * Check if value is valid GST
 */
export const isValidGst = (gst: string): boolean => {
  return gstSchema.safeParse(gst).success;
};

/**
 * Check if value is valid pincode
 */
export const isValidPincode = (pincode: string): boolean => {
  return pincodeSchema.safeParse(pincode).success;
};

/**
 * Check if value is valid price
 */
export const isValidPrice = (price: number): boolean => {
  return priceSchema.safeParse(price).success;
};

/**
 * Check if value is valid time
 */
export const isValidTime = (time: string): boolean => {
  return timeSchema.safeParse(time).success;
};

/**
 * Check if value is valid date
 */
export const isValidDate = (date: string): boolean => {
  return dateSchema.safeParse(date).success;
};

export default {
  // Schemas
  emailSchema,
  passwordSchema,
  simplePasswordSchema,
  phoneSchema,
  indianPhoneSchema,
  nameSchema,
  gstSchema,
  pincodeSchema,
  priceSchema,
  durationSchema,
  timeSchema,
  dateSchema,
  idSchema,
  // Form schemas
  loginFormSchema,
  registerFormSchema,
  forgotPasswordFormSchema,
  resetPasswordFormSchema,
  customerFormSchema,
  staffFormSchema,
  serviceFormSchema,
  bookingFormSchema,
  salonProfileFormSchema,
  workingHoursSchema,
  paymentFormSchema,
  // Helpers
  validateField,
  validateForm,
  getErrorMessage,
  isValidEmail,
  isValidPhone,
  isValidGst,
  isValidPincode,
  isValidPrice,
  isValidTime,
  isValidDate,
};


// Form Data Types
export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName?: string;
  phone: string;
  salonName: string;
}

export interface ForgotPasswordFormData {
  email: string;
}
