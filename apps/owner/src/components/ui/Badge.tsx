/**
 * Salon Flow Owner Dashboard - Badge Component
 * Professional badge with multiple variants and colors
 */

import React from 'react';
import { cn } from '../../lib/utils';
import type { BadgeVariant, BadgeColor, BaseComponentProps } from '../../types/design-system';

// ============================================
// Badge Component Types
// ============================================
export interface BadgeProps extends BaseComponentProps, React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  color?: BadgeColor;
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean;
  icon?: React.ReactNode;
  removable?: boolean;
  onRemove?: () => void;
}

// ============================================
// Style Variants
// ============================================
// const variantStyles: Record<BadgeVariant, string> = {
//   solid: '',
//   subtle: '',
//   outline: 'bg-transparent border',
//   default: '',
// };

const colorStyles: Record<BadgeColor, Record<BadgeVariant, string>> = {
  primary: {
    default: 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300',
    solid: 'bg-primary-600 text-white dark:bg-primary-500',
    subtle: 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400',
    outline: 'border-primary-300 text-primary-700 dark:border-primary-600 dark:text-primary-400',
    error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
    info: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    secondary: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300',
  },
  secondary: {
    default: 'bg-secondary-100 text-secondary-700 dark:bg-secondary-900/30 dark:text-secondary-300',
    solid: 'bg-secondary-600 text-white dark:bg-secondary-500',
    subtle: 'bg-secondary-50 text-secondary-600 dark:bg-secondary-900/20 dark:text-secondary-400',
    outline: 'border-secondary-300 text-secondary-700 dark:border-secondary-600 dark:text-secondary-400',
    error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
    info: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    secondary: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300',
  },
  accent: {
    default: 'bg-accent-100 text-accent-700 dark:bg-accent-900/30 dark:text-accent-300',
    solid: 'bg-accent-600 text-white dark:bg-accent-500',
    subtle: 'bg-accent-50 text-accent-600 dark:bg-accent-900/20 dark:text-accent-400',
    outline: 'border-accent-300 text-accent-700 dark:border-accent-600 dark:text-accent-400',
    error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
    info: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    secondary: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300',
  },
  success: {
    default: 'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-300',
    solid: 'bg-success-600 text-white dark:bg-success-500',
    subtle: 'bg-success-50 text-success-600 dark:bg-success-900/20 dark:text-success-400',
    outline: 'border-success-300 text-success-700 dark:border-success-600 dark:text-success-400',
    error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
    info: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    secondary: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300',
  },
  warning: {
    default: 'bg-warning-100 text-warning-700 dark:bg-warning-900/30 dark:text-warning-300',
    solid: 'bg-warning-600 text-white dark:bg-warning-500',
    subtle: 'bg-warning-50 text-warning-600 dark:bg-warning-900/20 dark:text-warning-400',
    outline: 'border-warning-300 text-warning-700 dark:border-warning-600 dark:text-warning-400',
    error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
    info: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    secondary: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300',
  },
  error: {
    default: 'bg-error-100 text-error-700 dark:bg-error-900/30 dark:text-error-300',
    solid: 'bg-error-600 text-white dark:bg-error-500',
    subtle: 'bg-error-50 text-error-600 dark:bg-error-900/20 dark:text-error-400',
    outline: 'border-error-300 text-error-700 dark:border-error-600 dark:text-error-400',
    error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
    info: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    secondary: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300',
  },
  surface: {
    default: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    solid: 'bg-gray-600 text-white dark:bg-gray-500',
    subtle: 'bg-gray-50 text-gray-600 dark:bg-gray-900/20 dark:text-gray-400',
    outline: 'border-gray-300 text-gray-700 dark:border-gray-600 dark:text-gray-400',
    error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
    info: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    secondary: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300',
  },
  info: {
    default: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    solid: 'bg-blue-600 text-white dark:bg-blue-500',
    subtle: 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400',
    outline: 'border-blue-300 text-blue-700 dark:border-blue-600 dark:text-blue-400',
    error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
    info: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    secondary: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300',
  },
  gray: {
    default: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    solid: 'bg-gray-600 text-white dark:bg-gray-500',
    subtle: 'bg-gray-50 text-gray-600 dark:bg-gray-900/20 dark:text-gray-400',
    outline: 'border-gray-300 text-gray-700 dark:border-gray-600 dark:text-gray-400',
    error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
    info: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    secondary: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300',
  },
};

const sizeStyles: Record<'sm' | 'md' | 'lg', string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-0.5 text-xs',
  lg: 'px-3 py-1 text-sm',
};

const dotColorStyles: Record<BadgeColor, string> = {
  primary: 'bg-primary-500',
  secondary: 'bg-secondary-500',
  accent: 'bg-accent-500',
  success: 'bg-success-500',
  warning: 'bg-warning-500',
  error: 'bg-error-500',
  surface: 'bg-surface-500',
  gray: 'bg-gray-500',
  info: 'bg-blue-500',
};

// ============================================
// Badge Component
// ============================================
export const Badge: React.FC<BadgeProps> = ({
  variant = 'default',
  color = 'primary',
  size = 'md',
  dot = false,
  icon,
  removable = false,
  onRemove,
  className,
  children,
  ...props
}) => {
  return (
    <span
      className={cn(
        // Base styles
        'inline-flex items-center gap-1.5 font-medium rounded-full',
        'transition-colors duration-150',
        // Variant and color styles
        colorStyles[color][variant],
        // Size styles
        sizeStyles[size],
        // Custom className
        className
      )}
      {...props}
    >
      {/* Dot indicator */}
      {dot && <span className={cn('w-1.5 h-1.5 rounded-full', dotColorStyles[color])} />}

      {/* Icon */}
      {icon && <span className="flex-shrink-0">{icon}</span>}

      {/* Content */}
      {children}

      {/* Remove button */}
      {removable && (
        <button
          type="button"
          onClick={onRemove}
          className="flex-shrink-0 ml-0.5 -mr-1 p-0.5 rounded-full hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
          aria-label="Remove"
        >
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      )}
    </span>
  );
};

// ============================================
// Status Badge Component
// ============================================
export type Status = 'active' | 'inactive' | 'pending' | 'completed' | 'cancelled' | 'confirmed';

export interface StatusBadgeProps extends Omit<BadgeProps, 'color'> {
  status: Status;
}

const statusConfig: Record<Status, { color: BadgeColor; label: string }> = {
  active: { color: 'success', label: 'Active' },
  inactive: { color: 'gray', label: 'Inactive' },
  pending: { color: 'warning', label: 'Pending' },
  completed: { color: 'success', label: 'Completed' },
  cancelled: { color: 'error', label: 'Cancelled' },
  confirmed: { color: 'primary', label: 'Confirmed' },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, ...props }) => {
  const config = statusConfig[status];
  return (
    <Badge color={config.color} dot {...props}>
      {config.label}
    </Badge>
  );
};

export default Badge;
