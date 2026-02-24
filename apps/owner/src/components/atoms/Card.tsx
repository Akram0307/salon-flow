/**
 * Salon Flow Owner PWA - Card Atom Component
 * Base container with variants, sizes, and hover effects
 */

import React, { forwardRef } from 'react';
import { cn } from '@/lib/utils';
import type { BaseComponentProps } from '@/types/design-system';

// ============================================
// Types
// ============================================
export type CardVariant = 'default' | 'outlined' | 'ghost' | 'elevated';
export type CardSize = 'sm' | 'md' | 'lg';

export interface CardProps extends BaseComponentProps {
  variant?: CardVariant;
  size?: CardSize;
  hoverable?: boolean;
  clickable?: boolean;
  onClick?: (event: React.MouseEvent<HTMLDivElement>) => void;
}

// ============================================
// Style Variants
// ============================================
const variantStyles: Record<CardVariant, string> = {
  default: `
    bg-white dark:bg-surface-800
    border border-surface-200 dark:border-surface-700
    shadow-sm
  `,
  outlined: `
    bg-transparent
    border-2 border-surface-200 dark:border-surface-700
  `,
  ghost: `
    bg-surface-50 dark:bg-surface-900/50
    border border-transparent
  `,
  elevated: `
    bg-white dark:bg-surface-800
    border border-surface-200 dark:border-surface-700
    shadow-md
  `,
};

const sizeStyles: Record<CardSize, string> = {
  sm: 'p-3',
  md: 'p-4',
  lg: 'p-6',
};

// ============================================
// Card Component
// ============================================
export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      variant = 'default',
      size = 'md',
      hoverable = false,
      clickable = false,
      onClick,
      className,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <div
        ref={ref}
        onClick={onClick}
        className={cn(
          // Base styles
          'rounded-xl',
          'transition-all duration-200 ease-smooth',
          // Variant styles
          variantStyles[variant],
          // Size styles
          sizeStyles[size],
          // Hover effects
          hoverable && 'hover:shadow-lg hover:border-surface-300 dark:hover:border-surface-600',
          // Clickable styles
          clickable && [
            'cursor-pointer',
            'active:scale-[0.98]',
            'hover:bg-surface-50 dark:hover:bg-surface-700/50',
          ],
          // Custom className
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

// Card Header Component
export interface CardHeaderProps extends BaseComponentProps {
  action?: React.ReactNode;
}

export const CardHeader: React.FC<CardHeaderProps> = ({
  className,
  children,
  action,
  ...props
}) => {
  return (
    <div
      className={cn(
        'flex items-center justify-between',
        'mb-4',
        className
      )}
      {...props}
    >
      <div className="flex-1 min-w-0">{children}</div>
      {action && <div className="flex-shrink-0 ml-4">{action}</div>}
    </div>
  );
};

// Card Title Component
export interface CardTitleProps extends BaseComponentProps {}

export const CardTitle: React.FC<CardTitleProps> = ({
  className,
  children,
  ...props
}) => {
  return (
    <h3
      className={cn(
        'text-lg font-semibold text-surface-900 dark:text-surface-100',
        'truncate',
        className
      )}
      {...props}
    >
      {children}
    </h3>
  );
};

// Card Description Component
export interface CardDescriptionProps extends BaseComponentProps {}

export const CardDescription: React.FC<CardDescriptionProps> = ({
  className,
  children,
  ...props
}) => {
  return (
    <p
      className={cn(
        'text-sm text-surface-500 dark:text-surface-400',
        'mt-1',
        className
      )}
      {...props}
    >
      {children}
    </p>
  );
};

// Card Content Component
export interface CardContentProps extends BaseComponentProps {}

export const CardContent: React.FC<CardContentProps> = ({
  className,
  children,
  ...props
}) => {
  return (
    <div className={cn('', className)} {...props}>
      {children}
    </div>
  );
};

// Card Footer Component
export interface CardFooterProps extends BaseComponentProps {}

export const CardFooter: React.FC<CardFooterProps> = ({
  className,
  children,
  ...props
}) => {
  return (
    <div
      className={cn(
        'flex items-center justify-between',
        'mt-4 pt-4',
        'border-t border-surface-200 dark:border-surface-700',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
