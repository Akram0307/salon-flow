/**
 * Salon Flow Owner Dashboard - Button Component
 * Professional button with multiple variants, sizes, and states
 */

import React, { forwardRef } from 'react';
import { cn } from '../../lib/utils';
import type { ButtonVariant, ButtonSize, BaseComponentProps } from '../../types/design-system';

// ============================================
// Button Component Types
// ============================================
export interface ButtonProps extends BaseComponentProps, React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
  rounded?: boolean;
}

// ============================================
// Style Variants
// ============================================
const variantStyles: Record<ButtonVariant, string> = {
  primary: `
    bg-primary-600 text-white 
    hover:bg-primary-700 
    focus:ring-primary-500 
    active:bg-primary-800
    shadow-sm hover:shadow-md
    dark:bg-primary-500 dark:hover:bg-primary-600
  `,
  secondary: `
    bg-secondary-600 text-white 
    hover:bg-secondary-700 
    focus:ring-secondary-500 
    active:bg-secondary-800
    shadow-sm hover:shadow-md
    dark:bg-secondary-500 dark:hover:bg-secondary-600
  `,
  accent: `
    bg-accent-600 text-white 
    hover:bg-accent-700 
    focus:ring-accent-500 
    active:bg-accent-800
    shadow-sm hover:shadow-md
    dark:bg-accent-500 dark:hover:bg-accent-600
  `,
  outline: `
    bg-transparent text-primary-600 
    border-2 border-primary-600 
    hover:bg-primary-50 
    focus:ring-primary-500 
    active:bg-primary-100
    dark:text-primary-400 dark:border-primary-400 
    dark:hover:bg-primary-900/20
  `,
  ghost: `
    bg-transparent text-surface-700 
    hover:bg-surface-100 
    focus:ring-surface-500 
    active:bg-surface-200
    dark:text-surface-300 dark:hover:bg-surface-800
  `,
  link: `
    bg-transparent text-primary-600 
    hover:text-primary-700 hover:underline 
    focus:ring-primary-500 
    underline-offset-4
    dark:text-primary-400 dark:hover:text-primary-300
  `,
  danger: `
    bg-error-600 text-white 
    hover:bg-error-700 
    focus:ring-error-500 
    active:bg-error-800
    shadow-sm hover:shadow-md
    dark:bg-error-500 dark:hover:bg-error-600
  `,
  success: `
    bg-success-600 text-white 
    hover:bg-success-700 
    focus:ring-success-500 
    active:bg-success-800
    shadow-sm hover:shadow-md
    dark:bg-success-500 dark:hover:bg-success-600
  `,
};

const sizeStyles: Record<ButtonSize, string> = {
  xs: 'px-2.5 py-1.5 text-xs gap-1',
  sm: 'px-3 py-2 text-sm gap-1.5',
  md: 'px-4 py-2.5 text-sm gap-2',
  lg: 'px-5 py-3 text-base gap-2',
  xl: 'px-6 py-3.5 text-lg gap-2.5',
};

const iconSizeStyles: Record<ButtonSize, string> = {
  xs: 'w-3.5 h-3.5',
  sm: 'w-4 h-4',
  md: 'w-4 h-4',
  lg: 'w-5 h-5',
  xl: 'w-5 h-5',
};

// ============================================
// Button Component
// ============================================
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      leftIcon,
      rightIcon,
      fullWidth = false,
      rounded = false,
      disabled,
      className,
      children,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        className={cn(
          // Base styles
          'inline-flex items-center justify-center',
          'font-medium rounded-lg',
          'transition-all duration-200 ease-smooth',
          'focus:outline-none focus:ring-2 focus:ring-offset-2',
          'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
          // Variant styles
          variantStyles[variant],
          // Size styles
          sizeStyles[size],
          // Full width
          fullWidth && 'w-full',
          // Rounded
          rounded && 'rounded-full',
          // Custom className
          className
        )}
        {...props}
      >
        {/* Loading Spinner */}
        {loading && (
          <svg
            className={cn('animate-spin', iconSizeStyles[size])}
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
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
        )}

        {/* Left Icon */}
        {!loading && leftIcon && (
          <span className={cn('flex-shrink-0', iconSizeStyles[size])}>
            {leftIcon}
          </span>
        )}

        {/* Button Text */}
        {children && <span className="truncate">{children}</span>}

        {/* Right Icon */}
        {rightIcon && (
          <span className={cn('flex-shrink-0', iconSizeStyles[size])}>
            {rightIcon}
          </span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

// ============================================
// Icon Button Variant
// ============================================
export interface IconButtonProps extends Omit<ButtonProps, 'leftIcon' | 'rightIcon' | 'children'> {
  icon: React.ReactNode;
  'aria-label': string;
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ icon, size = 'md', className, ...props }, ref) => {
    return (
      <Button
        ref={ref}
        size={size}
        className={cn('!p-2', className)}
        {...props}
      >
        {icon}
      </Button>
    );
  }
);

IconButton.displayName = 'IconButton';

// ============================================
// Button Group Component
// ============================================
export interface ButtonGroupProps extends BaseComponentProps {
  orientation?: 'horizontal' | 'vertical';
  attached?: boolean;
}

export const ButtonGroup: React.FC<ButtonGroupProps> = ({
  orientation = 'horizontal',
  attached = false,
  className,
  children,
}) => {
  return (
    <div
      role="group"
      className={cn(
        'inline-flex',
        orientation === 'vertical' ? 'flex-col' : 'flex-row',
        attached && orientation === 'horizontal' && '[&>*:first-child]:rounded-r-none [&>*:not(:first-child):not(:last-child)]:rounded-none [&>*:last-child]:rounded-l-none',
        attached && orientation === 'vertical' && '[&>*:first-child]:rounded-b-none [&>*:not(:first-child):not(:last-child)]:rounded-none [&>*:last-child]:rounded-t-none',
        !attached && 'gap-2',
        className
      )}
    >
      {children}
    </div>
  );
};

export default Button;
