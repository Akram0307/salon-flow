/**
 * InsightsBar Component
 *
 * Global AI insights banner that displays proactive alerts and recommendations.
 * Appears at the top of the dashboard with actionable AI insights.
 *
 * Features:
 * - Dismissible banner with smooth animations
 * - Multiple insight types (info, warning, success, action)
 * - Action buttons for immediate response
 * - Auto-dismiss option
 *
 * @example
 * <InsightsBar
 *   insights={[{ type: 'warning', message: '3 gaps in today\'s schedule', action: 'Optimize' }]}
 *   onAction={handleAction}
 * />
 */

import React, { useState, useEffect } from 'react';
import { 
  X, 
  Lightbulb, 
  AlertTriangle, 
  CheckCircle, 
  Info,
  Sparkles,
  ChevronRight
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ============================================
// Types
// ============================================

export type InsightType = 'info' | 'warning' | 'success' | 'action' | 'ai';

export interface Insight {
  id: string;
  type: InsightType;
  message: string;
  detail?: string;
  action?: string;
  onAction?: () => void;
  dismissible?: boolean;
  autoDismiss?: number; // milliseconds
}

export interface InsightsBarProps {
  insights: Insight[];
  onDismiss?: (id: string) => void;
  className?: string;
  maxVisible?: number;
}

// ============================================
// Insight Type Styles
// ============================================

const insightStyles: Record<InsightType, {
  container: string;
  icon: React.ElementType;
  iconBg: string;
}> = {
  info: {
    container: 'bg-info-50 dark:bg-info-900/20 border-info-200 dark:border-info-800',
    icon: Info,
    iconBg: 'bg-info-100 dark:bg-info-800 text-info-600 dark:text-info-300',
  },
  warning: {
    container: 'bg-warning-50 dark:bg-warning-900/20 border-warning-200 dark:border-warning-800',
    icon: AlertTriangle,
    iconBg: 'bg-warning-100 dark:bg-warning-800 text-warning-600 dark:text-warning-300',
  },
  success: {
    container: 'bg-success-50 dark:bg-success-900/20 border-success-200 dark:border-success-800',
    icon: CheckCircle,
    iconBg: 'bg-success-100 dark:bg-success-800 text-success-600 dark:text-success-300',
  },
  action: {
    container: 'bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800',
    icon: Lightbulb,
    iconBg: 'bg-primary-100 dark:bg-primary-800 text-primary-600 dark:text-primary-300',
  },
  ai: {
    container: 'bg-gradient-to-r from-primary-50 to-accent-50 dark:from-primary-900/20 dark:to-accent-900/20 border-primary-200 dark:border-primary-800',
    icon: Sparkles,
    iconBg: 'bg-gradient-to-r from-primary-500 to-accent-500 text-white',
  },
};

// ============================================
// Single Insight Item
// ============================================

interface InsightItemProps {
  insight: Insight;
  onDismiss?: (id: string) => void;
  isExiting?: boolean;
}

const InsightItem: React.FC<InsightItemProps> = ({
  insight,
  onDismiss,
  isExiting,
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const styles = insightStyles[insight.type];
  const Icon = styles.icon;

  useEffect(() => {
    if (insight.autoDismiss) {
      const timer = setTimeout(() => {
        handleDismiss();
      }, insight.autoDismiss);
      return () => clearTimeout(timer);
    }
  }, [insight.autoDismiss]);

  const handleDismiss = () => {
    setIsVisible(false);
    setTimeout(() => {
      onDismiss?.(insight.id);
    }, 200);
  };

  if (!isVisible) return null;

  return (
    <div
      className={cn(
        'flex items-start gap-3 p-3 rounded-xl border',
        'transition-all duration-200',
        styles.container,
        isExiting && 'opacity-0 translate-y-2'
      )}
    >
      {/* Icon */}
      <div className={cn('w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0', styles.iconBg)}>
        <Icon className="w-4 h-4" />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-surface-900 dark:text-white">
          {insight.message}
        </p>
        {insight.detail && (
          <p className="text-xs text-surface-600 dark:text-surface-400 mt-0.5">
            {insight.detail}
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 flex-shrink-0">
        {insight.action && insight.onAction && (
          <button
            onClick={insight.onAction}
            className={cn(
              'flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium',
              'bg-white dark:bg-surface-800',
              'text-primary-700 dark:text-primary-300',
              'border border-primary-200 dark:border-primary-700',
              'hover:bg-primary-50 dark:hover:bg-primary-900/30',
              'transition-colors duration-200',
              'min-h-[32px]'
            )}
          >
            {insight.action}
            <ChevronRight className="w-3 h-3" />
          </button>
        )}
        {insight.dismissible !== false && (
          <button
            onClick={handleDismiss}
            className="p-1.5 rounded-lg text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
            aria-label="Dismiss"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};

// ============================================
// InsightsBar Component
// ============================================

export const InsightsBar: React.FC<InsightsBarProps> = ({
  insights,
  onDismiss,
  className,
  maxVisible = 3,
}) => {
  const [visibleInsights, setVisibleInsights] = useState(insights.slice(0, maxVisible));

  useEffect(() => {
    setVisibleInsights(insights.slice(0, maxVisible));
  }, [insights, maxVisible]);

  const handleDismiss = (id: string) => {
    setVisibleInsights(prev => prev.filter(i => i.id !== id));
    onDismiss?.(id);
  };

  if (visibleInsights.length === 0) return null;

  return (
    <div className={cn('space-y-2', className)}>
      {visibleInsights.map((insight) => (
        <InsightItem
          key={insight.id}
          insight={insight}
          onDismiss={handleDismiss}
        />
      ))}
    </div>
  );
};

export default InsightsBar;
