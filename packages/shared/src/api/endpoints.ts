/**
 * API Endpoint Constants
 * Base URL: https://salon-flow-api-1050147155341.asia-south1.run.app/api/v1
 */

export const API_BASE_URL = 'https://salon-flow-api-1050147155341.asia-south1.run.app/api/v1';

// ============== Auth Endpoints ==============
export const AUTH_ENDPOINTS = {
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  LOGOUT: '/auth/logout',
  ME: '/auth/me',
  REFRESH: '/auth/refresh',
  FORGOT_PASSWORD: '/auth/forgot-password',
  RESET_PASSWORD: '/auth/reset-password',
  VERIFY_EMAIL: '/auth/verify-email',
  UPDATE_PASSWORD: '/auth/update-password',
} as const;

// ============== Tenant/Salon Endpoints ==============
export const TENANT_ENDPOINTS = {
  LIST: '/tenants/',
  GET: (id: string) => `/tenants/${id}`,
  CREATE: '/tenants/',
  UPDATE: (id: string) => `/tenants/${id}`,
  DELETE: (id: string) => `/tenants/${id}`,
  SETTINGS: (id: string) => `/tenants/${id}/settings`,
  WORKING_HOURS: (id: string) => `/tenants/${id}/working-hours`,
  LOGO: (id: string) => `/tenants/${id}/logo`,
} as const;

// ============== Booking Endpoints ==============
export const BOOKING_ENDPOINTS = {
  LIST: '/bookings/',
  GET: (id: string) => `/bookings/${id}`,
  CREATE: '/bookings/',
  UPDATE: (id: string) => `/bookings/${id}`,
  DELETE: (id: string) => `/bookings/${id}`,
  CANCEL: (id: string) => `/bookings/${id}/cancel`,
  CONFIRM: (id: string) => `/bookings/${id}/confirm`,
  COMPLETE: (id: string) => `/bookings/${id}/complete`,
  START: (id: string) => `/bookings/${id}/start`,
  BY_DATE: (date: string) => `/bookings/date/${date}`,
  BY_STAFF: (staffId: string) => `/bookings/staff/${staffId}`,
  BY_CUSTOMER: (customerId: string) => `/bookings/customer/${customerId}`,
  CHECK_SLOTS: '/bookings/slots',
  CALENDAR: '/bookings/calendar',
} as const;

// ============== Customer Endpoints ==============
export const CUSTOMER_ENDPOINTS = {
  LIST: '/customers/',
  GET: (id: string) => `/customers/${id}`,
  CREATE: '/customers/',
  UPDATE: (id: string) => `/customers/${id}`,
  DELETE: (id: string) => `/customers/${id}`,
  SEARCH: '/customers/search',
  HISTORY: (id: string) => `/customers/${id}/history`,
  LOYALTY: (id: string) => `/customers/${id}/loyalty`,
  MEMBERSHIP: (id: string) => `/customers/${id}/membership`,
  NOTES: (id: string) => `/customers/${id}/notes`,
} as const;

// ============== Staff Endpoints ==============
export const STAFF_ENDPOINTS = {
  LIST: '/staff/',
  GET: (id: string) => `/staff/${id}`,
  CREATE: '/staff/',
  UPDATE: (id: string) => `/staff/${id}`,
  DELETE: (id: string) => `/staff/${id}`,
  SCHEDULE: (id: string) => `/staff/${id}/schedule`,
  AVAILABILITY: (id: string) => `/staff/${id}/availability`,
  SERVICES: (id: string) => `/staff/${id}/services`,
  PERFORMANCE: (id: string) => `/staff/${id}/performance`,
  COMMISSIONS: (id: string) => `/staff/${id}/commissions`,
} as const;

// ============== Service Endpoints ==============
export const SERVICE_ENDPOINTS = {
  LIST: '/services/',
  GET: (id: string) => `/services/${id}`,
  CREATE: '/services/',
  UPDATE: (id: string) => `/services/${id}`,
  DELETE: (id: string) => `/services/${id}`,
  BY_CATEGORY: (category: string) => `/services/category/${category}`,
  BY_STAFF: (staffId: string) => `/services/staff/${staffId}`,
  CATEGORIES: '/services/categories',
} as const;

