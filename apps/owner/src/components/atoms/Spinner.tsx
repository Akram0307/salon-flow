/**
 * Salon Flow Owner PWA - Spinner Atom Component
 * Loading indicator with multiple sizes and colors
 */

import React from 'react';
import { cn } from '@/lib/utils';
import type { BaseComponentProps } from '@/types/design-system';

// ============================================
// Types
// ============================================
export type SpinnerSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type SpinnerColor = 'primary' | 'white' | 'gray' | 'current';

export interface SpinnerProps extends BaseComponentProps {
  size?: SpinnerSize;
  color?: SpinnerColor;
}

// ============================================
// Style Variants
// ============================================
const sizeStyles: Record<SpinnerSize, string> = {
  xs: 'w-3 h-3',
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
  xl: 'w-12 h-12',
};

const colorStyles: Record<SpinnerColor, string> = {
  primary: 'text-primary-600 dark:text-primary-400',
  white: 'text-white',
  gray: 'text-surface-400 dark:text-surface-500',
  current: 'text-current',
};

// ============================================
// Spinner Component
// ============================================
export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = 'primary',
  className,
  ...props
}) => {
  return (
    <svg
      className={cn(
        'animate-spin',
        sizeStyles[size],
        colorStyles[color],
        className
      )}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
      {...props}
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
};

// Spinner with label for accessibility
export interface SpinnerWithLabelProps extends SpinnerProps {
  label?: string;
  labelPosition?: 'left' | 'right' | 'top' | 'bottom';
}

export const SpinnerWithLabel: React.FC<SpinnerWithLabelProps> = ({
  label = 'Loading...',
  labelPosition = 'right',
  size = 'md',
  color = 'primary',
  className,
}) => {
  const isVertical = labelPosition === 'top' || labelPosition === 'bottom';

  return (
    <div
      className={cn(
        'inline-flex items-center',
        isVertical ? 'flex-col gap-2' : 'flex-row gap-2',
        labelPosition === 'left' && 'flex-row-reverse',
        labelPosition === 'top' && 'flex-col-reverse',
        className
      )}
    >
      <Spinner size={size} color={color} />
      <span className="text-sm text-surface-600 dark:text-surface-400">
        {label}
      </span>
    </div>
  );
};

// Full page loading overlay
export interface LoadingOverlayProps extends BaseComponentProps {
  message?: string;
  transparent?: boolean;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  message,
  transparent = false,
  className,
}) => {
  return (
    <div
      className={cn(
        'fixed inset-0 z-50',
        'flex flex-col items-center justify-center',
        transparent
          ? 'bg-transparent'
          : 'bg-white/80 dark:bg-surface-900/80 backdrop-blur-sm',
        className
      )}
    >
      <Spinner size="xl" />
      {message && (
        <p className="mt-4 text-surface-600 dark:text-surface-400">
          {message}
        </p>
      )}
    </div>
  );
};

export default Spinner;
