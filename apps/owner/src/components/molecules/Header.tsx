/**
 * Header Component
 * 
 * Mobile-optimized app header with title, back button,
 * and action buttons. Supports sticky positioning.
 * 
 * @example
 * <Header 
 *   title="Dashboard" 
 *   showBack 
 *   onBack={() => navigate(-1)}
 *   rightActions={[<IconButton key="search" icon={Search} />]}
 * />
 */

import React from 'react';
import { ChevronLeft } from 'lucide-react';
import { cn } from '@/lib/utils';

interface HeaderProps {
  title: string;
  subtitle?: string;
  showBack?: boolean;
  onBack?: () => void;
  rightActions?: React.ReactNode[];
  className?: string;
  sticky?: boolean;
  transparent?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  showBack = false,
  onBack,
  rightActions,
  className,
  sticky = true,
  transparent = false,
}) => {
  return (
    <header
      className={cn(
        'w-full px-4 py-3 flex items-center justify-between',
        'border-b border-surface-200 dark:border-surface-700',
        sticky && 'sticky top-0 z-50',
        transparent 
          ? 'bg-transparent' 
          : 'bg-white dark:bg-surface-900',
        className
      )}
    >
      {/* Left Section */}
      <div className="flex items-center gap-3 flex-1 min-w-0">
        {showBack && (
          <button
            onClick={onBack}
            className={cn(
              'p-2 -ml-2 rounded-full',
              'hover:bg-surface-100 dark:hover:bg-surface-800',
              'transition-colors duration-200',
              'text-surface-700 dark:text-surface-300'
            )}
            aria-label="Go back"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
        )}
        
        <div className="flex flex-col min-w-0">
          <h1 
            className={cn(
              'text-lg font-semibold truncate',
              'text-surface-900 dark:text-white'
            )}
          >
            {title}
          </h1>
          {subtitle && (
            <span className="text-xs text-surface-500 dark:text-surface-400 truncate">
              {subtitle}
            </span>
          )}
        </div>
      </div>

      {/* Right Actions */}
      {rightActions && rightActions.length > 0 && (
        <div className="flex items-center gap-1">
          {rightActions.map((action, index) => (
            <div key={index}>{action}</div>
          ))}
        </div>
      )}
    </header>
  );
};

export default Header;
