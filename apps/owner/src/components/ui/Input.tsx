/**
 * Salon Flow Owner Dashboard - Input Component
 * Professional input with multiple variants and states
 */

import React, { forwardRef, useState } from 'react';
import { cn } from '../../lib/utils';
import type { InputSize, InputVariant, BaseComponentProps } from '../../types/design-system';

// ============================================
// Input Component Types
// ============================================
export interface InputProps extends BaseComponentProps, Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  size?: InputSize;
  variant?: InputVariant;
  label?: string;
  helperText?: string;
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  rightElement?: React.ReactNode;
  fullWidth?: boolean;
}

// ============================================
// Style Variants
// ============================================
const variantStyles: Record<InputVariant, string> = {
  default: `
    bg-white dark:bg-surface-800
    border border-surface-300 dark:border-surface-600
    focus:border-primary-500 focus:ring-primary-500
  `,
  filled: `
    bg-surface-100 dark:bg-surface-800
    border border-transparent
    focus:bg-white dark:focus:bg-surface-800
    focus:border-primary-500 focus:ring-primary-500
  `,
  flushed: `
    bg-transparent
    border-0 border-b-2 border-surface-300 dark:border-surface-600
    rounded-none
    focus:border-primary-500 focus:ring-0
    px-0
  `,
  unstyled: `
    bg-transparent
    border-0
    focus:ring-0
    px-0
  `,
};

const sizeStyles: Record<InputSize, string> = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2.5 text-sm',
  lg: 'px-4 py-3 text-base',
};

const iconSizeStyles: Record<InputSize, string> = {
  sm: 'w-4 h-4',
  md: 'w-5 h-5',
  lg: 'w-5 h-5',
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
      rightElement,
      fullWidth = true,
      className,
      id,
      disabled,
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${Math.random().toString(36).substring(2, 9)}`;
    const hasError = !!error;

    return (
      <div className={cn(fullWidth && 'w-full', className)}>
        {/* Label */}
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5"
          >
            {label}
          </label>
        )}

        {/* Input Container */}
        <div className="relative">
          {/* Left Icon */}
          {leftIcon && (
            <div className={cn(
              'absolute left-3 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500',
              iconSizeStyles[size]
            )}>
              {leftIcon}
            </div>
          )}

          {/* Input */}
          <input
            ref={ref}
            id={inputId}
            disabled={disabled}
            className={cn(
              // Base styles
              'block rounded-lg w-full',
              'text-surface-900 dark:text-white',
              'placeholder:text-surface-400 dark:placeholder:text-surface-500',
              'focus:outline-none focus:ring-2 focus:ring-offset-0',
              'disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-surface-100 dark:disabled:bg-surface-800',
              'transition-colors duration-150',
              // Variant styles
              variantStyles[variant],
              // Size styles
              sizeStyles[size],
              // Icon padding
              leftIcon && 'pl-10',
              (rightIcon || rightElement) && 'pr-10',
              // Error state
              hasError && 'border-error-500 focus:border-error-500 focus:ring-error-500'
            )}
            aria-invalid={hasError}
            aria-describedby={hasError ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
            {...props}
          />

          {/* Right Icon */}
          {rightIcon && !rightElement && (
            <div className={cn(
              'absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500',
              iconSizeStyles[size]
            )}>
              {rightIcon}
            </div>
          )}

          {/* Right Element */}
          {rightElement && (
            <div className="absolute right-2 top-1/2 -translate-y-1/2">
              {rightElement}
            </div>
          )}
        </div>

        {/* Helper Text */}
        {helperText && !hasError && (
          <p id={`${inputId}-helper`} className="mt-1.5 text-sm text-surface-500 dark:text-surface-400">
            {helperText}
          </p>
        )}

        {/* Error Message */}
        {hasError && (
          <p id={`${inputId}-error`} className="mt-1.5 text-sm text-error-600 dark:text-error-400" role="alert">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

// ============================================
// Textarea Component
// ============================================
export interface TextareaProps extends InputProps {
  rows?: number;
  resize?: 'none' | 'vertical' | 'horizontal' | 'both';
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      size = 'md',
      variant = 'default',
      label,
      helperText,
      error,
      fullWidth = true,
      rows = 4,
      resize = 'vertical',
      className,
      id,
      disabled,
      ...props
    },
    ref
  ) => {
    const inputId = id || `textarea-${Math.random().toString(36).substring(2, 9)}`;
    const hasError = !!error;

    const resizeStyles: Record<string, string> = {
      none: 'resize-none',
      vertical: 'resize-y',
      horizontal: 'resize-x',
      both: 'resize',
    };

    return (
      <div className={cn(fullWidth && 'w-full', className)}>
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5"
          >
            {label}
          </label>
        )}

        <textarea
          ref={ref}
          id={inputId}
          disabled={disabled}
          rows={rows}
          className={cn(
            'block rounded-lg w-full',
            'text-surface-900 dark:text-white',
            'placeholder:text-surface-400 dark:placeholder:text-surface-500',
            'focus:outline-none focus:ring-2 focus:ring-offset-0',
            'disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-surface-100 dark:disabled:bg-surface-800',
            'transition-colors duration-150',
            variantStyles[variant],
            sizeStyles[size],
            resizeStyles[resize],
            hasError && 'border-error-500 focus:border-error-500 focus:ring-error-500'
          )}
          aria-invalid={hasError}
          aria-describedby={hasError ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
          {...props}
        />

        {helperText && !hasError && (
          <p id={`${inputId}-helper`} className="mt-1.5 text-sm text-surface-500 dark:text-surface-400">
            {helperText}
          </p>
        )}

        {hasError && (
          <p id={`${inputId}-error`} className="mt-1.5 text-sm text-error-600 dark:text-error-400" role="alert">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

// ============================================
// Search Input Component
// ============================================
export interface SearchInputProps extends Omit<InputProps, 'leftIcon' | 'type'> {
  onClear?: () => void;
}

export const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(
  ({ onClear, ...props }, ref) => {
    const [showClear, setShowClear] = useState(false);

    return (
      <Input
        ref={ref}
        type="search"
        leftIcon={
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        }
        rightElement={
          showClear && onClear ? (
            <button
              type="button"
              onClick={onClear}
              className="p-1 rounded-full hover:bg-surface-100 dark:hover:bg-surface-700 text-surface-400"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </button>
          ) : undefined
        }
        onChange={(e) => {
          setShowClear(e.target.value.length > 0);
          props.onChange?.(e);
        }}
        {...props}
      />
    );
  }
);

SearchInput.displayName = 'SearchInput';

export default Input;
