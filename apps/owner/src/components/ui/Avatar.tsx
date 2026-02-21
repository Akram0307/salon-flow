/**
 * Salon Flow Owner Dashboard - Avatar Component
 * Professional avatar with multiple sizes and states
 */

import React, { forwardRef, useState } from 'react';
import { cn, getInitials } from '../../lib/utils';
import type { AvatarSize, BaseComponentProps } from '../../types/design-system';

// ============================================
// Avatar Component Types
// ============================================
export interface AvatarProps extends BaseComponentProps, React.ImgHTMLAttributes<HTMLImageElement> {
  size?: AvatarSize;
  name?: string;
  src?: string;
  fallback?: string;
  status?: 'online' | 'offline' | 'busy' | 'away';
  shape?: 'circle' | 'square';
}

export interface AvatarGroupProps extends BaseComponentProps {
  max?: number;
  size?: AvatarSize;
  children: React.ReactNode;
}

// ============================================
// Style Variants
// ============================================
const sizeStyles: Record<AvatarSize, string> = {
  xs: 'w-6 h-6 text-xs',
  sm: 'w-8 h-8 text-sm',
  md: 'w-10 h-10 text-sm',
  lg: 'w-12 h-12 text-base',
  xl: 'w-16 h-16 text-lg',
  '2xl': 'w-20 h-20 text-xl',
};

const statusStyles: Record<string, string> = {
  online: 'bg-success-500',
  offline: 'bg-surface-400',
  busy: 'bg-error-500',
  away: 'bg-warning-500',
};

const statusSizeStyles: Record<AvatarSize, string> = {
  xs: 'w-1.5 h-1.5',
  sm: 'w-2 h-2',
  md: 'w-2.5 h-2.5',
  lg: 'w-3 h-3',
  xl: 'w-3.5 h-3.5',
  '2xl': 'w-4 h-4',
};

// ============================================
// Avatar Component
// ============================================
export const Avatar = forwardRef<HTMLImageElement, AvatarProps>(
  (
    {
      size = 'md',
      name,
      src,
      fallback,
      status,
      shape = 'circle',
      className,
      alt,
      ...props
    },
    ref
  ) => {
    const [imageError, setImageError] = useState(false);
    const initials = name ? getInitials(name) : fallback || '?';

    const showFallback = !src || imageError;

    return (
      <div className={cn('relative inline-flex', className)}>
        {showFallback ? (
          <div
            className={cn(
              'inline-flex items-center justify-center',
              'bg-gradient-to-br from-primary-400 to-primary-600',
              'text-white font-medium',
              shape === 'circle' ? 'rounded-full' : 'rounded-lg',
              sizeStyles[size]
            )}
            role="img"
            aria-label={alt || name || 'Avatar'}
          >
            {initials}
          </div>
        ) : (
          <img
            ref={ref}
            src={src}
            alt={alt || name || 'Avatar'}
            onError={() => setImageError(true)}
            className={cn(
              'object-cover',
              shape === 'circle' ? 'rounded-full' : 'rounded-lg',
              sizeStyles[size]
            )}
            {...props}
          />
        )}

        {/* Status Indicator */}
        {status && (
          <span
            className={cn(
              'absolute bottom-0 right-0 ring-2 ring-white dark:ring-surface-800 rounded-full',
              statusStyles[status],
              statusSizeStyles[size]
            )}
            aria-label={`Status: ${status}`}
          />
        )}
      </div>
    );
  }
);

Avatar.displayName = 'Avatar';

// ============================================
// Avatar Group Component
// ============================================
export const AvatarGroup: React.FC<AvatarGroupProps> = ({
  max = 4,
  size = 'md',
  className,
  children,
}) => {
  const childArray = React.Children.toArray(children);
  const visibleChildren = childArray.slice(0, max);
  const remainingCount = childArray.length - max;

  return (
    <div className={cn('flex -space-x-2', className)}>
      {visibleChildren.map((child, index) => (
        <div key={index} className="ring-2 ring-white dark:ring-surface-800 rounded-full">
          {React.isValidElement(child)
            ? React.cloneElement(child as React.ReactElement<AvatarProps>, { size })
            : child}
        </div>
      ))}
      {remainingCount > 0 && (
        <div
          className={cn(
            'inline-flex items-center justify-center',
            'bg-surface-200 dark:bg-surface-700',
            'text-surface-600 dark:text-surface-300 font-medium',
            'rounded-full ring-2 ring-white dark:ring-surface-800',
            sizeStyles[size]
          )}
        >
          +{remainingCount}
        </div>
      )}
    </div>
  );
};

export default Avatar;
