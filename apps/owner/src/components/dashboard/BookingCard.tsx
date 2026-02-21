/**
 * Salon Flow Owner Dashboard - BookingCard Component
 * Professional booking card with status and actions
 */

import React, { forwardRef } from 'react';
import { cn } from '../../lib/utils';
import { Avatar } from '../ui/Avatar';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import type { BaseComponentProps, BookingStatus } from '../../types/design-system';

// ============================================
// BookingCard Types
// ============================================
export interface BookingCardProps extends BaseComponentProps {
  id: string;
  customer: {
    name: string;
    avatar?: string;
    phone?: string;
  };
  service: {
    name: string;
    duration: number;
    price: number;
  };
  staff?: {
    name: string;
    avatar?: string;
  };
  time: string;
  date: string;
  status: BookingStatus;
  notes?: string;
  onConfirm?: () => void;
  onCancel?: () => void;
  onReschedule?: () => void;
  onViewDetails?: () => void;
  onStart?: () => void;
  onComplete?: () => void;
  compact?: boolean;
}

// ============================================
// Status Styles
// ============================================
const statusConfig: Record<BookingStatus, { label: string; variant: 'default' | 'success' | 'warning' | 'error' | 'info' | 'secondary' }> = {
  pending: { label: 'Pending', variant: 'warning' },
  confirmed: { label: 'Confirmed', variant: 'success' },
  cancelled: { label: 'Cancelled', variant: 'error' },
  completed: { label: 'Completed', variant: 'secondary' },
  'no-show': { label: 'No Show', variant: 'error' },
  'in-progress': { label: 'In Progress', variant: 'info' },
};

// ============================================
// BookingCard Component
// ============================================
export const BookingCard = forwardRef<HTMLDivElement, BookingCardProps>(
  (
    {
      id,
      customer,
      service,
      staff,
      time,
      date,
      status,
      notes,
      onConfirm,
      onCancel,
      onReschedule,
      onViewDetails,
      onStart,
      onComplete,
      compact = false,
      className,
    },
    ref
  ) => {
    const statusInfo = statusConfig[status];

    const formatDuration = (minutes: number) => {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      if (hours > 0 && mins > 0) return `${hours}h ${mins}m`;
      if (hours > 0) return `${hours}h`;
      return `${mins}m`;
    };

    const formatPrice = (price: number) => {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
      }).format(price);
    };

    return (
      <div
        ref={ref}
        className={cn(
          'bg-white dark:bg-surface-800 rounded-xl border border-surface-200 dark:border-surface-700',
          'transition-all duration-200 hover:shadow-md',
          compact ? 'p-3' : 'p-4',
          className
        )}
      >
        <div className={cn('flex gap-3', compact ? 'items-center' : 'items-start')}>
          {/* Time Column */}
          <div className={cn('text-center', compact ? 'min-w-[50px]' : 'min-w-[60px]')}>
            <p className="text-lg font-semibold text-surface-900 dark:text-white">{time}</p>
            <p className="text-xs text-surface-500 dark:text-surface-400">{date}</p>
          </div>

          {/* Divider */}
          <div className="w-px bg-surface-200 dark:bg-surface-700" />

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                {/* Customer */}
                <div className="flex items-center gap-2">
                  <Avatar name={customer.name} src={customer.avatar} size="xs" />
                  <span className="font-medium text-surface-900 dark:text-white truncate">
                    {customer.name}
                  </span>
                </div>

                {/* Service */}
                <p className="mt-1 text-sm text-surface-600 dark:text-surface-400 truncate">
                  {service.name} • {formatDuration(service.duration)} • {formatPrice(service.price)}
                </p>

                {/* Staff */}
                {staff && !compact && (
                  <p className="mt-1 text-xs text-surface-500 dark:text-surface-400">
                    with {staff.name}
                  </p>
                )}
              </div>

              {/* Status */}
              <Badge variant={statusInfo.variant} size="sm">
                {statusInfo.label}
              </Badge>
            </div>

            {/* Notes */}
            {notes && !compact && (
              <p className="mt-2 text-xs text-surface-500 dark:text-surface-400 italic">
                {notes}
              </p>
            )}

            {/* Actions */}
            {!compact && (
              <div className="mt-3 flex items-center gap-2">
                {status === 'pending' && (
                  <>
                    <Button size="sm" onClick={onConfirm}>
                      Confirm
                    </Button>
                    <Button size="sm" variant="outline" onClick={onReschedule}>
                      Reschedule
                    </Button>
                    <Button size="sm" variant="ghost" onClick={onCancel}>
                      Cancel
                    </Button>
                  </>
                )}
                {status === 'confirmed' && (
                  <>
                    <Button size="sm" onClick={onStart}>
                      Start Service
                    </Button>
                    <Button size="sm" variant="outline" onClick={onReschedule}>
                      Reschedule
                    </Button>
                  </>
                )}
                {status === 'in-progress' && (
                  <Button size="sm" onClick={onComplete}>
                    Complete
                  </Button>
                )}
                <Button size="sm" variant="ghost" onClick={onViewDetails}>
                  View Details
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }
);

BookingCard.displayName = 'BookingCard';

// ============================================
// BookingList Component
// ============================================
export interface BookingListProps extends BaseComponentProps {
  bookings: BookingCardProps[];
  emptyMessage?: string;
  onBookingClick?: (id: string) => void;
}

export const BookingList: React.FC<BookingListProps> = ({
  bookings,
  emptyMessage = 'No bookings found',
  onBookingClick,
  className,
}) => {
  if (bookings.length === 0) {
    return (
      <div className={cn('text-center py-8', className)}>
        <svg
          className="mx-auto w-12 h-12 text-surface-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className={cn('space-y-3', className)}>
      {bookings.map((booking) => (
        <BookingCard
          key={booking.id}
          {...booking}
          onViewDetails={() => onBookingClick?.(booking.id)}
        />
      ))}
    </div>
  );
};

export default BookingCard;
