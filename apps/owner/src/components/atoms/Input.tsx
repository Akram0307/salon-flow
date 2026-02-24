/**
 * Salon Flow Owner PWA - Input Atom Component
 * Text input with validation states, icons, and dark mode support
 */

import React, { forwardRef } from 'react';
import { cn } from '@/lib/utils';
import type { InputSize, BaseComponentProps } from '@/types/design-system';

// ============================================
// Types
// ============================================
export interface InputProps extends BaseComponentProps, Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  size?: InputSize | 'sm' | 'md' | 'lg';
  label?: string;
  helperText?: string;
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
  variant?: 'default' | 'filled' | 'ghost';
}

// ============================================
// Style Variants
// ============================================
const sizeStyles: Record<string, string> = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2.5 text-sm',
  lg: 'px-4 py-3 text-base',
};

const iconSizeStyles: Record<string, string> = {
  sm: 'w-4 h-4',
  md: 'w-5 h-5',
  lg: 'w-5 h-5',
};

const iconPositionStyles: Record<string, string> = {
  sm: 'left-2.5',
  md: 'left-3',
  lg: 'left-4',
};

const rightIconPositionStyles: Record<string, string> = {
  sm: 'right-2.5',
  md: 'right-3',
  lg: 'right-4',
};

const variantStyles: Record<string, string> = {
  default: `
    bg-white dark:bg-surface-800
    border border-surface-300 dark:border-surface-600
    focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20
  `,
  filled: `
    bg-surface-100 dark:bg-surface-700
    border border-transparent
    focus:bg-white dark:focus:bg-surface-800
    focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20
  `,
  ghost: `
    bg-transparent
    border-0 border-b border-surface-300 dark:border-surface-600
    rounded-none
    focus:border-primary-500 focus:ring-0
    px-0
  `,
};

// ============================================
// Input Component
// ============================================
export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      size = 'md',
      variant = 'default',
      label,
      helperText,
      error,
      leftIcon,
      rightIcon,
      fullWidth = true,
      className,
      id,
      disabled,
      type = 'text',
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${Math.random().toString(36).substring(2, 9)}`;
    const hasError = !!error;
    const hasLeftIcon = !!leftIcon;
    const hasRightIcon = !!rightIcon;

    const inputStyles = cn(
      // Base styles
      'w-full rounded-lg',
      'text-surface-900 dark:text-surface-100',
      'placeholder:text-surface-400 dark:placeholder:text-surface-500',
      'transition-all duration-200 ease-smooth',
      'focus:outline-none',
      'disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-surface-100',
      // Variant styles
      variantStyles[variant],
      // Size styles
      sizeStyles[size],
      // Error state
      hasError && 'border-error-500 focus:border-error-500 focus:ring-error-500/20',
      // Icon padding
      hasLeftIcon && variant !== 'ghost' && 'pl-10',
      hasRightIcon && variant !== 'ghost' && 'pr-10',
      // Touch target minimum
      'min-h-[44px]'
    );

    return (
      <div className={cn(fullWidth && 'w-full', className)}>
        {/* Label */}
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5"
          >
            {label}
            {props.required && <span className="text-error-500 ml-1">*</span>}
          </label>
        )}

        {/* Input Container */}
        <div className="relative">
          {/* Left Icon */}
          {hasLeftIcon && (
            <div
              className={cn(
                'absolute top-1/2 -translate-y-1/2 text-surface-400',
                iconPositionStyles[size]
              )}
            >
              <span className={iconSizeStyles[size]}>{leftIcon}</span>
            </div>
          )}

          {/* Input Element */}
          <input
            ref={ref}
            id={inputId}
            type={type}
            disabled={disabled}
            className={inputStyles}
            aria-invalid={hasError}
            aria-describedby={
              hasError ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined
            }
            {...props}
          />

          {/* Right Icon */}
          {hasRightIcon && (
            <div
              className={cn(
                'absolute top-1/2 -translate-y-1/2 text-surface-400',
                rightIconPositionStyles[size]
              )}
            >
              <span className={iconSizeStyles[size]}>{rightIcon}</span>
            </div>
          )}
        </div>

        {/* Helper Text */}
        {helperText && !hasError && (
          <p
            id={`${inputId}-helper`}
            className="mt-1.5 text-sm text-surface-500 dark:text-surface-400"
          >
            {helperText}
          </p>
        )}

        {/* Error Message */}
        {hasError && (
          <p
            id={`${inputId}-error`}
            className="mt-1.5 text-sm text-error-500 flex items-center gap-1"
          >
            <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
