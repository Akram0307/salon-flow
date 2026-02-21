/**
 * Salon Flow Owner Dashboard - StatCard Component
 * Professional metric card with trends and visualizations
 */

import React, { forwardRef } from 'react';
import { cn } from '../../lib/utils';
import { Badge } from '../ui/Badge';
import type { BaseComponentProps } from '../../types/design-system';

// ============================================
// StatCard Types
// ============================================
export interface StatCardProps extends BaseComponentProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    type: 'increase' | 'decrease' | 'neutral';
    period?: string;
  };
  icon?: React.ReactNode;
  iconColor?: 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'error';
  subtitle?: string;
  trend?: 'up' | 'down' | 'flat';
  sparklineData?: number[];
  onClick?: () => void;
  loading?: boolean;
}

// ============================================
// Style Variants
// ============================================
const iconColorStyles: Record<string, string> = {
  primary: 'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400',
  secondary: 'bg-secondary-100 text-secondary-600 dark:bg-secondary-900/30 dark:text-secondary-400',
  accent: 'bg-accent-100 text-accent-600 dark:bg-accent-900/30 dark:text-accent-400',
  success: 'bg-success-100 text-success-600 dark:bg-success-900/30 dark:text-success-400',
  warning: 'bg-warning-100 text-warning-600 dark:bg-warning-900/30 dark:text-warning-400',
  error: 'bg-error-100 text-error-600 dark:bg-error-900/30 dark:text-error-400',
};

const trendColorStyles: Record<string, string> = {
  up: 'text-success-600 dark:text-success-400',
  down: 'text-error-600 dark:text-error-400',
  flat: 'text-surface-500 dark:text-surface-400',
};

// ============================================
// Mini Sparkline Component
// ============================================
const MiniSparkline: React.FC<{ data: number[]; color?: string }> = ({ 
  data, 
  color = 'primary' 
}) => {
  if (data.length < 2) return null;

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const width = 80;
  const height = 24;
  const padding = 2;

  const points = data.map((value, index) => {
    const x = padding + (index / (data.length - 1)) * (width - 2 * padding);
    const y = height - padding - ((value - min) / range) * (height - 2 * padding);
    return `${x},${y}`;
  }).join(' ');

  const colorStyles: Record<string, string> = {
    primary: '#8B5CF6',
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
  };

  return (
    <svg width={width} height={height} className="opacity-60">
      <polyline
        fill="none"
        stroke={colorStyles[color] || colorStyles.primary}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
    </svg>
  );
};

// ============================================
// StatCard Component
// ============================================
export const StatCard = forwardRef<HTMLDivElement, StatCardProps>(
  (
    {
      title,
      value,
      change,
      icon,
      iconColor = 'primary',
      subtitle,
      trend,
      sparklineData,
      onClick,
      loading = false,
      className,
    },
    ref
  ) => {
    const Component = onClick ? 'button' : 'div';

    return (
      <Component
        ref={ref as any}
        onClick={onClick}
        className={cn(
          'bg-white dark:bg-surface-800 rounded-xl border border-surface-200 dark:border-surface-700',
          'p-5 transition-all duration-200',
          onClick && 'cursor-pointer hover:shadow-lg hover:border-primary-300 dark:hover:border-primary-600',
          className
        )}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            {/* Title */}
            <p className="text-sm font-medium text-surface-500 dark:text-surface-400 truncate">
              {title}
            </p>

            {/* Value */}
            <p className="mt-2 text-3xl font-bold text-surface-900 dark:text-white">
              {value}
            </p>

            {/* Change Indicator */}
            {change && (
              <div className="mt-2 flex items-center gap-2">
                <span
                  className={cn(
                    'inline-flex items-center gap-1 text-sm font-medium',
                    change.type === 'increase' && 'text-success-600 dark:text-success-400',
                    change.type === 'decrease' && 'text-error-600 dark:text-error-400',
                    change.type === 'neutral' && 'text-surface-500 dark:text-surface-400'
                  )}
                >
                  {change.type === 'increase' && (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                    </svg>
                  )}
                  {change.type === 'decrease' && (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                    </svg>
                  )}
                  {change.value > 0 && '+'}{change.value}%
                </span>
                {change.period && (
                  <span className="text-xs text-surface-400 dark:text-surface-500">
                    vs {change.period}
                  </span>
                )}
              </div>
            )}

            {/* Subtitle */}
            {subtitle && (
              <p className="mt-1 text-xs text-surface-400 dark:text-surface-500">
                {subtitle}
              </p>
            )}
          </div>

          {/* Icon */}
          {icon && (
            <div className={cn('p-3 rounded-xl', iconColorStyles[iconColor])}>
              {icon}
            </div>
          )}
        </div>

        {/* Sparkline */}
        {sparklineData && sparklineData.length > 1 && (
          <div className="mt-4 flex justify-end">
            <MiniSparkline data={sparklineData} color={iconColor} />
          </div>
        )}
      </Component>
    );
  }
);

StatCard.displayName = 'StatCard';

// ============================================
// StatCard Grid Component
// ============================================
export interface StatCardGridProps extends BaseComponentProps {
  cards: StatCardProps[];
  columns?: 2 | 3 | 4;
}

export const StatCardGrid: React.FC<StatCardGridProps> = ({
  cards,
  columns = 4,
  className,
}) => {
  const gridCols: Record<number, string> = {
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
  };

  return (
    <div className={cn('grid gap-4', gridCols[columns], className)}>
      {cards.map((card, index) => (
        <StatCard key={index} {...card} />
      ))}
    </div>
  );
};

export default StatCard;
