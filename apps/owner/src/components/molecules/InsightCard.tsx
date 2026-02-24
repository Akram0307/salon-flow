/**
 * Salon Flow Owner PWA - InsightCard Molecule
 * AI insight display with lightbulb icon, text, confidence, and action button
 */

import React from 'react';
import { Lightbulb, X, Sparkles, TrendingUp, AlertTriangle, Info, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card } from '@/components/atoms';

// ============================================
// Types
// ============================================
export type InsightType = 'optimization' | 'warning' | 'trend' | 'opportunity' | 'info';

export interface Insight {
  id: string;
  text: string;
  type: InsightType;
  confidence: number; // 0-100
  metric?: string;
  metricValue?: string;
  actionLabel?: string;
}

export interface InsightCardProps {
  insight: Insight;
  onAction?: (insight: Insight) => void;
  onDismiss?: (insight: Insight) => void;
  className?: string;
  compact?: boolean;
}

// ============================================
// InsightCard Component
// ============================================
export const InsightCard: React.FC<InsightCardProps> = ({
  insight,
  onAction,
  onDismiss,
  className,
  
}) => {
  const typeConfig: Record<InsightType, { 
    icon: React.ElementType; 
    gradient: string; 
    border: string;
    label: string;
  }> = {
    optimization: {
      icon: Sparkles,
      gradient: 'from-primary-500/20 to-primary-600/10',
      border: 'border-primary-200 dark:border-primary-800',
      label: 'Optimization',
    },
    warning: {
      icon: AlertTriangle,
      gradient: 'from-warning-500/20 to-warning-600/10',
      border: 'border-warning-200 dark:border-warning-800',
      label: 'Warning',
    },
    trend: {
      icon: TrendingUp,
      gradient: 'from-success-500/20 to-success-600/10',
      border: 'border-success-200 dark:border-success-800',
      label: 'Trend',
    },
    opportunity: {
      icon: Lightbulb,
      gradient: 'from-secondary-500/20 to-secondary-600/10',
      border: 'border-secondary-200 dark:border-secondary-800',
      label: 'Opportunity',
    },
    info: {
      icon: Info,
      gradient: 'from-info-500/20 to-info-600/10',
      border: 'border-info-200 dark:border-info-800',
      label: 'Info',
    },
  };

  const config = typeConfig[insight.type];
  const Icon = config.icon;

  const getConfidenceLabel = (score: number) => {
    if (score >= 90) return 'Very High';
    if (score >= 70) return 'High';
    if (score >= 50) return 'Medium';
    return 'Low';
  };

  return (
    <Card
      className={cn(
        'relative overflow-hidden',
        'bg-gradient-to-br',
        config.gradient,
        config.border,
        'border',
        className
      )}
    >
      {/* Dismiss Button */}
      {onDismiss && (
        <button
          type="button"
          onClick={() => onDismiss(insight)}
          className={cn(
            'absolute top-2 right-2 p-1 rounded-full',
            'text-surface-400 hover:text-surface-600',
            'dark:text-surface-500 dark:hover:text-surface-300',
            'hover:bg-white/50 dark:hover:bg-black/20',
            'transition-colors duration-200'
          )}
          aria-label="Dismiss insight"
        >
          <X className="w-4 h-4" />
        </button>
      )}

      <div className="flex gap-3">
        {/* Icon */}
        <div
          className={cn(
            'flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center',
            'bg-white/60 dark:bg-black/20',
            insight.type === 'optimization' && 'text-primary-600 dark:text-primary-400',
            insight.type === 'warning' && 'text-warning-600 dark:text-warning-400',
            insight.type === 'trend' && 'text-success-600 dark:text-success-400',
            insight.type === 'opportunity' && 'text-secondary-600 dark:text-secondary-400',
            insight.type === 'info' && 'text-info-600 dark:text-info-400'
          )}
        >
          <Icon className="w-5 h-5" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Type Badge */}
          <div className="flex items-center gap-2 mb-1">
            <span
              className={cn(
                'text-xs font-medium uppercase tracking-wide',
                insight.type === 'optimization' && 'text-primary-700 dark:text-primary-300',
                insight.type === 'warning' && 'text-warning-700 dark:text-warning-300',
                insight.type === 'trend' && 'text-success-700 dark:text-success-300',
                insight.type === 'opportunity' && 'text-secondary-700 dark:text-secondary-300',
                insight.type === 'info' && 'text-info-700 dark:text-info-300'
              )}
            >
              {config.label}
            </span>
            {/* Confidence Score */}
            <span className="text-xs text-surface-400 dark:text-surface-500">
              {getConfidenceLabel(insight.confidence)} confidence
            </span>
          </div>

          {/* Insight Text */}
          <p className="text-sm text-surface-700 dark:text-surface-200 leading-relaxed">
            {insight.text}
          </p>

          {/* Metric */}
          {insight.metric && insight.metricValue && (
            <div className="mt-2 flex items-center gap-2">
              <span className="text-xs text-surface-500 dark:text-surface-400">
                {insight.metric}:
              </span>
              <span className="text-sm font-semibold text-surface-900 dark:text-white">
                {insight.metricValue}
              </span>
            </div>
          )}

          {/* Action Button */}
          {onAction && (
            <button
              type="button"
              onClick={() => onAction(insight)}
              className={cn(
                'mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium',
                'bg-white dark:bg-surface-800',
                'text-primary-700 dark:text-primary-300',
                'hover:bg-surface-50 dark:hover:bg-surface-700',
                'border border-surface-200 dark:border-surface-700',
                'transition-colors duration-200',
                'min-h-[36px]'
              )}
            >
              {insight.actionLabel || 'Take Action'}
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </Card>
  );
};

export default InsightCard;
