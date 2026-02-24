/**
 * MobileFrame Component
 * 
 * Mobile viewport wrapper that simulates a mobile device frame
 * for development and provides proper viewport constraints.
 * 
 * Features:
 * - Max-width constraint for mobile viewport
 * - Centered layout with shadow on larger screens
 * - Safe area support
 * - Scrollable content area
 * 
 * @example
 * <MobileFrame>
 *   <AppContent />
 * </MobileFrame>
 */

import React from 'react';
import { cn } from '@/lib/utils';
import { SafeArea } from './SafeArea';

interface MobileFrameProps {
  children: React.ReactNode;
  className?: string;
  showFrame?: boolean;
}

export const MobileFrame: React.FC<MobileFrameProps> = ({
  children,
  className,
  showFrame = true,
}) => {
  return (
    <div
      className={cn(
        'min-h-screen w-full bg-surface-100 dark:bg-surface-900',
        'flex items-start justify-center',
        className
      )}
    >
      <div
        className={cn(
          'w-full min-h-screen bg-white dark:bg-surface-900',
          'flex flex-col relative',
          // Mobile viewport constraints
          'max-w-md',
          // Frame styling for larger screens
          showFrame && [
            'sm:min-h-[800px] sm:h-auto sm:my-8',
            'sm:rounded-[2.5rem] sm:shadow-2xl',
            'sm:border-8 sm:border-surface-800',
            'sm:overflow-hidden',
          ]
        )}
      >
        <SafeArea top bottom className="flex-1 flex flex-col">
          {children}
        </SafeArea>
      </div>
    </div>
  );
};

export default MobileFrame;
