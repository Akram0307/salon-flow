/**
 * Salon Flow Owner PWA - Avatar Atom Component
 * Circular image with fallback initials and gradient placeholder
 */

import React, { useState } from 'react';
import { cn, getInitials } from '@/lib/utils';
import type { BaseComponentProps } from '@/types/design-system';

// ============================================
// Types
// ============================================
export type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface AvatarProps extends BaseComponentProps {
  src?: string;
  alt: string;
  size?: AvatarSize;
  fallback?: string;
}

// ============================================
// Style Variants
// ============================================
const sizeStyles: Record<AvatarSize, string> = {
  xs: 'w-6 h-6 text-xs',
  sm: 'w-8 h-8 text-sm',
  md: 'w-10 h-10 text-base',
  lg: 'w-12 h-12 text-lg',
  xl: 'w-16 h-16 text-xl',
};

const gradientStyles = [
  'bg-gradient-to-br from-primary-400 to-primary-600',
  'bg-gradient-to-br from-secondary-400 to-secondary-600',
  'bg-gradient-to-br from-accent-400 to-accent-600',
  'bg-gradient-to-br from-success-400 to-success-600',
  'bg-gradient-to-br from-warning-400 to-warning-600',
  'bg-gradient-to-br from-info-400 to-info-600',
];

// ============================================
// Get gradient based on name
// ============================================
function getGradientIndex(name: string): number {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return Math.abs(hash) % gradientStyles.length;
}

// ============================================
// Avatar Component
// ============================================
export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt,
  size = 'md',
  fallback,
  className,
  ...props
}) => {
  const [hasError, setHasError] = useState(false);
  const initials = fallback ? getInitials(fallback) : getInitials(alt);
  const gradientClass = gradientStyles[getGradientIndex(fallback || alt)];

  const showImage = src && !hasError;

  return (
    <div
      className={cn(
        // Base styles
        'relative inline-flex items-center justify-center',
        'rounded-full overflow-hidden',
        'flex-shrink-0',
        // Size styles
        sizeStyles[size],
        // Gradient background
        !showImage && gradientClass,
        // Custom className
        className
      )}
      {...props}
    >
      {showImage ? (
        <img
          src={src}
          alt={alt}
          className="w-full h-full object-cover"
          onError={() => setHasError(true)}
        />
      ) : (
        <span className="font-semibold text-white select-none">
          {initials}
        </span>
      )}
    </div>
  );
};

// Avatar Group Component
export interface AvatarGroupProps extends BaseComponentProps {
  max?: number;
  spacing?: 'tight' | 'normal' | 'loose';
}

export const AvatarGroup: React.FC<AvatarGroupProps> = ({
  max = 4,
  spacing = 'normal',
  className,
  children,
  ...props
}) => {
  const childrenArray = React.Children.toArray(children);
  const visibleChildren = childrenArray.slice(0, max);
  const remainingCount = childrenArray.length - max;

  const spacingStyles = {
    tight: '-space-x-2',
    normal: '-space-x-3',
    loose: '-space-x-4',
  };

  return (
    <div
      className={cn(
        'inline-flex items-center',
        spacingStyles[spacing],
        className
      )}
      {...props}
    >
      {visibleChildren.map((child, index) => (
        <div key={index} className="ring-2 ring-white dark:ring-surface-800 rounded-full">
          {child}
        </div>
      ))}
      {remainingCount > 0 && (
        <div
          className={cn(
            'relative inline-flex items-center justify-center rounded-full',
            'bg-surface-200 dark:bg-surface-700 text-surface-600 dark:text-surface-300',
            'font-medium ring-2 ring-white dark:ring-surface-800',
            sizeStyles.md
          )}
        >
          +{remainingCount}
        </div>
      )}
    </div>
  );
};

export default Avatar;
