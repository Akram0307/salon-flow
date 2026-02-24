import { format, formatDistanceToNow, parseISO, isValid, differenceInMinutes, addMinutes, startOfDay, endOfDay, isToday, isTomorrow, isThisWeek, isThisMonth } from 'date-fns';
import { enIN } from 'date-fns/locale';

// ============== Currency Formatting ==============

/**
 * Format amount as Indian Rupees
 */
export const formatCurrency = (amount: number, options?: {
  showSymbol?: boolean;
  compact?: boolean;
}): string => {
  const { showSymbol = true, compact = false } = options || {};
  
  if (compact && amount >= 100000) {
    // Format in lakhs
    const lakhs = amount / 100000;
    return showSymbol ? `₹${lakhs.toFixed(1)}L` : `${lakhs.toFixed(1)}L`;
  }
  
  return new Intl.NumberFormat('en-IN', {
    style: showSymbol ? 'currency' : 'decimal',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount);
};

/**
 * Format amount with GST breakdown
 */
export const formatWithGst = (baseAmount: number, gstRate: number = 5): {
  base: string;
  gst: string;
  total: string;
} => {
  const gst = (baseAmount * gstRate) / 100;
  const total = baseAmount + gst;
  
  return {
    base: formatCurrency(baseAmount),
    gst: formatCurrency(gst),
    total: formatCurrency(total),
  };
};

/**
 * Parse currency string to number
 */
export const parseCurrency = (value: string): number => {
  const cleaned = value.replace(/[^\d.-]/g, '');
  return parseFloat(cleaned) || 0;
};

// ============== Date & Time Formatting ==============

/**
 * Format date to Indian locale
 */
export const formatDate = (date: string | Date, formatStr: string = 'dd MMM yyyy'): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  if (!isValid(dateObj)) return 'Invalid Date';
  return format(dateObj, formatStr, { locale: enIN });
};

/**
 * Format time (24h to 12h)
 */
export const formatTime = (time: string): string => {
  const [hours, minutes] = time.split(':').map(Number);
  const period = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;
  return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
};

/**
 * Format time for display (24h format)
 */
export const formatTime24 = (time: string): string => {
  const [hours, minutes] = time.split(':');
  return `${hours}:${minutes}`;
};

/**
 * Format date and time together
 */
export const formatDateTime = (date: string | Date, time?: string): string => {
  const dateStr = formatDate(date);
  return time ? `${dateStr}, ${formatTime(time)}` : dateStr;
};

/**
 * Format relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  if (!isValid(dateObj)) return 'Invalid Date';
  return formatDistanceToNow(dateObj, { addSuffix: true, locale: enIN });
};

/**
 * Format duration in minutes to readable string
 */
export const formatDuration = (minutes: number): string => {
  if (minutes < 60) {
    return `${minutes} min`;
  }
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
};

/**
 * Format date with smart labels (Today, Tomorrow, etc.)
 */
export const formatSmartDate = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  if (!isValid(dateObj)) return 'Invalid Date';
  
  if (isToday(dateObj)) return 'Today';
  if (isTomorrow(dateObj)) return 'Tomorrow';
  if (isThisWeek(dateObj)) return format(dateObj, 'EEEE', { locale: enIN });
  if (isThisMonth(dateObj)) return format(dateObj, 'dd MMM', { locale: enIN });
  
  return formatDate(dateObj);
};

/**
 * Format date range
 */
export const formatDateRange = (startDate: string | Date, endDate: string | Date): string => {
  const start = typeof startDate === 'string' ? parseISO(startDate) : startDate;
  const end = typeof endDate === 'string' ? parseISO(endDate) : endDate;
  
  if (!isValid(start) || !isValid(end)) return 'Invalid Date Range';
  
  return `${formatDate(start)} - ${formatDate(end)}`;
};

/**
 * Format time slot for display
 */
export const formatTimeSlot = (startTime: string, endTime: string): string => {
  return `${formatTime(startTime)} - ${formatTime(endTime)}`;
};

/**
 * Calculate end time from start time and duration
 */
export const calculateEndTime = (startTime: string, durationMinutes: number): string => {
  const [hours, minutes] = startTime.split(':').map(Number);
  const startDate = new Date();
  startDate.setHours(hours, minutes, 0, 0);
  
  const endDate = addMinutes(startDate, durationMinutes);
  
  return `${endDate.getHours().toString().padStart(2, '0')}:${endDate.getMinutes().toString().padStart(2, '0')}`;
};

/**
 * Get day of week from date
 */
export const getDayOfWeek = (date: string | Date): number => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return dateObj.getDay();
};

/**
 * Format day name
 */
export const formatDayName = (dayOfWeek: number, short: boolean = false): string => {
  const days = short 
    ? ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    : ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  return days[dayOfWeek] || '';
};

// ============== Phone Formatting ==============

/**
 * Format Indian phone number
 */
