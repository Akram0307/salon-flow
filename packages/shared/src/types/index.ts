// Staff Types
export type StaffRole = 'owner' | 'manager' | 'receptionist' | 'stylist' | 'senior_stylist' | 'colorist' | 'therapist';

export interface StaffSchedule {
  dayOfWeek: number;
  startTime: string;
  endTime: string;
  isWorking: boolean;
}

export interface Staff {
  id: string;
  firstName: string;
  lastName: string;
  name?: string;
  email: string;
  phone: string;
  role: StaffRole;
  specialization?: string[];
  commission?: number;
  isActive: boolean;
  photoURL?: string;
  schedule: StaffSchedule[];
  createdAt?: string;
  updatedAt?: string;
  // Stats
  totalBookings?: number;
  totalRevenue?: number;
  rating?: number;
  completionRate?: number;
}

export interface StaffCreate {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  role: StaffRole;
  specialization?: string[];
  commission?: number;
  isActive?: boolean;
  schedule?: StaffSchedule[];
}

export interface StaffUpdate extends Partial<StaffCreate> {
  id?: string;
}

// Service Types
export type ServiceCategory = 'hair' | 'skin' | 'nails' | 'makeup' | 'bridal' | 'spa' | 'treatment';

export interface Service {
  id: string;
  name: string;
  description?: string;
  category: ServiceCategory;
  duration: number;
  price: number;
  gstRate: number;
  isActive?: boolean;
  createdAt?: string;
  updatedAt?: string;
}

export interface ServiceCreate {
  name: string;
  description?: string;
  category: ServiceCategory;
  duration: number;
  price: number;
  gstRate: number;
}

export interface ServiceUpdate extends Partial<ServiceCreate> {}

// Booking Types
export type BookingStatus = 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled' | 'no_show';

export interface Booking {
  id: string;
  customerId: string;
  customerName?: string;
  customerPhone?: string;
  staffId: string;
  staffName?: string;
  serviceId: string;
  serviceName?: string;
  date: string;
  startTime: string;
  endTime: string;
  status: BookingStatus;
  notes?: string;
  totalAmount?: number;
  createdAt?: string;
  updatedAt?: string;
  serviceDuration?: number;}

export interface BookingCreate {
  customerId: string;
  staffId: string;
  serviceId: string;
  date: string;
  startTime: string;
  notes?: string;
}

export interface BookingUpdate extends Partial<BookingCreate> {
  status?: BookingStatus;
}

// Customer Types
export interface Customer {
  id: string;
  name: string;
  email?: string;
  phone: string;
  notes?: string;
  totalVisits?: number;
  totalSpent?: number;
  lastVisit?: string;
  createdAt?: string;
  updatedAt?: string;

  loyaltyPoints?: number;
  avgSpend?: number;
  membershipTier?: 'none' | 'bronze' | 'silver' | 'gold' | 'platinum';
  birthday?: string;
  anniversary?: string;
  gender?: 'male' | 'female' | 'other' | 'prefer_not_to_say';
  address?: string;
  birthdayMonth?: number;
}

export interface CustomerCreate {
  name: string;
  email?: string;
  phone: string;
  notes?: string;
}

export interface CustomerUpdate extends Partial<CustomerCreate> {}

export interface CreateCustomerData {
  firstName: string;
  lastName: string;
  name: string;
  phone: string;
  email?: string;
  address?: string;
  birthday?: string;
  anniversary?: string;
  gender?: 'male' | 'female' | 'other' | 'prefer_not_to_say';
  notes?: string;
  membershipTier?: 'none' | 'bronze' | 'silver' | 'gold' | 'platinum';
}

// Salon/Tenant Types
export interface SalonHours {
  open: string;
  close: string;
}

export interface WorkingHours {
  monday: SalonHours | null;
  tuesday: SalonHours | null;
  wednesday: SalonHours | null;
  thursday: SalonHours | null;
  friday: SalonHours | null;
  saturday: SalonHours | null;
  sunday: SalonHours | null;
}

export interface NotificationChannelSettings {
  enabled: boolean;
  new_booking?: boolean;
  cancellation?: boolean;
  reminder?: boolean;
  marketing?: boolean;
  daily_summary?: boolean;
  weekly_report?: boolean;
  monthly_report?: boolean;
}

export interface QuietHours {
  enabled: boolean;
  start_time: string;
  end_time: string;
}

export interface NotificationSettings {
  email_notifications: NotificationChannelSettings;
  sms_notifications: NotificationChannelSettings;
  whatsapp_notifications: NotificationChannelSettings;
  push_notifications: NotificationChannelSettings;
  quiet_hours: QuietHours;
}

export interface Salon {
  id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  pincode: string;
  phone: string;
  email: string;
  gstNumber?: string;
  workingHours?: WorkingHours;
  notificationSettings?: NotificationSettings;
  logo?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface SalonUpdate extends Partial<Omit<Salon, 'id' | 'createdAt' | 'updatedAt'>> {}

// Payment Types
export type PaymentStatus = 'pending' | 'completed' | 'failed' | 'refunded';
export type PaymentMethod = 'cash' | 'card' | 'upi' | 'wallet';

export interface Payment {
  id: string;
  bookingId: string;
  customerId: string;
  amount: number;
  method: PaymentMethod;
  status: PaymentStatus;
  gstAmount?: number;
  createdAt?: string;
}

// Analytics Types
export interface RevenueAnalytics {
  total: number;
  byService: { service: string; amount: number }[];
  byStaff: { staff: string; amount: number }[];
  byDate: { date: string; amount: number }[];
}

export interface BookingAnalytics {
  total: number;
  byStatus: { status: string; count: number }[];
  byService: { service: string; count: number }[];
  byStaff: { staff: string; count: number }[];
  byDate: { date: string; count: number }[];
}

// Auth Types
export interface User {
  uid: string;
  email: string;
  displayName?: string;
  photoURL?: string;
  role?: StaffRole;
  salonId?: string;
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error?: string | null;
}

// Form Data Types (inferred from schemas)
export type LoginFormData = {
  email: string;
  password: string;
};

export type RegisterFormData = {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phone: string;
  salonName: string;
  confirmPassword: string;
  acceptTerms: boolean;
};

export type ForgotPasswordFormData = {
  email: string;
};

export type TimeSlot = {
  time: string;
  available: boolean;
};

export type BookingFormData = {
  customerId: string;
  serviceId: string;
  staffId?: string;
  date: string;
  startTime: string;
  notes?: string;
  services?: Array<{
    serviceId: string;
    staffId: string;
    duration: number;
    price: number;
    gstRate?: number;
  }>;
};

export type CreateBookingData = {
  customerId: string;
  services: Array<{
    serviceId: string;
    staffId?: string;
  }>;
  date: string;
  startTime: string;
  notes?: string;
};
