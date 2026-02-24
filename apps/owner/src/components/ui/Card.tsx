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
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
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
      title,
      subtitle,
      actions,
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
          'rounded-xl overflow-hidden',
          'transition-all duration-200 ease-smooth',
          variantStyles[variant],
          paddingStyles[padding],
          hoverable && 'hover:shadow-card-hover hover:-translate-y-0.5',
          clickable && 'cursor-pointer hover:shadow-card-hover active:scale-[0.99]',
          className
        )}
        {...props}
      >
        {(title || subtitle || actions) && (
          <div className="px-4 sm:px-5 py-4 border-b border-surface-100 dark:border-surface-700">
            <div className="flex items-start justify-between gap-4">
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
              </div>
              {actions && <div className="flex-shrink-0">{actions}</div>}
            </div>
          </div>
        )}
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
  const alignStyles = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end',
    between: 'justify-between',
  };

  return (
    <div
      className={cn(
        'px-4 sm:px-5 py-4 border-t border-surface-100 dark:border-surface-700',
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
    type: 'neutral' | 'increase' | 'decrease';
    period?: string;
  };
  icon?: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
}

const statColorStyles = {
  primary: 'bg-primary-50 text-primary-600',
  secondary: 'bg-secondary-50 text-secondary-600',
  success: 'bg-green-50 text-green-600',
  warning: 'bg-yellow-50 text-yellow-600',
  error: 'bg-red-50 text-red-600',
  info: 'bg-blue-50 text-blue-600',
};

const changeColorStyles = {
  increase: 'text-green-600',
  decrease: 'text-red-600',
  neutral: 'text-surface-500',
};

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  icon,
  color = 'primary',
  className,
}) => {
  return (
    <Card className={cn('p-5', className)}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-surface-500 dark:text-surface-400">{title}</p>
          <p className="mt-1 text-2xl font-bold text-surface-900 dark:text-white">{value}</p>
          {change && (
            <p className={cn('mt-1 text-sm', changeColorStyles[change.type])}>
              {change.type === 'increase' && '+'}
              {change.value}%
              {change.period && <span className="text-surface-400 ml-1">{change.period}</span>}
            </p>
          )}
        </div>
        {icon && (
          <div className={cn('p-2 rounded-lg', statColorStyles[color])}>
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
};

export default Card;
