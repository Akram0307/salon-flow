/**
 * Salon Flow Owner Dashboard - Card Component
 * Professional card with multiple variants and states
 */

import React, { forwardRef } from 'react';
import { cn } from '../../lib/utils';
import type { CardVariant, BaseComponentProps } from '../../types/design-system';

// ============================================
// Card Component Types
// ============================================
export interface CardProps extends BaseComponentProps, React.HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  hoverable?: boolean;
  clickable?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export interface CardHeaderProps extends BaseComponentProps {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
}

export interface CardBodyProps extends BaseComponentProps {}

export interface CardFooterProps extends BaseComponentProps {
  align?: 'left' | 'center' | 'right' | 'between';
}

// ============================================
// Style Variants
// ============================================
const variantStyles: Record<CardVariant, string> = {
  default: 'bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700',
  elevated: 'bg-white dark:bg-surface-800 shadow-card hover:shadow-card-hover',
  outlined: 'bg-transparent border-2 border-surface-200 dark:border-surface-700',
  filled: 'bg-surface-50 dark:bg-surface-800/50',
};

const paddingStyles: Record<'none' | 'sm' | 'md' | 'lg', string> = {
  none: '',
  sm: 'p-3',
  md: 'p-4 sm:p-5',
  lg: 'p-5 sm:p-6',
};

// ============================================
// Card Component
// ============================================
export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      variant = 'default',
      hoverable = false,
      clickable = false,
      padding = 'none',
      className,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <div
        ref={ref}
        className={cn(
          // Base styles
          'rounded-xl overflow-hidden',
          'transition-all duration-200 ease-smooth',
          // Variant styles
          variantStyles[variant],
          // Padding
          paddingStyles[padding],
          // Interactive states
          hoverable && 'hover:shadow-card-hover hover:-translate-y-0.5',
          clickable && 'cursor-pointer hover:shadow-card-hover active:scale-[0.99]',
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

// ============================================
// Card Header Component
// ============================================
export const CardHeader: React.FC<CardHeaderProps> = ({
  title,
  subtitle,
  action,
  icon,
  className,
  children,
}) => {
  return (
    <div className={cn('px-4 sm:px-5 py-4 border-b border-surface-100 dark:border-surface-700', className)}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 min-w-0 flex-1">
          {icon && (
            <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-primary-600 dark:text-primary-400">
              {icon}
            </div>
          )}
          <div className="min-w-0 flex-1">
            {title && (
              <h3 className="text-base font-semibold text-surface-900 dark:text-white truncate">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="mt-0.5 text-sm text-surface-500 dark:text-surface-400 truncate">
                {subtitle}
              </p>
            )}
            {children}
          </div>
        </div>
        {action && <div className="flex-shrink-0">{action}</div>}
      </div>
    </div>
  );
};

// ============================================
// Card Body Component
// ============================================
export const CardBody: React.FC<CardBodyProps> = ({ className, children }) => {
  return (
    <div className={cn('px-4 sm:px-5 py-4', className)}>
      {children}
    </div>
  );
};

// ============================================
// Card Footer Component
// ============================================
export const CardFooter: React.FC<CardFooterProps> = ({
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
        'px-4 sm:px-5 py-3 bg-surface-50 dark:bg-surface-800/50 border-t border-surface-100 dark:border-surface-700',
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
// Stat Card Component
// ============================================
export interface StatCardProps extends BaseComponentProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
  };
  icon?: React.ReactNode;
  trend?: 'positive' | 'negative' | 'neutral';
  prefix?: string;
  suffix?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  icon,
  trend = 'neutral',
  prefix,
  suffix,
  className,
}) => {
  const trendColors = {
    positive: 'text-success-600 dark:text-success-400 bg-success-50 dark:bg-success-900/20',
    negative: 'text-error-600 dark:text-error-400 bg-error-50 dark:bg-error-900/20',
    neutral: 'text-surface-500 dark:text-surface-400 bg-surface-100 dark:bg-surface-700',
  };

  return (
    <Card variant="default" className={cn('p-5', className)}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-surface-500 dark:text-surface-400 truncate">
            {title}
          </p>
          <p className="mt-2 text-2xl sm:text-3xl font-bold text-surface-900 dark:text-white">
            {prefix && <span className="text-lg mr-0.5">{prefix}</span>}
            {value}
            {suffix && <span className="text-lg ml-0.5">{suffix}</span>}
          </p>
          {change && (
            <div className="mt-2 flex items-center gap-1.5">
              <span
                className={cn(
                  'inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full text-xs font-medium',
                  trendColors[trend]
                )}
              >
                {change.direction === 'up' && (
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                )}
                {change.direction === 'down' && (
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
                {change.value}%
              </span>
              <span className="text-xs text-surface-400 dark:text-surface-500">vs last period</span>
            </div>
          )}
        </div>
        {icon && (
          <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-primary-600 dark:text-primary-400">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
};

export default Card;
