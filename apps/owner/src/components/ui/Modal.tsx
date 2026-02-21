/**
 * Salon Flow Owner Dashboard - Modal Component
 * Professional modal with animations and accessibility
 */

import React, { useEffect, useCallback, forwardRef } from 'react';
import { cn } from '../../lib/utils';
import type { ModalSize, BaseComponentProps } from '../../types/design-system';

// ============================================
// Modal Component Types
// ============================================
export interface ModalProps extends BaseComponentProps {
  isOpen: boolean;
  onClose: () => void;
  size?: ModalSize;
  title?: string;
  description?: string;
  closeOnOverlayClick?: boolean;
  closeOnEsc?: boolean;
  showCloseButton?: boolean;
}

export interface ModalHeaderProps extends BaseComponentProps {
  title?: string;
  description?: string;
}

export interface ModalBodyProps extends BaseComponentProps {}

export interface ModalFooterProps extends BaseComponentProps {
  align?: 'left' | 'center' | 'right' | 'between';
}

// ============================================
// Style Variants
// ============================================
const sizeStyles: Record<ModalSize, string> = {
  xs: 'max-w-xs',
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  '2xl': 'max-w-2xl',
  '3xl': 'max-w-3xl',
  '4xl': 'max-w-4xl',
  '5xl': 'max-w-5xl',
  '6xl': 'max-w-6xl',
  full: 'max-w-[95vw] h-[95vh]',
};

// ============================================
// Modal Component
// ============================================
export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  size = 'md',
  title,
  description,
  closeOnOverlayClick = true,
  closeOnEsc = true,
  showCloseButton = true,
  className,
  children,
}) => {
  // Handle ESC key
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (closeOnEsc && event.key === 'Escape') {
        onClose();
      }
    },
    [closeOnEsc, onClose]
  );

  // Add/remove event listener
  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto"
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? 'modal-title' : undefined}
      aria-describedby={description ? 'modal-description' : undefined}
    >
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity animate-fade-in"
        onClick={closeOnOverlayClick ? onClose : undefined}
        aria-hidden="true"
      />

      {/* Modal Container */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div
          className={cn(
            // Base styles
            'relative w-full bg-white dark:bg-surface-800',
            'rounded-2xl shadow-xl',
            'transform transition-all animate-scale-in',
            // Size
            sizeStyles[size],
            // Custom className
            className
          )}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Close Button */}
          {showCloseButton && (
            <button
              type="button"
              onClick={onClose}
              className="absolute top-4 right-4 p-2 rounded-lg text-surface-400 hover:text-surface-600 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
              aria-label="Close modal"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}

          {/* Content */}
          {(title || description) && (
            <ModalHeader title={title} description={description} />
          )}
          {children}
        </div>
      </div>
    </div>
  );
};

// ============================================
// Modal Header Component
// ============================================
export const ModalHeader: React.FC<ModalHeaderProps> = ({
  title,
  description,
  className,
  children,
}) => {
  return (
    <div className={cn('px-6 py-4 border-b border-surface-100 dark:border-surface-700', className)}>
      {title && (
        <h2
          id="modal-title"
          className="text-lg font-semibold text-surface-900 dark:text-white"
        >
          {title}
        </h2>
      )}
      {description && (
        <p
          id="modal-description"
          className="mt-1 text-sm text-surface-500 dark:text-surface-400"
        >
          {description}
        </p>
      )}
      {children}
    </div>
  );
};

// ============================================
// Modal Body Component
// ============================================
export const ModalBody: React.FC<ModalBodyProps> = ({ className, children }) => {
  return (
    <div className={cn('px-6 py-4 max-h-[60vh] overflow-y-auto', className)}>
      {children}
    </div>
  );
};

// ============================================
// Modal Footer Component
// ============================================
export const ModalFooter: React.FC<ModalFooterProps> = ({
  align = 'right',
  className,
  children,
}) => {
  const alignStyles: Record<string, string> = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end',
    between: 'justify-between',
  };

  return (
    <div
      className={cn(
        'px-6 py-4 border-t border-surface-100 dark:border-surface-700',
        'flex items-center gap-3',
        alignStyles[align],
        className
      )}
    >
      {children}
    </div>
  );
};

// ============================================
// Confirm Dialog Component
// ============================================
export interface ConfirmDialogProps extends Omit<ModalProps, 'children'> {
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  variant?: 'danger' | 'warning' | 'info';
  loading?: boolean;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  variant = 'info',
  loading = false,
  ...props
}) => {
  const variantStyles: Record<string, string> = {
    danger: 'bg-error-600 hover:bg-error-700 focus:ring-error-500',
    warning: 'bg-warning-500 hover:bg-warning-600 focus:ring-warning-500',
    info: 'bg-primary-600 hover:bg-primary-700 focus:ring-primary-500',
  };

  return (
    <Modal {...props} size="sm">
      <ModalBody>
        <p className="text-surface-600 dark:text-surface-300">{props.description}</p>
      </ModalBody>
      <ModalFooter>
        <button
          type="button"
          onClick={props.onClose}
          disabled={loading}
          className="px-4 py-2 text-sm font-medium text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700 rounded-lg transition-colors"
        >
          {cancelText}
        </button>
        <button
          type="button"
          onClick={onConfirm}
          disabled={loading}
          className={cn(
            'px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors',
            'focus:outline-none focus:ring-2 focus:ring-offset-2',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            variantStyles[variant]
          )}
        >
          {loading ? 'Processing...' : confirmText}
        </button>
      </ModalFooter>
    </Modal>
  );
};

export default Modal;
