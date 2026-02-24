/**
 * Salon Flow Owner Dashboard - ActivityFeed Component
 * Real-time activity stream with filtering and actions
 */

import React, { forwardRef } from 'react';
import { cn } from '../../lib/utils';
import { Avatar } from '../ui/Avatar';
import type { BaseComponentProps } from '../../types/design-system';

// ============================================
// ActivityFeed Types
// ============================================
export interface ActivityItem {
  id: string;
  type: 'booking' | 'payment' | 'customer' | 'staff' | 'ai' | 'system';
  title: string;
  description?: string;
  timestamp: Date | string;
  user?: {
    name: string;
    avatar?: string;
  };
  metadata?: Record<string, any>;
  actionable?: boolean;
  actionLabel?: string;
  onAction?: () => void;
}

export interface ActivityFeedProps extends BaseComponentProps {
  activities: ActivityItem[];
  maxItems?: number;
  showTimestamp?: boolean;
  groupByDate?: boolean;
  emptyMessage?: string;
  onLoadMore?: () => void;
  hasMore?: boolean;
  loading?: boolean;
}

// ============================================
// Activity Icon Styles
// ============================================
const activityIconConfig: Record<string, { icon: React.ReactNode; color: string }> = {
  booking: {
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
    color: 'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400',
  },
  payment: {
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    color: 'bg-success-100 text-success-600 dark:bg-success-900/30 dark:text-success-400',
  },
  customer: {
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    ),
    color: 'bg-secondary-100 text-secondary-600 dark:bg-secondary-900/30 dark:text-secondary-400',
  },
  staff: {
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
    color: 'bg-accent-100 text-accent-600 dark:bg-accent-900/30 dark:text-accent-400',
  },
  ai: {
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    color: 'bg-gradient-to-br from-primary-100 to-accent-100 text-primary-600 dark:from-primary-900/30 dark:to-accent-900/30 dark:text-primary-400',
  },
  system: {
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
    color: 'bg-surface-100 text-surface-600 dark:bg-surface-700 dark:text-surface-400',
  },
};

// ============================================
// Time Formatting Utility
// ============================================
const formatRelativeTime = (timestamp: Date | string): string => {
  const now = new Date();
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
};

// ============================================
// ActivityItem Component
// ============================================
const ActivityItemComponent: React.FC<{ activity: ActivityItem; showTimestamp: boolean }> = ({
  activity,
  showTimestamp,
}) => {
  const config = activityIconConfig[activity.type];

  return (
    <div className="flex gap-3 p-3 hover:bg-surface-50 dark:hover:bg-surface-700/50 rounded-lg transition-colors">
      {/* Icon */}
      <div className={cn('flex-shrink-0 p-2 rounded-lg', config.color)}>
        {config.icon}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="text-sm font-medium text-surface-900 dark:text-white truncate">
              {activity.title}
            </p>
            {activity.description && (
              <p className="mt-0.5 text-xs text-surface-500 dark:text-surface-400 line-clamp-2">
                {activity.description}
              </p>
            )}
          </div>
          {showTimestamp && (
            <span className="flex-shrink-0 text-xs text-surface-400 dark:text-surface-500">
              {formatRelativeTime(activity.timestamp)}
            </span>
          )}
        </div>

        {/* User & Action */}
        <div className="mt-2 flex items-center justify-between">
          {activity.user && (
            <div className="flex items-center gap-2">
              <Avatar name={activity.user.name} src={activity.user.avatar} size="xs" />
              <span className="text-xs text-surface-500 dark:text-surface-400">
                {activity.user.name}
              </span>
            </div>
          )}
          {activity.actionable && activity.actionLabel && (
            <button
              onClick={activity.onAction}
              className="text-xs font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
            >
              {activity.actionLabel}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

// ============================================
// ActivityFeed Component
// ============================================
export const ActivityFeed = forwardRef<HTMLDivElement, ActivityFeedProps>(
  (
    {
      activities,
      maxItems = 10,
      showTimestamp = true,
      groupByDate: _groupByDate = false,
      emptyMessage = 'No recent activity',
      onLoadMore,
      hasMore = false,
      loading = false,
      className,
    },
    ref
  ) => {
    const displayedActivities = activities.slice(0, maxItems);

    if (displayedActivities.length === 0 && !loading) {
      return (
        <div ref={ref} className={cn('text-center py-8', className)}>
          <svg
            className="mx-auto w-12 h-12 text-surface-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
            />
          </svg>
          <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">{emptyMessage}</p>
        </div>
      );
    }

    return (
      <div ref={ref} className={cn('space-y-1', className)}>
        {displayedActivities.map((activity) => (
          <ActivityItemComponent
            key={activity.id}
            activity={activity}
            showTimestamp={showTimestamp}
          />
        ))}

        {/* Load More */}
        {hasMore && (
          <button
            onClick={onLoadMore}
            disabled={loading}
            className="w-full py-2 text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Load more'}
          </button>
        )}
      </div>
    );
  }
);

ActivityFeed.displayName = 'ActivityFeed';

export default ActivityFeed;
