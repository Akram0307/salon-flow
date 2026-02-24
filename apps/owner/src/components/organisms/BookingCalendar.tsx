/**
 * BookingCalendar Component
 *
 * Calendar grid with bookings for the Owner PWA.
 * Displays appointments in a weekly or daily view with time slots.
 *
 * @example
 * <BookingCalendar
 *   bookings={bookings}
 *   viewMode="week"
 *   onSlotClick={handleSlotClick}
 *   onBookingClick={handleBookingClick}
 * />
 */

import React, { useState, useMemo } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  Clock,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ============================================
// Types
// ============================================

export type ViewMode = 'day' | 'week';

export type BookingStatus = 'confirmed' | 'pending' | 'in-progress' | 'completed' | 'cancelled' | 'no-show';

export interface CalendarBooking {
  id: string;
  customerName: string;
  serviceName: string;
  staffName: string;
  staffId: string;
  startTime: Date;
  endTime: Date;
  status: BookingStatus;
  color?: string;
}

export interface TimeSlot {
  time: Date;
  bookings: CalendarBooking[];
}

export interface BookingCalendarProps {
  bookings: CalendarBooking[];
  viewMode?: ViewMode;
  selectedDate?: Date;
  onDateChange?: (date: Date) => void;
  onViewModeChange?: (mode: ViewMode) => void;
  onSlotClick?: (date: Date, hour: number) => void;
  onBookingClick?: (booking: CalendarBooking) => void;
  staffFilter?: string[];
  workingHours?: { start: number; end: number };
  className?: string;
}

// ============================================
// Constants
// ============================================

const HOURS = Array.from({ length: 24 }, (_, i) => i);
const DEFAULT_WORKING_HOURS = { start: 9, end: 21 };

const STATUS_COLORS: Record<BookingStatus, string> = {
  confirmed: 'bg-primary-100 dark:bg-primary-900/30 border-l-primary-500',
  pending: 'bg-warning-50 dark:bg-warning-900/20 border-l-warning-500',
  'in-progress': 'bg-accent-50 dark:bg-accent-900/20 border-l-accent-500',
  completed: 'bg-success-50 dark:bg-success-900/20 border-l-success-500',
  cancelled: 'bg-surface-100 dark:bg-surface-800 border-l-surface-400 line-through opacity-60',
  'no-show': 'bg-error-50 dark:bg-error-900/20 border-l-error-500 opacity-60',
};

// ============================================
// Helper Functions
// ============================================

const formatDate = (date: Date): string => {
  return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
};

const formatTime = (hour: number): string => {
  const period = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour % 12 || 12;
  return `${displayHour} ${period}`;
};

const getWeekDays = (date: Date): Date[] => {
  const days: Date[] = [];
  const startOfWeek = new Date(date);
  startOfWeek.setDate(date.getDate() - date.getDay());
  
  for (let i = 0; i < 7; i++) {
    const day = new Date(startOfWeek);
    day.setDate(startOfWeek.getDate() + i);
    days.push(day);
  }
  
  return days;
};

const isSameDay = (date1: Date, date2: Date): boolean => {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
};

const isToday = (date: Date): boolean => {
  return isSameDay(date, new Date());
};

// ============================================
// Booking Card Component
// ============================================

interface BookingItemProps {
  booking: CalendarBooking;
  onClick?: (booking: CalendarBooking) => void;
  compact?: boolean;
}

