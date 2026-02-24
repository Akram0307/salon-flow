/**
 * Salon Flow Owner PWA - Skeleton Atom Component
 * Loading placeholders with pulse animation
 */

import React from 'react';
import { cn } from '@/lib/utils';
import type { BaseComponentProps } from '@/types/design-system';

// ============================================
// Types
// ============================================
export type SkeletonVariant = 'text' | 'circle' | 'rectangle' | 'rounded';
export type SkeletonSize = 'sm' | 'md' | 'lg';

export interface SkeletonProps extends BaseComponentProps {
  variant?: SkeletonVariant;
  size?: SkeletonSize;
  width?: string | number;
  height?: string | number;
}

// ============================================
// Style Variants
// ============================================
const variantStyles: Record<SkeletonVariant, string> = {
  text: 'rounded',
  circle: 'rounded-full',
  rectangle: 'rounded-lg',
  rounded: 'rounded-xl',
};


const defaultHeights: Record<SkeletonVariant, Record<SkeletonSize, string>> = {
  text: {
    sm: 'h-3',
    md: 'h-4',
    lg: 'h-6',
  },
  circle: {
    sm: 'h-8 w-8',
    md: 'h-12 w-12',
    lg: 'h-16 w-16',
  },
  rectangle: {
    sm: 'h-16',
    md: 'h-24',
    lg: 'h-32',
  },
  rounded: {
    sm: 'h-20',
    md: 'h-32',
    lg: 'h-48',
  },
};

// ============================================
// Skeleton Component
// ============================================
export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'text',
  size = 'md',
  width,
  height,
  className,
  style,
  ...props
}) => {
  const defaultHeight = defaultHeights[variant][size];

  return (
    <div
      className={cn(
        // Base styles
        'bg-surface-200 dark:bg-surface-700',
        'animate-pulse',
        // Variant styles
        variantStyles[variant],
        // Size styles (only if no custom dimensions)
        !width && !height && defaultHeight,
        // Custom className
        className
      )}
      style={{
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
        ...style,
      }}
      {...props}
    />
  );
};

// Skeleton Text Line Component
export interface SkeletonTextProps extends BaseComponentProps {
  lines?: number;
  size?: SkeletonSize;
  lastLineWidth?: string;
}

export const SkeletonText: React.FC<SkeletonTextProps> = ({
  lines = 3,
  size = 'md',
  lastLineWidth = '60%',
  className,
}) => {
  return (
    <div className={cn('space-y-2', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          variant="text"
          size={size}
          className={i === lines - 1 ? `w-[${lastLineWidth}]` : 'w-full'}
        />
      ))}
    </div>
  );
};

// Skeleton Card Component
export interface SkeletonCardProps extends BaseComponentProps {
  hasHeader?: boolean;
  hasFooter?: boolean;
  contentLines?: number;
}

export const SkeletonCard: React.FC<SkeletonCardProps> = ({
  hasHeader = true,
  hasFooter = true,
  contentLines = 3,
  className,
}) => {
  return (
    <div
      className={cn(
        'p-4 rounded-xl border border-surface-200 dark:border-surface-700',
        'bg-white dark:bg-surface-800',
        'space-y-4',
        className
      )}
    >
      {hasHeader && (
        <div className="flex items-center space-x-3">
          <Skeleton variant="circle" size="sm" />
          <div className="flex-1 space-y-2">
            <Skeleton variant="text" size="sm" className="w-1/3" />
            <Skeleton variant="text" size="sm" className="w-1/4" />
          </div>
        </div>
      )}
      <SkeletonText lines={contentLines} size="sm" />
      {hasFooter && (
        <div className="flex items-center justify-between pt-2">
          <Skeleton variant="text" size="sm" className="w-20" />
          <Skeleton variant="text" size="sm" className="w-16" />
        </div>
      )}
    </div>
  );
};

export default Skeleton;
