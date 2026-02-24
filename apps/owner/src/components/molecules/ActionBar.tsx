/**
 * Salon Flow Owner PWA - ActionBar Molecule
 * Bottom action buttons with primary + secondary actions
 * Full-width on mobile with sticky positioning support
 */

import React from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/atoms';

// ============================================
// Types
// ============================================
export interface ActionConfig {
  label: string;
  onPress: () => void;
  icon?: React.ReactNode;
  loading?: boolean;
  disabled?: boolean;
}

export interface ActionBarProps {
  primaryAction: ActionConfig;
  secondaryAction?: ActionConfig;
  sticky?: boolean;
  className?: string;
  safeArea?: boolean;
  variant?: 'default' | 'minimal' | 'stacked';
}

// ============================================
// ActionBar Component
// ============================================
export const ActionBar: React.FC<ActionBarProps> = ({
  primaryAction,
  secondaryAction,
  sticky = false,
  className,
  safeArea = true,
  variant = 'default',
}) => {
  if (variant === 'stacked') {
    return (
      <div
        className={cn(
          'w-full px-4 py-4 space-y-3',
          'bg-white dark:bg-surface-900',
          'border-t border-surface-200 dark:border-surface-800',
          sticky && 'sticky bottom-0 z-50',
          safeArea && 'pb-[calc(1rem+env(safe-area-inset-bottom))]',
          className
        )}
      >
        {/* Primary Action - Full Width */}
        <Button
          variant="primary"
          size="lg"
          fullWidth
          loading={primaryAction.loading}
          disabled={primaryAction.disabled}
          leftIcon={primaryAction.icon}
          onClick={primaryAction.onPress}
          className="min-h-[48px]"
        >
          {primaryAction.label}
        </Button>

        {/* Secondary Action - Full Width */}
        {secondaryAction && (
          <Button
            variant="ghost"
            size="lg"
            fullWidth
            loading={secondaryAction.loading}
            disabled={secondaryAction.disabled}
            leftIcon={secondaryAction.icon}
            onClick={secondaryAction.onPress}
            className="min-h-[48px]"
          >
            {secondaryAction.label}
          </Button>
        )}
      </div>
    );
  }

  if (variant === 'minimal') {
    return (
      <div
        className={cn(
          'w-full px-4 py-3',
          sticky && 'sticky bottom-0 z-50',
          safeArea && 'pb-[env(safe-area-inset-bottom)]',
          className
        )}
      >
        <div className="flex items-center justify-end gap-3">
          {secondaryAction && (
            <Button
              variant="ghost"
              size="md"
              loading={secondaryAction.loading}
              disabled={secondaryAction.disabled}
              leftIcon={secondaryAction.icon}
              onClick={secondaryAction.onPress}
              className="min-h-[44px]"
            >
              {secondaryAction.label}
            </Button>
          )}
          <Button
            variant="primary"
            size="md"
            loading={primaryAction.loading}
            disabled={primaryAction.disabled}
            leftIcon={primaryAction.icon}
            onClick={primaryAction.onPress}
            className="min-h-[44px]"
          >
            {primaryAction.label}
          </Button>
        </div>
      </div>
    );
  }

  // Default variant - Side by side on mobile
  return (
    <div
      className={cn(
        'w-full px-4 py-4',
        'bg-white dark:bg-surface-900',
        'border-t border-surface-200 dark:border-surface-800',
        sticky && 'sticky bottom-0 z-50',
        safeArea && 'pb-[calc(1rem+env(safe-area-inset-bottom))]',
        className
      )}
    >
      <div className="flex items-center gap-3">
        {/* Secondary Action */}
        {secondaryAction ? (
          <Button
            variant="outline"
            size="lg"
            loading={secondaryAction.loading}
            disabled={secondaryAction.disabled}
            leftIcon={secondaryAction.icon}
            onClick={secondaryAction.onPress}
            className="flex-1 min-h-[48px]"
          >
            {secondaryAction.label}
          </Button>
        ) : null}

        {/* Primary Action */}
        <Button
          variant="primary"
          size="lg"
          fullWidth={!secondaryAction}
          className={cn('min-h-[48px]', secondaryAction && 'flex-[2]')}
          loading={primaryAction.loading}
          disabled={primaryAction.disabled}
          leftIcon={primaryAction.icon}
          onClick={primaryAction.onPress}
        >
          {primaryAction.label}
        </Button>
      </div>
    </div>
  );
};

export default ActionBar;
