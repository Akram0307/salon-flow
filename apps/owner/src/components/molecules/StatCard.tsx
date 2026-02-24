/**
 * Salon Flow Owner PWA - StatCard Molecule
 * Dashboard KPI display with AI action buttons
 * Based on mockup 06: Icon, value, label, trend, "Why?" and "Optimize" buttons
 */

import React from 'react';
import { TrendingUp, TrendingDown, Minus, Lightbulb, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

// ============================================
// Types
// ============================================
export type TrendDirection = 'up' | 'down' | 'neutral';

export interface StatCardProps {
  icon: React.ReactNode;
  value: string | number;
  label: string;
  trend?: TrendDirection;
  trendValue?: string;
  onWhy?: () => void;
  onOptimize?: () => void;
  className?: string;
  loading?: boolean;
}

// ============================================
// StatCard Component
// ============================================
export const StatCard: React.FC<StatCardProps> = ({
  icon,
  value,
  label,
  trend = 'neutral',
  trendValue,
  onWhy,
  onOptimize,
  className,
  loading = false,
}) => {
  const trendIcons = {
    up: TrendingUp,
    down: TrendingDown,
    neutral: Minus,
  };

  const trendStyles = {
    up: 'text-success-600 dark:text-success-400',
    down: 'text-error-600 dark:text-error-400',
    neutral: 'text-surface-400 dark:text-surface-500',
  };

  const TrendIcon = trendIcons[trend];

  if (loading) {
    return (
      <div
        className={cn(
          'bg-white dark:bg-surface-800 rounded-xl p-4',
          'border border-surface-200 dark:border-surface-700',
          'shadow-sm',
          className
        )}
      >
        <div className="animate-pulse space-y-3">
          <div className="w-10 h-10 rounded-lg bg-surface-200 dark:bg-surface-700" />
          <div className="h-8 w-24 bg-surface-200 dark:bg-surface-700 rounded" />
          <div className="h-4 w-16 bg-surface-200 dark:bg-surface-700 rounded" />
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'bg-white dark:bg-surface-800 rounded-xl p-4',
        'border border-surface-200 dark:border-surface-700',
        'shadow-sm',
        'flex flex-col',
        className
      )}
    >
      {/* Icon - Top Left */}
      <div
        className={cn(
          'w-10 h-10 rounded-lg flex items-center justify-center mb-3',
          'bg-primary-100 dark:bg-primary-900/30',
          'text-primary-600 dark:text-primary-400'
        )}
      >
        {icon}
      </div>

      {/* Value - Large */}
      <div className="text-3xl font-bold text-surface-900 dark:text-white mb-1">
        {value}
      </div>

      {/* Label */}
      <div className="text-sm text-surface-500 dark:text-surface-400 mb-3">
        {label}
      </div>

      {/* Trend Indicator */}
      {trendValue && (
        <div className={cn('flex items-center gap-1 text-sm mb-3', trendStyles[trend])}>
          <TrendIcon className="w-4 h-4" />
          <span className="font-medium">{trendValue}</span>
        </div>
      )}

      {/* AI Action Buttons */}
      <div className="flex items-center gap-2 mt-auto pt-2 border-t border-surface-100 dark:border-surface-700">
        {onWhy && (
          <button
            type="button"
            onClick={onWhy}
            className={cn(
              'flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium',
              'bg-indigo-50 dark:bg-indigo-900/20',
              'text-indigo-700 dark:text-indigo-300',
              'hover:bg-indigo-100 dark:hover:bg-indigo-900/30',
              'transition-colors duration-200',
              'min-h-[32px]'
            )}
          >
            <Lightbulb className="w-3.5 h-3.5" />
            Why?
          </button>
        )}
        {onOptimize && (
          <button
            type="button"
            onClick={onOptimize}
            className={cn(
              'flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium',
              'bg-primary-50 dark:bg-primary-900/20',
              'text-primary-700 dark:text-primary-300',
              'hover:bg-primary-100 dark:hover:bg-primary-900/30',
              'transition-colors duration-200',
              'min-h-[32px]'
            )}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Optimize
          </button>
        )}
      </div>
    </div>
  );
};

export default StatCard;
