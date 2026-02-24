/**
 * BottomSheet Component
 * 
 * Mobile-optimized modal alternative that slides up from the bottom.
 * Supports multiple snap points and gesture-based interactions.
 * 
 * Features:
 * - Multiple snap points (25%, 50%, 75%, 100%)
 * - Backdrop click to dismiss
 * - Smooth animations
 * - Safe area support
 * 
 * @example
 * <BottomSheet 
 *   isOpen={isOpen} 
 *   onClose={() => setIsOpen(false)}
 *   snapPoint="50%"
 * >
 *   <Content />
 * </BottomSheet>
 */

import React, { useEffect, useCallback } from 'react';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
  snapPoint?: '25%' | '50%' | '75%' | '100%' | 'auto';
  showHandle?: boolean;
  showCloseButton?: boolean;
  className?: string;
  preventClose?: boolean;
}

export const BottomSheet: React.FC<BottomSheetProps> = ({
  isOpen,
  onClose,
  children,
  title,
  snapPoint = '50%',
  showHandle = true,
  showCloseButton = true,
  className,
  preventClose = false,
}) => {
  // Handle escape key
  const handleEscape = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape' && !preventClose) {
      onClose();
    }
  }, [onClose, preventClose]);

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, handleEscape]);

  // Prevent body scroll when open
  useEffect(() => {
    if (isOpen) {
      const originalStyle = window.getComputedStyle(document.body).overflow;
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = originalStyle;
      };
    }
  }, [isOpen]);

  const snapPointClasses = {
    '25%': 'h-[25vh]',
    '50%': 'h-[50vh]',
    '75%': 'h-[75vh]',
    '100%': 'h-[100vh] rounded-t-none',
    'auto': 'max-h-[90vh]',
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[1400]">
      {/* Backdrop */}
      <div
        className={cn(
          'absolute inset-0 bg-black/50',
          'transition-opacity duration-300',
          'animate-fade-in'
        )}
        onClick={!preventClose ? onClose : undefined}
        aria-hidden="true"
      />

      {/* Sheet */}
      <div
        className={cn(
          'absolute bottom-0 left-0 right-0',
          'bg-white dark:bg-surface-900',
          'rounded-t-3xl',
          'shadow-2xl',
          'flex flex-col',
          'pb-[env(safe-area-inset-bottom)]',
          'animate-slide-in-up',
          snapPointClasses[snapPoint],
          className
        )}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'bottom-sheet-title' : undefined}
      >
        {/* Handle */}
        {showHandle && (
          <div className="flex justify-center pt-3 pb-1">
            <div className="w-10 h-1 rounded-full bg-surface-300 dark:bg-surface-600" />
          </div>
        )}

        {/* Header */}
        {(title || showCloseButton) && (
          <div className="flex items-center justify-between px-4 py-3 border-b border-surface-200 dark:border-surface-700">
            {title && (
              <h2 
                id="bottom-sheet-title"
                className="text-lg font-semibold text-surface-900 dark:text-white"
              >
                {title}
              </h2>
            )}
            
            {showCloseButton && !preventClose && (
              <button
                onClick={onClose}
                className={cn(
                  'p-2 rounded-full',
                  'hover:bg-surface-100 dark:hover:bg-surface-800',
                  'transition-colors duration-200',
                  'text-surface-500 dark:text-surface-400',
                  !title && 'ml-auto'
                )}
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
};

export default BottomSheet;
