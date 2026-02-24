/**
 * Salon Flow Owner PWA - Tooltip Atom Component
 * Info tooltips with positioning and delay support
 */

import React, { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import type { BaseComponentProps } from '@/types/design-system';

// ============================================
// Types
// ============================================
export type TooltipPosition = 'top' | 'bottom' | 'left' | 'right';
export type TooltipTrigger = 'hover' | 'focus' | 'click';

export interface TooltipProps extends BaseComponentProps {
  content: React.ReactNode;
  position?: TooltipPosition;
  delay?: number;
  trigger?: TooltipTrigger[];
}

// ============================================
// Style Variants
// ============================================
const positionStyles: Record<TooltipPosition, string> = {
  top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
  bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
  left: 'right-full top-1/2 -translate-y-1/2 mr-2',
  right: 'left-full top-1/2 -translate-y-1/2 ml-2',
};

const arrowStyles: Record<TooltipPosition, string> = {
  top: 'top-full left-1/2 -translate-x-1/2 -mt-1 border-l-transparent border-r-transparent border-b-0 border-t-surface-800',
  bottom: 'bottom-full left-1/2 -translate-x-1/2 -mb-1 border-l-transparent border-r-transparent border-t-0 border-b-surface-800',
  left: 'left-full top-1/2 -translate-y-1/2 -ml-1 border-t-transparent border-b-transparent border-r-0 border-l-surface-800',
  right: 'right-full top-1/2 -translate-y-1/2 -mr-1 border-t-transparent border-b-transparent border-l-0 border-r-surface-800',
};

// ============================================
// Tooltip Component
// ============================================
export const Tooltip: React.FC<TooltipProps> = ({
  content,
  position = 'top',
  delay = 200,
  trigger = ['hover', 'focus'],
  className,
  children,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null);

  const show = useCallback(() => {
    if (timeoutId) clearTimeout(timeoutId);
    const id = setTimeout(() => setIsVisible(true), delay);
    setTimeoutId(id);
  }, [delay, timeoutId]);

  const hide = useCallback(() => {
    if (timeoutId) clearTimeout(timeoutId);
    setIsVisible(false);
  }, [timeoutId]);

  const handleClick = useCallback(() => {
    if (trigger.includes('click')) {
      setIsVisible(prev => !prev);
    }
  }, [trigger]);

  const eventHandlers: React.HTMLAttributes<HTMLDivElement> = {};

  if (trigger.includes('hover')) {
    eventHandlers.onMouseEnter = show;
    eventHandlers.onMouseLeave = hide;
  }

  if (trigger.includes('focus')) {
    eventHandlers.onFocus = show;
    eventHandlers.onBlur = hide;
  }

  if (trigger.includes('click')) {
    eventHandlers.onClick = handleClick;
  }

  return (
    <div className={cn('relative inline-flex', className)} {...eventHandlers}>
      {children}
      
      {/* Tooltip Content */}
      {isVisible && (
        <div
          className={cn(
            'absolute z-50',
            'px-3 py-2',
            'text-sm text-white',
            'bg-surface-800 dark:bg-surface-900',
            'rounded-lg shadow-lg',
            'whitespace-nowrap',
            'animate-in fade-in-0 zoom-in-95 duration-200',
            positionStyles[position]
          )}
          role="tooltip"
        >
          {content}
          {/* Arrow */}
          <div
            className={cn(
              'absolute w-0 h-0',
              'border-4 border-solid',
              arrowStyles[position]
            )}
          />
        </div>
      )}
    </div>
  );
};

// Simple Icon Tooltip wrapper
export interface IconTooltipProps extends Omit<TooltipProps, 'children'> {
  icon: React.ReactNode;
  iconClassName?: string;
}

export const IconTooltip: React.FC<IconTooltipProps> = ({
  icon,
  iconClassName,
  ...props
}) => {
  return (
    <Tooltip {...props}>
      <span className={cn('inline-flex items-center justify-center cursor-help text-surface-400 hover:text-surface-600 dark:text-surface-500 dark:hover:text-surface-300', iconClassName)}>
        {icon}
      </span>
    </Tooltip>
  );
};

export default Tooltip;