// ============== Payment Endpoints ==============
export const PAYMENT_ENDPOINTS = {
  LIST: '/payments/',
  GET: (id: string) => `/payments/${id}`,
  CREATE: '/payments/',
  REFUND: (id: string) => `/payments/${id}/refund`,
  BY_BOOKING: (bookingId: string) => `/payments/booking/${bookingId}`,
  BY_CUSTOMER: (customerId: string) => `/payments/customer/${customerId}`,
} as const;

// ============== Analytics Endpoints ==============
export const ANALYTICS_ENDPOINTS = {
  REVENUE: '/analytics/revenue',
  BOOKINGS: '/analytics/bookings',
  CUSTOMERS: '/analytics/customers',
  STAFF_PERFORMANCE: '/analytics/staff-performance',
  SERVICES_POPULARITY: '/analytics/services-popularity',
  PEAK_HOURS: '/analytics/peak-hours',
  DASHBOARD: '/analytics/dashboard',
  EXPORT: '/analytics/export',
} as const;

// ============== AI Endpoints ==============
export const AI_ENDPOINTS = {
  HEALTH: '/ai/health',
  AGENTS: '/ai/agents',
  CHAT: '/ai/chat',
  CHAT_STREAM: '/ai/chat/stream',
  INSIGHTS: '/ai/insights',
  SUGGESTIONS: '/ai/suggestions',
  MARKETING_CAMPAIGNS: '/ai/marketing/campaigns',
  MARKETING_GENERATE: '/ai/marketing/generate',
} as const;

// ============== Integration Endpoints ==============
export const INTEGRATION_ENDPOINTS = {
  LIST: '/integrations/',
  TWILIO_CONFIG: '/integrations/twilio',
  TWILIO_TEST: '/integrations/twilio/test',
  WHATSAPP_CONFIG: '/integrations/whatsapp',
  WHATSAPP_TEST: '/integrations/whatsapp/test',
} as const;

// ============== Membership Endpoints ==============
export const MEMBERSHIP_ENDPOINTS = {
  LIST: '/memberships/',
  GET: (id: string) => `/memberships/${id}`,
  CREATE: '/memberships/',
  UPDATE: (id: string) => `/memberships/${id}`,
  DELETE: (id: string) => `/memberships/${id}`,
  PLANS: '/memberships/plans',
} as const;

// ============== Shift Endpoints ==============
export const SHIFT_ENDPOINTS = {
  LIST: '/shifts/',
  GET: (id: string) => `/shifts/${id}`,
  CREATE: '/shifts/',
  UPDATE: (id: string) => `/shifts/${id}`,
  DELETE: (id: string) => `/shifts/${id}`,
  BY_STAFF: (staffId: string) => `/shifts/staff/${staffId}`,
  BY_DATE: (date: string) => `/shifts/date/${date}`,
} as const;

// ============== Resource Endpoints ==============
export const RESOURCE_ENDPOINTS = {
  LIST: '/resources/',
  GET: (id: string) => `/resources/${id}`,
  CREATE: '/resources/',
  UPDATE: (id: string) => `/resources/${id}`,
  DELETE: (id: string) => `/resources/${id}`,
  AVAILABILITY: (id: string) => `/resources/${id}/availability`,
} as const;

// ============== Notification Endpoints ==============
export const NOTIFICATION_ENDPOINTS = {
  LIST: '/notifications/',
  GET: (id: string) => `/notifications/${id}`,
  MARK_READ: (id: string) => `/notifications/${id}/read`,
  MARK_ALL_READ: '/notifications/read-all',
  PREFERENCES: '/notifications/preferences',
} as const;

export default {
  AUTH: AUTH_ENDPOINTS,
  TENANT: TENANT_ENDPOINTS,
  BOOKING: BOOKING_ENDPOINTS,
  CUSTOMER: CUSTOMER_ENDPOINTS,
  STAFF: STAFF_ENDPOINTS,
  SERVICE: SERVICE_ENDPOINTS,
  PAYMENT: PAYMENT_ENDPOINTS,
  ANALYTICS: ANALYTICS_ENDPOINTS,
  AI: AI_ENDPOINTS,
  INTEGRATION: INTEGRATION_ENDPOINTS,
  MEMBERSHIP: MEMBERSHIP_ENDPOINTS,
  SHIFT: SHIFT_ENDPOINTS,
  RESOURCE: RESOURCE_ENDPOINTS,
  NOTIFICATION: NOTIFICATION_ENDPOINTS,
};
