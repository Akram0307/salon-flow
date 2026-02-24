/**
 * Salon Flow Owner PWA - Icon Atom Component
 * Wrapper for Lucide icons with theme integration
 */

import React from 'react';
import { cn } from '@/lib/utils';
import type { BaseComponentProps } from '@/types/design-system';

// ============================================
// Types
// ============================================
export type IconSize = 16 | 20 | 24 | 32;
export type IconColor = 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'error' | 'info' | 'current' | 'muted';

export interface IconProps extends BaseComponentProps {
  name: string;
  size?: IconSize;
  color?: IconColor;
  strokeWidth?: number;
}

// ============================================
// Style Variants
// ============================================
const sizeStyles: Record<IconSize, string> = {
  16: 'w-4 h-4',
  20: 'w-5 h-5',
  24: 'w-6 h-6',
  32: 'w-8 h-8',
};

const colorStyles: Record<IconColor, string> = {
  primary: 'text-primary-600 dark:text-primary-400',
  secondary: 'text-secondary-600 dark:text-secondary-400',
  accent: 'text-accent-600 dark:text-accent-400',
  success: 'text-success-500 dark:text-success-400',
  warning: 'text-warning-500 dark:text-warning-400',
  error: 'text-error-500 dark:text-error-400',
  info: 'text-info-500 dark:text-info-400',
  current: 'text-current',
  muted: 'text-surface-400 dark:text-surface-500',
};

// ============================================
// Icon Component
// ============================================
export const Icon: React.FC<IconProps> = ({
  name,
  size = 20,
  color = 'current',
  strokeWidth = 2,
  className,
  ...props
}) => {
  // This component expects the parent to pass the actual Lucide icon element
  // Usage: <Icon name="User" size={24} color="primary" />
  // The icon element should be passed as children
  return (
    <span
      className={cn(
        'inline-flex items-center justify-center',
        sizeStyles[size],
        colorStyles[color],
        className
      )}
      {...props}
    >
      {/* 
        This is a wrapper component that works with Lucide icons.
        Usage with Lucide:
        import { User } from 'lucide-react';
        <IconWrapper size={24} color="primary"><User /></IconWrapper>
        
        Or use the icon map below for dynamic icons.
      */}
    </span>
  );
};

// Icon Wrapper for Lucide components
export interface IconWrapperProps extends Omit<IconProps, 'name'> {
  children: React.ReactElement;
}

export const IconWrapper: React.FC<IconWrapperProps> = ({
  children,
  size = 20,
  color = 'current',
  className,
}) => {
  return (
    <span
      className={cn(
        'inline-flex items-center justify-center flex-shrink-0',
        sizeStyles[size],
        colorStyles[color],
        className
      )}
    >
      {React.cloneElement(children, {
        className: 'w-full h-full',
      })}
    </span>
  );
};

// Helper to render icons with Lucide
export interface LucideIconProps extends IconProps {
  icon: React.ComponentType<{ className?: string; strokeWidth?: number }>;
}

export const LucideIcon: React.FC<LucideIconProps> = ({
  icon: IconComponent,
  size = 20,
  color = 'current',
  strokeWidth = 2,
  className,
}) => {
  return (
    <span
      className={cn(
        'inline-flex items-center justify-center flex-shrink-0',
        sizeStyles[size],
        colorStyles[color],
        className
      )}
    >
      <IconComponent className="w-full h-full" strokeWidth={strokeWidth} />
    </span>
  );
};

export default Icon;
