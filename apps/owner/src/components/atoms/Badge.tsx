/**
 * Salon Flow Owner PWA - Badge Atom Component
 * Status indicators with multiple variants and colors
 */

import React from 'react';
import { cn } from '@/lib/utils';
import type { BaseComponentProps } from '@/types/design-system';

// ============================================
// Types
// ============================================
export type BadgeVariant = 'solid' | 'subtle' | 'outline';
export type BadgeSize = 'sm' | 'md' | 'lg';
export type BadgeStatus = 'confirmed' | 'pending' | 'cancelled' | 'completed' | 'default' | 'gray' | 'success' | 'warning' | 'error' | 'info' | 'secondary';

export interface BadgeProps extends BaseComponentProps {
  variant?: BadgeVariant;
  size?: BadgeSize;
  status?: BadgeStatus;
  children: React.ReactNode;
}

// ============================================
// Style Variants
// ============================================
const variantStyles: Record<BadgeVariant, string> = {
  solid: 'font-medium',
  subtle: 'font-medium bg-opacity-10 dark:bg-opacity-20',
  outline: 'bg-transparent border font-medium',
};

const sizeStyles: Record<BadgeSize, string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base',
};

const statusStyles: Record<BadgeStatus, Record<BadgeVariant, string>> = {
  confirmed: {
    solid: 'bg-success-500 text-white',
    subtle: 'bg-success-500 text-success-700 dark:text-success-300',
    outline: 'border-success-500 text-success-600 dark:text-success-400',
  },
  success: {
    solid: 'bg-success-500 text-white',
    subtle: 'bg-success-500 text-success-700 dark:text-success-300',
    outline: 'border-success-500 text-success-600 dark:text-success-400',
  },
  pending: {
    solid: 'bg-warning-500 text-white',
    subtle: 'bg-warning-500 text-warning-700 dark:text-warning-300',
    outline: 'border-warning-500 text-warning-600 dark:text-warning-400',
  },
  warning: {
    solid: 'bg-warning-500 text-white',
    subtle: 'bg-warning-500 text-warning-700 dark:text-warning-300',
    outline: 'border-warning-500 text-warning-600 dark:text-warning-400',
  },
  cancelled: {
    solid: 'bg-error-500 text-white',
    subtle: 'bg-error-500 text-error-700 dark:text-error-300',
    outline: 'border-error-500 text-error-600 dark:text-error-400',
  },
  error: {
    solid: 'bg-error-500 text-white',
    subtle: 'bg-error-500 text-error-700 dark:text-error-300',
    outline: 'border-error-500 text-error-600 dark:text-error-400',
  },
  completed: {
    solid: 'bg-primary-500 text-white',
    subtle: 'bg-primary-500 text-primary-700 dark:text-primary-300',
    outline: 'border-primary-500 text-primary-600 dark:text-primary-400',
  },
  default: {
    solid: 'bg-surface-500 text-white',
    subtle: 'bg-surface-500 text-surface-700 dark:text-surface-300',
    outline: 'border-surface-500 text-surface-600 dark:text-surface-400',
  },
  gray: {
    solid: 'bg-surface-500 text-white',
    subtle: 'bg-surface-500 text-surface-700 dark:text-surface-300',
    outline: 'border-surface-500 text-surface-600 dark:text-surface-400',
  },
  info: {
    solid: 'bg-info-500 text-white',
    subtle: 'bg-info-500 text-info-700 dark:text-info-300',
    outline: 'border-info-500 text-info-600 dark:text-info-400',
  },
  secondary: {
    solid: 'bg-secondary-500 text-white',
    subtle: 'bg-secondary-500 text-secondary-700 dark:text-secondary-300',
    outline: 'border-secondary-500 text-secondary-600 dark:text-secondary-400',
  },
};

// ============================================
// Badge Component
// ============================================
export const Badge: React.FC<BadgeProps> = ({
  variant = 'subtle',
  size = 'md',
  status = 'default',
  className,
  children,
  ...props
}) => {
  return (
    <span
      className={cn(
        // Base styles
        'inline-flex items-center justify-center',
        'rounded-full',
        'transition-colors duration-200',
        // Size styles
        sizeStyles[size],
        // Variant styles
        variantStyles[variant],
        // Status styles
        statusStyles[status][variant],
        // Custom className
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};

export default Badge;
