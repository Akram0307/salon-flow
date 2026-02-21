/**
 * Salon Flow Owner Dashboard - QuickActions Component
 * Quick action buttons for common tasks
 */

import React, { forwardRef } from 'react';
import { cn } from '../../lib/utils';
import type { BaseComponentProps } from '../../types/design-system';

// ============================================
// QuickActions Types
// ============================================
export interface QuickAction {
  id: string;
  label: string;
  description?: string;
  icon: React.ReactNode;
  color?: 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'error';
  onClick: () => void;
  disabled?: boolean;
  badge?: string | number;
}

export interface QuickActionsProps extends BaseComponentProps {
  actions: QuickAction[];
  columns?: 2 | 3 | 4;
  size?: 'sm' | 'md' | 'lg';
}

// ============================================
// Style Variants
// ============================================
const colorStyles: Record<string, { bg: string; icon: string; hover: string }> = {
  primary: {
    bg: 'bg-primary-50 dark:bg-primary-900/20',
    icon: 'text-primary-600 dark:text-primary-400',
    hover: 'hover:bg-primary-100 dark:hover:bg-primary-900/30',
  },
  secondary: {
    bg: 'bg-secondary-50 dark:bg-secondary-900/20',
    icon: 'text-secondary-600 dark:text-secondary-400',
    hover: 'hover:bg-secondary-100 dark:hover:bg-secondary-900/30',
  },
  accent: {
    bg: 'bg-accent-50 dark:bg-accent-900/20',
    icon: 'text-accent-600 dark:text-accent-400',
    hover: 'hover:bg-accent-100 dark:hover:bg-accent-900/30',
  },
  success: {
    bg: 'bg-success-50 dark:bg-success-900/20',
    icon: 'text-success-600 dark:text-success-400',
    hover: 'hover:bg-success-100 dark:hover:bg-success-900/30',
  },
  warning: {
    bg: 'bg-warning-50 dark:bg-warning-900/20',
    icon: 'text-warning-600 dark:text-warning-400',
    hover: 'hover:bg-warning-100 dark:hover:bg-warning-900/30',
  },
  error: {
    bg: 'bg-error-50 dark:bg-error-900/20',
    icon: 'text-error-600 dark:text-error-400',
    hover: 'hover:bg-error-100 dark:hover:bg-error-900/30',
  },
};

const sizeStyles: Record<string, { container: string; icon: string; text: string }> = {
  sm: {
    container: 'p-3',
    icon: 'w-5 h-5',
    text: 'text-xs',
  },
  md: {
    container: 'p-4',
    icon: 'w-6 h-6',
    text: 'text-sm',
  },
  lg: {
    container: 'p-5',
    icon: 'w-7 h-7',
    text: 'text-base',
  },
};

const gridCols: Record<number, string> = {
  2: 'grid-cols-2',
  3: 'grid-cols-2 sm:grid-cols-3',
  4: 'grid-cols-2 sm:grid-cols-4',
};

// ============================================
// QuickActions Component
// ============================================
export const QuickActions = forwardRef<HTMLDivElement, QuickActionsProps>(
  ({ actions, columns = 4, size = 'md', className }, ref) => {
    return (
      <div ref={ref} className={cn('grid gap-3', gridCols[columns], className)}>
        {actions.map((action) => {
          const colors = colorStyles[action.color || 'primary'];
          const sizes = sizeStyles[size];

          return (
            <button
              key={action.id}
              onClick={action.onClick}
              disabled={action.disabled}
              className={cn(
                'relative flex flex-col items-center justify-center gap-2',
                'rounded-xl border border-surface-200 dark:border-surface-700',
                'transition-all duration-200',
                colors.bg,
                colors.hover,
                'disabled:opacity-50 disabled:cursor-not-allowed',
                sizes.container
              )}
            >
              {/* Badge */}
              {action.badge && (
                <span className="absolute top-2 right-2 px-1.5 py-0.5 text-xs font-medium bg-white dark:bg-surface-800 rounded-full shadow-sm">
                  {action.badge}
                </span>
              )}

              {/* Icon */}
              <span className={cn(colors.icon, sizes.icon)}>{action.icon}</span>

              {/* Label */}
              <span className={cn('font-medium text-surface-700 dark:text-surface-300', sizes.text)}>
                {action.label}
              </span>

              {/* Description */}
              {action.description && size === 'lg' && (
                <span className="text-xs text-surface-500 dark:text-surface-400 text-center">
                  {action.description}
                </span>
              )}
            </button>
          );
        })}
      </div>
    );
  }
);

QuickActions.displayName = 'QuickActions';

// ============================================
// Default Quick Actions
// ============================================
export const defaultQuickActions: QuickAction[] = [
  {
    id: 'new-booking',
    label: 'New Booking',
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
    ),
    color: 'primary',
    onClick: () => {},
  },
  {
    id: 'add-customer',
    label: 'Add Customer',
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
      </svg>
    ),
    color: 'secondary',
    onClick: () => {},
  },
  {
    id: 'ai-assistant',
    label: 'AI Assistant',
    description: 'Get AI help',
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    color: 'accent',
    onClick: () => {},
    badge: 'New',
  },
  {
    id: 'send-message',
    label: 'Send Message',
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    ),
    color: 'success',
    onClick: () => {},
  },
];

export default QuickActions;
