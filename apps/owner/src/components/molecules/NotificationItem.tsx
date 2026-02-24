/**
 * Salon Flow Owner PWA - NotificationItem Molecule
 * Notification list item with icon by type, title, message, timestamp, unread indicator
 */

import React from 'react';
import { 
  Bell, 
  Calendar, 
  User, 
  Wallet, 
  AlertTriangle, 
  CheckCircle, 
  Info,
  X,
  ChevronRight
} from 'lucide-react';
import { cn, formatDate } from '@/lib/utils';

// ============================================
// Types
// ============================================
export type NotificationType = 
  | 'booking' 
  | 'customer' 
  | 'payment' 
  | 'staff' 
  | 'alert' 
  | 'system' 
  | 'success' 
  | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: Date | string;
  read: boolean;
  actionable?: boolean;
  actionLabel?: string;
  imageUrl?: string;
}

export interface NotificationItemProps {
  notification: Notification;
  onPress?: (notification: Notification) => void;
  onDismiss?: (notification: Notification) => void;
  className?: string;
}

// ============================================
// NotificationItem Component
// ============================================
export const NotificationItem: React.FC<NotificationItemProps> = ({
  notification,
  onPress,
  onDismiss,
  className,
}) => {
  const typeConfig: Record<NotificationType, { 
    icon: React.ElementType; 
    bg: string;
    iconColor: string;
  }> = {
    booking: {
      icon: Calendar,
      bg: 'bg-primary-100 dark:bg-primary-900/30',
      iconColor: 'text-primary-600 dark:text-primary-400',
    },
    customer: {
      icon: User,
      bg: 'bg-secondary-100 dark:bg-secondary-900/30',
      iconColor: 'text-secondary-600 dark:text-secondary-400',
    },
    payment: {
      icon: Wallet,
      bg: 'bg-success-100 dark:bg-success-900/30',
      iconColor: 'text-success-600 dark:text-success-400',
    },
    staff: {
      icon: User,
      bg: 'bg-accent-100 dark:bg-accent-900/30',
      iconColor: 'text-accent-600 dark:text-accent-400',
    },
    alert: {
      icon: AlertTriangle,
      bg: 'bg-warning-100 dark:bg-warning-900/30',
      iconColor: 'text-warning-600 dark:text-warning-400',
    },
    system: {
      icon: Bell,
      bg: 'bg-surface-100 dark:bg-surface-800',
      iconColor: 'text-surface-600 dark:text-surface-400',
    },
    success: {
      icon: CheckCircle,
      bg: 'bg-success-100 dark:bg-success-900/30',
      iconColor: 'text-success-600 dark:text-success-400',
    },
    info: {
      icon: Info,
      bg: 'bg-info-100 dark:bg-info-900/30',
      iconColor: 'text-info-600 dark:text-info-400',
    },
  };

  const config = typeConfig[notification.type];
  const Icon = config.icon;

  const formattedTime = formatDate(notification.timestamp, { format: 'relative' });

  return (
    <div
      onClick={() => onPress?.(notification)}
      className={cn(
        'relative flex items-start gap-3 p-4',
        'border-b border-surface-100 dark:border-surface-800',
        'transition-colors duration-200',
        !notification.read && 'bg-primary-50/30 dark:bg-primary-900/5',
        onPress && 'cursor-pointer hover:bg-surface-50 dark:hover:bg-surface-800/50',
        className
      )}
    >
      {/* Unread Indicator */}
      {!notification.read && (
        <div className="absolute top-4 left-1 w-2 h-2 rounded-full bg-primary-500" />
      )}

      {/* Icon */}
      <div
        className={cn(
          'flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center',
          config.bg,
          config.iconColor
        )}
      >
        {notification.imageUrl ? (
          <img
            src={notification.imageUrl}
            alt=""
            className="w-full h-full object-cover rounded-xl"
          />
        ) : (
          <Icon className="w-5 h-5" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0 pr-8">
        {/* Title */}
        <div className="flex items-start justify-between gap-2">
          <h4 className={cn(
            'font-semibold text-sm text-surface-900 dark:text-white',
            !notification.read && 'text-primary-900 dark:text-primary-100'
          )}>
            {notification.title}
          </h4>
        </div>

        {/* Message */}
        <p className="text-sm text-surface-500 dark:text-surface-400 mt-0.5 line-clamp-2">
          {notification.message}
        </p>

        {/* Timestamp & Action */}
        <div className="flex items-center gap-2 mt-2">
          <span className="text-xs text-surface-400 dark:text-surface-500">
            {formattedTime}
          </span>
          {notification.actionable && notification.actionLabel && (
            <>
              <span className="text-surface-300">·</span>
              <span className="text-xs font-medium text-primary-600 dark:text-primary-400">
                {notification.actionLabel}
              </span>
            </>
          )}
        </div>
      </div>

      {/* Dismiss Button */}
      {onDismiss && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onDismiss(notification);
          }}
          className={cn(
            'absolute top-3 right-3 p-1.5 rounded-full',
            'text-surface-300 hover:text-surface-500',
            'dark:text-surface-600 dark:hover:text-surface-400',
            'hover:bg-surface-100 dark:hover:bg-surface-700',
            'transition-colors duration-200'
          )}
          aria-label="Dismiss notification"
        >
          <X className="w-4 h-4" />
        </button>
      )}

      {/* Chevron for pressable */}
      {onPress && !onDismiss && (
        <ChevronRight className="absolute top-1/2 right-3 -translate-y-1/2 w-5 h-5 text-surface-300 dark:text-surface-600" />
      )}
    </div>
  );
};

export default NotificationItem;
