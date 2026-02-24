/**
 * Divider Component
 * 
 * Visual separator for content sections.
 * 
 * @example
 * <Divider /> // Horizontal solid
 * <Divider variant="dashed" /> // Horizontal dashed
 * <Divider orientation="vertical" className="h-20" /> // Vertical
 * <Divider>OR</Divider> // With label
 */

import React from 'react';
import { cn } from '@/lib/utils';

export type DividerVariant = 'solid' | 'dashed' | 'dotted';
export type DividerOrientation = 'horizontal' | 'vertical';

export interface DividerProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'style'> {
  variant?: DividerVariant;
  orientation?: DividerOrientation;
  thickness?: 'thin' | 'medium' | 'thick';
}

const thicknessClasses = {
  thin: 'border-surface-200 dark:border-surface-700',
  medium: 'border-surface-300 dark:border-surface-600',
  thick: 'border-surface-400 dark:border-surface-500',
};

const variantClasses: Record<DividerVariant, string> = {
  solid: 'border-solid',
  dashed: 'border-dashed',
  dotted: 'border-dotted',
};

export const Divider: React.FC<DividerProps> = ({
  variant = 'solid',
  orientation = 'horizontal',
  thickness = 'thin',
  className,
  ...props
}) => {
  return (
    <div
      className={cn(
        'flex items-center',
        orientation === 'horizontal' 
          ? 'w-full border-t' 
          : 'h-full border-l',
        thicknessClasses[thickness],
        variantClasses[variant],
        className
      )}
      {...props}
    />
  );
};

export default Divider;
