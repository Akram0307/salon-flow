/**
 * SafeArea Component
 * 
 * Handles safe area insets for mobile devices with notches,
 * home indicators, and status bars.
 * 
 * @example
 * <SafeArea top bottom>
 *   <Content />
 * </SafeArea>
 */

import React from 'react';
import { cn } from '@/lib/utils';

interface SafeAreaProps {
  children: React.ReactNode;
  top?: boolean;
  bottom?: boolean;
  left?: boolean;
  right?: boolean;
  className?: string;
}

export const SafeArea: React.FC<SafeAreaProps> = ({
  children,
  top = false,
  bottom = false,
  left = false,
  right = false,
  className,
}) => {
  return (
    <div
      className={cn(
        'w-full h-full',
        top && 'pt-[env(safe-area-inset-top)]',
        bottom && 'pb-[env(safe-area-inset-bottom)]',
        left && 'pl-[env(safe-area-inset-left)]',
        right && 'pr-[env(safe-area-inset-right)]',
        className
      )}
    >
      {children}
    </div>
  );
};

export default SafeArea;
