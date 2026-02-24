/**
 * Salon Flow Owner PWA - BookingCard Molecule
 * Appointment card with customer info, service, time, status, staff
 * Based on mockup 07
 */

import React from 'react';
import { Clock } from 'lucide-react';
import { cn, formatTime } from '@/lib/utils';
import { Avatar, Badge, Card } from '@/components/atoms';

// ============================================
// Types
// ============================================
export type BookingStatus = 'confirmed' | 'pending' | 'cancelled' | 'completed';

export interface Booking {
  id: string;
  customer: {
    id: string;
    name: string;
    avatar?: string;
    phone?: string;
  };
  service: {
    id: string;
    name: string;
    duration: number; // in minutes
    price?: number;
  };
  time: Date | string;
  duration: number; // in minutes
  status: BookingStatus;
  staff: {
    id: string;
    name: string;
    avatar?: string;
  };
  notes?: string;
}

export interface BookingCardProps {
  booking: Booking;
  onPress?: (booking: Booking) => void;
  onReschedule?: (booking: Booking) => void;
  onCancel?: (booking: Booking) => void;
  className?: string;
  compact?: boolean;
}

// ============================================
// BookingCard Component
// ============================================
export const BookingCard: React.FC<BookingCardProps> = ({
  booking,
  onPress,
  onReschedule,
  onCancel,
  className,
  compact = false,
}) => {
  const statusConfig: Record<BookingStatus, { status: string; variant: 'solid' | 'subtle' }> = {
    confirmed: { status: 'success', variant: 'subtle' },
    pending: { status: 'warning', variant: 'subtle' },
    cancelled: { status: 'error', variant: 'subtle' },
    completed: { status: 'gray', variant: 'subtle' },
  };

  const formattedTime = typeof booking.time === 'string'
    ? formatTime(new Date(booking.time))
    : formatTime(booking.time);

  const formatDuration = (mins: number) => {
    if (mins < 60) return `${mins}m`;
    const hours = Math.floor(mins / 60);
    const remaining = mins % 60;
    return remaining > 0 ? `${hours}h ${remaining}m` : `${hours}h`;
  };

  return (
    <Card
      hoverable={!!onPress}
      clickable={!!onPress}
      onClick={() => onPress?.(booking)}
      className={cn(
        'relative',
        booking.status === 'cancelled' && 'opacity-75',
        className
      )}
    >
      {/* Status Badge - Absolute Top Right */}
      <div className="absolute top-4 right-4">
        <Badge
          status={statusConfig[booking.status].status as any}
          variant={statusConfig[booking.status].variant}
          size="sm"
        >
          {booking.status}
        </Badge>
      </div>

      {/* Main Content */}
      <div className={cn('flex gap-4', compact ? 'items-center' : '')}>
        {/* Customer Avatar */}
        <Avatar
          src={booking.customer.avatar}
          fallback={booking.customer.name}
          alt={booking.customer.name}
          size={compact ? 'md' : 'lg'}
        />

        {/* Booking Details */}
        <div className="flex-1 min-w-0">
          {/* Customer Name */}
          <h3 className="font-semibold text-surface-900 dark:text-white truncate">
            {booking.customer.name}
          </h3>

          {/* Service Name */}
          <p className="text-sm text-surface-600 dark:text-surface-400 truncate">
            {booking.service.name}
          </p>

          {/* Time & Duration */}
          <div className="flex items-center gap-3 mt-2 text-xs text-surface-500 dark:text-surface-500">
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {formattedTime}
            </span>
            <span>{formatDuration(booking.duration)}</span>
            {booking.service.price && (
              <span>₹{booking.service.price}</span>
            )}
          </div>

          {/* Staff Info (Non-compact only) */}
          {!compact && (
            <div className="flex items-center gap-2 mt-3 pt-3 border-t border-surface-100 dark:border-surface-700">
              <Avatar
                src={booking.staff.avatar}
                fallback={booking.staff.name}
                alt={booking.staff.name}
                size="sm"
              />
              <span className="text-sm text-surface-600 dark:text-surface-400">
                {booking.staff.name}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons (if provided) */}
      {(onReschedule || onCancel) && (
        <div className="flex gap-2 mt-4 pt-4 border-t border-surface-100 dark:border-surface-700">
          {onReschedule && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onReschedule(booking);
              }}
              className="flex-1 px-3 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20 rounded-lg hover:bg-primary-100 dark:hover:bg-primary-900/30 transition-colors"
            >
              Reschedule
            </button>
          )}
          {onCancel && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onCancel(booking);
              }}
              className="flex-1 px-3 py-2 text-sm font-medium text-error-600 dark:text-error-400 bg-error-50 dark:bg-error-900/20 rounded-lg hover:bg-error-100 dark:hover:bg-error-900/30 transition-colors"
            >
              Cancel
            </button>
          )}
        </div>
      )}
    </Card>
  );
};

export default BookingCard;
