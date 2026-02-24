/**
 * Salon Flow Owner PWA - FormField Molecule
 * Label + Input + Error message + Helper text combination
 * Mobile-first with proper accessibility
 */

import React, { forwardRef } from 'react';
import { cn } from '@/lib/utils';
import type { InputProps } from '@/components/atoms';

// ============================================
// Types
// ============================================
export interface FormFieldProps extends Omit<InputProps, 'label' | 'helperText' | 'error'> {
  label: string;
  error?: string;
  helperText?: string;
  required?: boolean;
  children?: React.ReactNode;
  inputId?: string;
}

// ============================================
// FormField Component
// ============================================
export const FormField = forwardRef<HTMLDivElement, FormFieldProps>(
  (
    {
      label,
      error,
      helperText,
      required = false,
      children,
      inputId,
      className,
      size, // Extract size to not pass to native input
      ...props
    },
    ref
  ) => {
    const id = inputId || `field-${Math.random().toString(36).substring(2, 9)}`;
    const hasError = Boolean(error);
    const helpTextId = `${id}-help`;
    const errorId = `${id}-error`;

    return (
      <div ref={ref} className={cn('w-full space-y-1.5', className)} {...props}>
        {/* Label */}
        <label
          htmlFor={id}
          className={cn(
            'block text-sm font-medium',
            'text-surface-700 dark:text-surface-300',
            'min-h-[20px]'
          )}
        >
          {label}
          {required && (
            <span className="text-error-500 ml-0.5" aria-hidden="true">
              *
            </span>
          )}
        </label>

        {/* Input Container */}
        <div className="relative">
          {children ? (
            React.cloneElement(children as React.ReactElement, {
              id,
              'aria-invalid': hasError,
              'aria-describedby': cn(
                hasError && errorId,
                helperText && helpTextId
              ),
              className: cn(
                hasError && 'border-error-500 focus:border-error-500 focus:ring-error-500/20'
              ),
            })
          ) : (
            <input
              id={id}
              className={cn(
                // Base styles
                'w-full rounded-lg',
                'bg-white dark:bg-surface-800',
                'border border-surface-300 dark:border-surface-600',
                'text-surface-900 dark:text-surface-100',
                'placeholder:text-surface-400 dark:placeholder:text-surface-500',
                'focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500',
                'transition-colors duration-200',
                // Size
                'px-4 py-2.5 text-sm',
                // Error state
                hasError && 'border-error-500 focus:border-error-500 focus:ring-error-500/20',
                // Touch target
                'min-h-[44px]'
              )}
              aria-invalid={hasError}
              aria-describedby={cn(hasError && errorId, helperText && helpTextId)}
              {...props}
            />
          )}
        </div>

        {/* Helper Text or Error */}
        {(helperText || error) && (
          <div className="space-y-1">
            {helperText && !hasError && (
              <p
                id={helpTextId}
                className="text-xs text-surface-500 dark:text-surface-400"
              >
                {helperText}
              </p>
            )}
            {error && (
              <p
                id={errorId}
                className="text-xs text-error-500 dark:text-error-400 flex items-center gap-1"
                role="alert"
              >
                <svg
                  className="w-3.5 h-3.5 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
                {error}
              </p>
            )}
          </div>
        )}
      </div>
    );
  }
);

FormField.displayName = 'FormField';

export default FormField;