const BookingItem: React.FC<BookingItemProps> = ({ booking, onClick, compact = false }) => {
  const duration = Math.round((booking.endTime.getTime() - booking.startTime.getTime()) / (1000 * 60));
  
  return (
    <button
      onClick={() => onClick?.(booking)}
      className={cn(
        'w-full text-left rounded-lg border-l-4 p-2 transition-all',
        'hover:shadow-md hover:scale-[1.02]',
        STATUS_COLORS[booking.status],
        compact ? 'text-xs' : 'text-sm'
      )}
    >
      <div className="font-medium text-surface-900 dark:text-white truncate">
        {booking.customerName}
      </div>
      {!compact && (
        <>
          <div className="text-xs text-surface-600 dark:text-surface-400 truncate">
            {booking.serviceName}
          </div>
          <div className="flex items-center gap-2 mt-1 text-xs text-surface-500 dark:text-surface-400">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {booking.startTime.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
            </span>
            <span>{duration} min</span>
          </div>
        </>
      )}
    </button>
  );
};

// ============================================
// Time Slot Component
// ============================================

interface TimeSlotRowProps {
  hour: number;
  bookings: CalendarBooking[];
  onBookingClick?: (booking: CalendarBooking) => void;
  onSlotClick?: () => void;
}

const TimeSlotRow: React.FC<TimeSlotRowProps> = ({
  hour,
  bookings,
  onBookingClick,
  onSlotClick,
}) => {
  return (
    <div className="flex border-b border-surface-100 dark:border-surface-800 min-h-[60px]">
      {/* Time Label */}
      <div className="w-16 flex-shrink-0 p-2 text-xs text-surface-500 dark:text-surface-400 text-right border-r border-surface-100 dark:border-surface-800">
        {formatTime(hour)}
      </div>
      
      {/* Slot Content */}
      <div
        className="flex-1 p-1 cursor-pointer hover:bg-surface-50 dark:hover:bg-surface-800/50 transition-colors"
        onClick={onSlotClick}
      >
        {bookings.length > 0 ? (
          <div className="space-y-1">
            {bookings.map((booking) => (
              <BookingItem
                key={booking.id}
                booking={booking}
                onClick={onBookingClick}
              />
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
};

// ============================================
// Main BookingCalendar Component
// ============================================

export const BookingCalendar: React.FC<BookingCalendarProps> = ({
  bookings,
  viewMode = 'week',
  selectedDate = new Date(),
  onDateChange,
  onViewModeChange,
  onSlotClick,
  onBookingClick,
  staffFilter,
  workingHours = DEFAULT_WORKING_HOURS,
  className,
}) => {
  const [currentDate, setCurrentDate] = useState(selectedDate);
  const [internalViewMode, setInternalViewMode] = useState<ViewMode>(viewMode);

  const weekDays = useMemo(() => getWeekDays(currentDate), [currentDate]);

  const filteredBookings = useMemo(() => {
    let filtered = bookings;
    if (staffFilter && staffFilter.length > 0) {
      filtered = filtered.filter(b => staffFilter.includes(b.staffId));
    }
    return filtered;
  }, [bookings, staffFilter]);

  const getBookingsForSlot = (date: Date, hour: number): CalendarBooking[] => {
    return filteredBookings.filter((booking) => {
      const bookingHour = booking.startTime.getHours();
      return isSameDay(booking.startTime, date) && bookingHour === hour;
    });
  };

  const navigateDate = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    if (internalViewMode === 'week') {
      newDate.setDate(currentDate.getDate() + (direction === 'next' ? 7 : -7));
    } else {
      newDate.setDate(currentDate.getDate() + (direction === 'next' ? 1 : -1));
    }
    setCurrentDate(newDate);
    onDateChange?.(newDate);
  };

  const goToToday = () => {
    setCurrentDate(new Date());
    onDateChange?.(new Date());
  };

  const handleViewModeChange = (mode: ViewMode) => {
    setInternalViewMode(mode);
    onViewModeChange?.(mode);
  };

  const hours = HOURS.slice(workingHours.start, workingHours.end + 1);

  return (
    <div className={cn('bg-white dark:bg-surface-900 rounded-xl overflow-hidden', className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-surface-200 dark:border-surface-700">
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigateDate('prev')}
            className="p-2 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
            aria-label="Previous"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <button
            onClick={() => navigateDate('next')}
            className="p-2 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
            aria-label="Next"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
          <button
            onClick={goToToday}
            className="px-3 py-1.5 text-sm font-medium rounded-lg bg-surface-100 dark:bg-surface-800 hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors"
          >
            Today
          </button>
        </div>

        <h2 className="text-lg font-semibold text-surface-900 dark:text-white">
          {internalViewMode === 'week'
            ? `${formatDate(weekDays[0])} - ${formatDate(weekDays[6])}`
            : formatDate(currentDate)}
        </h2>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-1 p-1 bg-surface-100 dark:bg-surface-800 rounded-lg">
          <button
            onClick={() => handleViewModeChange('day')}
            className={cn(
              'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
              internalViewMode === 'day'
                ? 'bg-white dark:bg-surface-700 text-primary-600 dark:text-primary-400 shadow-sm'
                : 'text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-white'
            )}
          >
            Day
          </button>
          <button
            onClick={() => handleViewModeChange('week')}
            className={cn(
              'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
              internalViewMode === 'week'
                ? 'bg-white dark:bg-surface-700 text-primary-600 dark:text-primary-400 shadow-sm'
                : 'text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-white'
            )}
          >
            Week
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="overflow-x-auto">
        {internalViewMode === 'week' ? (
          /* Week View */
          <div className="min-w-[800px]">
            {/* Day Headers */}
            <div className="flex border-b border-surface-200 dark:border-surface-700">
              <div className="w-16 flex-shrink-0" />
              {weekDays.map((day, index) => (
                <div
                  key={index}
                  className={cn(
                    'flex-1 p-3 text-center border-r border-surface-100 dark:border-surface-800 last:border-r-0',
                    isToday(day) && 'bg-primary-50 dark:bg-primary-900/20'
                  )}
                >
                  <div className="text-xs text-surface-500 dark:text-surface-400">
                    {day.toLocaleDateString('en-US', { weekday: 'short' })}
                  </div>
                  <div
                    className={cn(
                      'text-lg font-semibold',
                      isToday(day)
                        ? 'text-primary-600 dark:text-primary-400'
                        : 'text-surface-900 dark:text-white'
                    )}
                  >
                    {day.getDate()}
                  </div>
                </div>
              ))}
            </div>

            {/* Time Slots */}
            <div className="max-h-[500px] overflow-y-auto">
              {hours.map((hour) => (
                <div key={hour} className="flex border-b border-surface-100 dark:border-surface-800">
                  <div className="w-16 flex-shrink-0 p-2 text-xs text-surface-500 dark:text-surface-400 text-right border-r border-surface-100 dark:border-surface-800">
                    {formatTime(hour)}
                  </div>
                  {weekDays.map((day, dayIndex) => (
                    <div
                      key={dayIndex}
                      className={cn(
                        'flex-1 p-1 min-h-[50px] border-r border-surface-100 dark:border-surface-800 last:border-r-0 cursor-pointer',
                        'hover:bg-surface-50 dark:hover:bg-surface-800/50 transition-colors',
                        isToday(day) && 'bg-primary-50/30 dark:bg-primary-900/10'
                      )}
                      onClick={() => onSlotClick?.(day, hour)}
                    >
                      {getBookingsForSlot(day, hour).map((booking) => (
                        <BookingItem
                          key={booking.id}
                          booking={booking}
                          compact
                          onClick={onBookingClick}
                        />
                      ))}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        ) : (
          /* Day View */
          <div>
            {/* Day Header */}
            <div className="p-4 border-b border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800/50">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-surface-500 dark:text-surface-400">
                    {currentDate.toLocaleDateString('en-US', { weekday: 'long' })}
                  </div>
                  <div className="text-2xl font-bold text-surface-900 dark:text-white">
                    {currentDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-surface-500 dark:text-surface-400">
                    {filteredBookings.filter(b => isSameDay(b.startTime, currentDate)).length} bookings
                  </div>
                </div>
              </div>
            </div>

            {/* Time Slots */}
            <div className="max-h-[500px] overflow-y-auto">
              {hours.map((hour) => (
                <TimeSlotRow
                  key={hour}
                  hour={hour}
                  bookings={getBookingsForSlot(currentDate, hour)}
                  onBookingClick={onBookingClick}
                  onSlotClick={() => onSlotClick?.(currentDate, hour)}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 p-3 border-t border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800/50 overflow-x-auto">
        <span className="text-xs text-surface-500 dark:text-surface-400">Status:</span>
        {(['confirmed', 'pending', 'in-progress', 'completed'] as BookingStatus[]).map((status) => (
          <div key={status} className="flex items-center gap-1.5">
            <div className={cn('w-3 h-3 rounded', STATUS_COLORS[status].split(' ')[0])} />
            <span className="text-xs text-surface-600 dark:text-surface-400 capitalize">
              {status.replace('-', ' ')}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BookingCalendar;
