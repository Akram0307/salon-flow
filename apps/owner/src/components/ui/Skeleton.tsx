/**
 * Salon Flow Owner Dashboard - Skeleton Component
 * Loading placeholder with shimmer animation
 */

import React from 'react';
import { cn } from '../../lib/utils';
import type { BaseComponentProps } from '../../types/design-system';

// ============================================
// Skeleton Component Types
// ============================================
export interface SkeletonProps extends BaseComponentProps {
  width?: string | number;
  height?: string | number;
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'full';
  animate?: boolean;
}

export interface SkeletonTextProps extends BaseComponentProps {
  lines?: number;
  lineHeight?: 'sm' | 'md' | 'lg';
  lastLineWidth?: string;
}

export interface SkeletonAvatarProps extends BaseComponentProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  shape?: 'circle' | 'square';
}

export interface SkeletonCardProps extends BaseComponentProps {
  lines?: number;
  showHeader?: boolean;
  showFooter?: boolean;
}

// ============================================
// Style Variants
// ============================================
const roundedStyles: Record<string, string> = {
  none: 'rounded-none',
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',
  full: 'rounded-full',
};

const avatarSizeStyles: Record<string, string> = {
  xs: 'w-6 h-6',
  sm: 'w-8 h-8',
  md: 'w-10 h-10',
  lg: 'w-12 h-12',
  xl: 'w-16 h-16',
};

const lineHeightStyles: Record<string, string> = {
  sm: 'h-3',
  md: 'h-4',
  lg: 'h-5',
};

// ============================================
// Skeleton Component
// ============================================
export const Skeleton: React.FC<SkeletonProps> = ({
  width,
  height,
  rounded = 'md',
  animate = true,
  className,
  style,
}) => {
  return (
    <div
      className={cn(
        'bg-surface-200 dark:bg-surface-700',
        roundedStyles[rounded],
        animate && 'animate-shimmer bg-gradient-to-r from-surface-200 via-surface-100 to-surface-200 dark:from-surface-700 dark:via-surface-600 dark:to-surface-700 bg-[length:200%_100%]',
        className
      )}
      style={{
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
        ...style,
      }}
      aria-hidden="true"
    />
  );
};

// ============================================
// Skeleton Text Component
// ============================================
export const SkeletonText: React.FC<SkeletonTextProps> = ({
  lines = 3,
  lineHeight = 'md',
  lastLineWidth = '60%',
  className,
}) => {
  return (
    <div className={cn('space-y-2', className)} aria-hidden="true">
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          width={index === lines - 1 ? lastLineWidth : '100%'}
          rounded="sm"
          className={lineHeightStyles[lineHeight]}
        />
      ))}
    </div>
  );
};

// ============================================
// Skeleton Avatar Component
// ============================================
export const SkeletonAvatar: React.FC<SkeletonAvatarProps> = ({
  size = 'md',
  shape = 'circle',
  className,
}) => {
  return (
    <Skeleton
      className={cn(
        avatarSizeStyles[size],
        shape === 'circle' ? 'rounded-full' : 'rounded-lg',
        className
      )}
    />
  );
};

// ============================================
// Skeleton Card Component
// ============================================
export const SkeletonCard: React.FC<SkeletonCardProps> = ({
  lines = 3,
  showHeader = true,
  showFooter = false,
  className,
}) => {
  return (
    <div
      className={cn(
        'bg-white dark:bg-surface-800 rounded-xl border border-surface-200 dark:border-surface-700',
        className
      )}
      aria-hidden="true"
    >
      {showHeader && (
        <div className="px-4 py-3 border-b border-surface-100 dark:border-surface-700 flex items-center gap-3">
          <SkeletonAvatar size="sm" />
          <div className="flex-1 space-y-2">
            <Skeleton width="40%" height={14} rounded="sm" />
            <Skeleton width="60%" height={12} rounded="sm" />
          </div>
        </div>
      )}
      <div className="p-4">
        <SkeletonText lines={lines} />
      </div>
      {showFooter && (
        <div className="px-4 py-3 border-t border-surface-100 dark:border-surface-700 flex justify-end gap-2">
          <Skeleton width={80} height={32} rounded="lg" />
          <Skeleton width={80} height={32} rounded="lg" />
        </div>
      )}
    </div>
  );
};

// ============================================
// Skeleton Stat Card Component
// ============================================
export const SkeletonStatCard: React.FC<BaseComponentProps> = ({ className }) => {
  return (
    <div
      className={cn(
        'bg-white dark:bg-surface-800 rounded-xl border border-surface-200 dark:border-surface-700 p-5',
        className
      )}
      aria-hidden="true"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 space-y-3">
          <Skeleton width="40%" height={14} rounded="sm" />
          <Skeleton width="60%" height={32} rounded="sm" />
          <Skeleton width="30%" height={20} rounded="full" />
        </div>
        <Skeleton width={48} height={48} rounded="xl" />
      </div>
    </div>
  );
};

// ============================================
// Skeleton Table Component
// ============================================
export interface SkeletonTableProps extends BaseComponentProps {
  rows?: number;
  columns?: number;
  showHeader?: boolean;
}

export const SkeletonTable: React.FC<SkeletonTableProps> = ({
  rows = 5,
  columns = 4,
  showHeader = true,
  className,
}) => {
  return (
    <div className={cn('overflow-hidden', className)} aria-hidden="true">
      <table className="w-full">
        {showHeader && (
          <thead className="bg-surface-50 dark:bg-surface-800/50">
            <tr>
              {Array.from({ length: columns }).map((_, index) => (
                <th key={index} className="px-4 py-3">
                  <Skeleton width="60%" height={14} rounded="sm" />
                </th>
              ))}
            </tr>
          </thead>
        )}
        <tbody>
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <tr key={rowIndex} className="border-b border-surface-100 dark:border-surface-700">
              {Array.from({ length: columns }).map((_, colIndex) => (
                <td key={colIndex} className="px-4 py-3">
                  <Skeleton
                    width={colIndex === 0 ? '80%' : '60%'}
                    height={14}
                    rounded="sm"
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// ============================================
// Skeleton List Component
// ============================================
export interface SkeletonListProps extends BaseComponentProps {
  items?: number;
  showAvatar?: boolean;
}

export const SkeletonList: React.FC<SkeletonListProps> = ({
  items = 5,
  showAvatar = true,
  className,
}) => {
  return (
    <div className={cn('space-y-3', className)} aria-hidden="true">
      {Array.from({ length: items }).map((_, index) => (
        <div
          key={index}
          className="flex items-center gap-3 p-3 bg-white dark:bg-surface-800 rounded-lg border border-surface-200 dark:border-surface-700"
        >
          {showAvatar && <SkeletonAvatar size="md" />}
          <div className="flex-1 space-y-2">
            <Skeleton width="40%" height={14} rounded="sm" />
            <Skeleton width="70%" height={12} rounded="sm" />
          </div>
          <Skeleton width={60} height={28} rounded="lg" />
        </div>
      ))}
    </div>
  );
};

export default Skeleton;