export const formatPhone = (phone: string): string => {
  // Remove all non-digits
  const cleaned = phone.replace(/\D/g, '');
  
  // Handle different formats
  if (cleaned.length === 10) {
    // 9876543210 -> 98765 43210
    return `${cleaned.slice(0, 5)} ${cleaned.slice(5)}`;
  }
  
  if (cleaned.length === 12 && cleaned.startsWith('91')) {
    // 919876543210 -> +91 98765 43210
    return `+91 ${cleaned.slice(2, 7)} ${cleaned.slice(7)}`;
  }
  
  if (cleaned.length === 13 && cleaned.startsWith('910')) {
    // 9109876543210 -> +91 09876 543210 (with leading zero)
    return `+91 ${cleaned.slice(3, 8)} ${cleaned.slice(8)}`;
  }
  
  // Return as-is if format not recognized
  return phone;
};

/**
 * Format phone for display (with country code)
 */
export const formatPhoneDisplay = (phone: string): string => {
  const cleaned = phone.replace(/\D/g, '');
  
  if (cleaned.length === 10) {
    return `+91 ${cleaned.slice(0, 5)} ${cleaned.slice(5)}`;
  }
  
  return formatPhone(phone);
};

/**
 * Format phone for tel: link
 */
export const formatPhoneLink = (phone: string): string => {
  const cleaned = phone.replace(/\D/g, '');
  
  if (cleaned.length === 10) {
    return `tel:+91${cleaned}`;
  }
  
  if (cleaned.length === 12 && cleaned.startsWith('91')) {
    return `tel:+${cleaned}`;
  }
  
  return `tel:${phone}`;
};

// ============== Name Formatting ==============

/**
 * Format full name
 */
export const formatName = (firstName: string, lastName?: string): string => {
  return lastName ? `${firstName} ${lastName}` : firstName;
};

/**
 * Get initials from name
 */
export const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
};

/**
 * Format name with title
 */
export const formatNameWithTitle = (firstName: string, lastName?: string, title?: string): string => {
  const fullName = formatName(firstName, lastName);
  return title ? `${title} ${fullName}` : fullName;
};

// ============== Number Formatting ==============

/**
 * Format number with Indian locale
 */
export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('en-IN').format(num);
};

/**
 * Format percentage
 */
export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${value.toFixed(decimals)}%`;
};

/**
 * Format compact number (1K, 1L, etc.)
 */
export const formatCompactNumber = (num: number): string => {
  if (num >= 10000000) {
    return `${(num / 10000000).toFixed(1)}Cr`;
  }
  if (num >= 100000) {
    return `${(num / 100000).toFixed(1)}L`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
};

// ============== Loyalty Points Formatting ==============

/**
 * Format loyalty points
 */
export const formatLoyaltyPoints = (points: number): string => {
  return `${formatNumber(points)} pts`;
};

/**
 * Calculate loyalty points from amount
 */
export const calculateLoyaltyPoints = (amount: number, rate: number = 1): number => {
  // 1 point per ₹10 spent (default rate)
  return Math.floor(amount / 10) * rate;
};

/**
 * Calculate loyalty value in rupees
 */
export const calculateLoyaltyValue = (points: number, rate: number = 1): number => {
  // Each point is worth ₹rate
  return points * rate;
};

// ============== GST Formatting ==============

/**
 * Format GST number
 */
export const formatGstNumber = (gst: string): string => {
  const cleaned = gst.replace(/[^A-Z0-9]/gi, '').toUpperCase();
  if (cleaned.length === 15) {
    // Format: 22AAAAA0000A1Z5
    return `${cleaned.slice(0, 2)}${cleaned.slice(2, 7)}${cleaned.slice(7, 11)}${cleaned.slice(11, 13)}${cleaned.slice(13)}`;
  }
  return gst;
};

/**
 * Calculate GST amount
 */
export const calculateGst = (amount: number, rate: number = 5): number => {
  return (amount * rate) / 100;
};

// ============== Address Formatting ==============

/**
 * Format address
 */
export const formatAddress = (parts: {
  address?: string;
  city?: string;
  state?: string;
  pincode?: string;
}): string => {
  const { address, city, state, pincode } = parts;
  const lines: string[] = [];
  
  if (address) lines.push(address);
  if (city) lines.push(city);
  if (state || pincode) {
    lines.push(`${state || ''} ${pincode || ''}`.trim());
  }
  
  return lines.join(', ');
};

export default {
  formatCurrency,
  formatWithGst,
  parseCurrency,
  formatDate,
  formatTime,
  formatTime24,
  formatDateTime,
  formatRelativeTime,
  formatDuration,
  formatSmartDate,
  formatDateRange,
  formatTimeSlot,
  calculateEndTime,
  getDayOfWeek,
  formatDayName,
  formatPhone,
  formatPhoneDisplay,
  formatPhoneLink,
  formatName,
  getInitials,
  formatNameWithTitle,
  formatNumber,
  formatPercentage,
  formatCompactNumber,
  formatLoyaltyPoints,
  calculateLoyaltyPoints,
  calculateLoyaltyValue,
  formatGstNumber,
  calculateGst,
  formatAddress,
};
