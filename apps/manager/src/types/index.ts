// Manager-specific types
export interface ManagerUser {
  id: string;
  email: string;
  displayName: string;
  role: 'manager';
  salonId: string;
  salonName: string;
  photoURL?: string;
}

export interface DashboardStats {
  todayBookings: number;
  pendingConfirmations: number;
  todayRevenue: number;
  activeStaff: number;
  completedToday: number;
  cancelledToday: number;
}

export interface StaffAttendance {
  staffId: string;
  staffName: string;
  role: string;
  checkInTime?: string;
  checkOutTime?: string;
  status: 'present' | 'absent' | 'late' | 'on_leave';
  photoURL?: string;
}

export interface Alert {
  id: string;
  type: 'booking' | 'staff' | 'customer' | 'system';
  message: string;
  timestamp: string;
  read: boolean;
  priority: 'low' | 'medium' | 'high';
}

export interface TimeSlot {
  time: string;
  available: boolean;
  staffId?: string;
}

export interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  status: string;
  staffId: string;
  staffName: string;
  customerId: string;
  customerName: string;
  serviceName: string;
  color?: string;
}

export interface ReportData {
  date: string;
  totalBookings: number;
  completedBookings: number;
  cancelledBookings: number;
  totalRevenue: number;
  topServices: { name: string; count: number; revenue: number }[];
  topStaff: { name: string; bookings: number; revenue: number }[];
}

// Billing types
export * from './billing';
