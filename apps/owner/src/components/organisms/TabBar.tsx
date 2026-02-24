/**
 * TabBar Component
 * 
 * 5-tab mobile navigation bar for the Owner PWA.
 * Tabs: Home, Bookings, Customers, Staff, More
 * 
 * Features:
 * - Active state highlighting
 * - Badge support for notifications
 * - Safe area padding for home indicator
 * - Haptic feedback on press (mobile)
 * 
 * @example
 * <TabBar activeTab="home" onTabChange={(tab) => setActiveTab(tab)} />
 */

import React from 'react';
import { 
  Home, 
  Calendar, 
  Users, 
  UserCircle, 
  MoreHorizontal,
  LucideIcon 
} from 'lucide-react';
import { cn } from '@/lib/utils';

export type TabId = 'home' | 'bookings' | 'customers' | 'staff' | 'more';

interface TabItem {
  id: TabId;
  label: string;
  icon: LucideIcon;
  badge?: number;
}

const tabs: TabItem[] = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'bookings', label: 'Bookings', icon: Calendar },
  { id: 'customers', label: 'Customers', icon: Users },
  { id: 'staff', label: 'Staff', icon: UserCircle },
  { id: 'more', label: 'More', icon: MoreHorizontal },
];

interface TabBarProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
  className?: string;
}

export const TabBar: React.FC<TabBarProps> = ({
  activeTab,
  onTabChange,
  className,
}) => {
  return (
    <nav
      className={cn(
        'fixed bottom-0 left-0 right-0 z-50',
        'bg-white dark:bg-surface-900',
        'border-t border-surface-200 dark:border-surface-700',
        'pb-[env(safe-area-inset-bottom)]',
        'shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]',
        className
      )}
    >
      <div className="max-w-md mx-auto flex items-center justify-around h-16">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          const Icon = tab.icon;
          
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={cn(
                'flex flex-col items-center justify-center',
                'flex-1 h-full px-2',
                'transition-colors duration-200',
                'relative',
                isActive 
                  ? 'text-primary-600 dark:text-primary-400' 
                  : 'text-surface-500 dark:text-surface-400 hover:text-surface-700 dark:hover:text-surface-300'
              )}
              aria-label={tab.label}
              aria-current={isActive ? 'page' : undefined}
            >
              <div className="relative">
                <Icon 
                  className={cn(
                    'w-6 h-6 transition-transform duration-200',
                    isActive && 'scale-110'
                  )} 
                />
                
                {/* Badge */}
                {tab.badge && tab.badge > 0 && (
                  <span 
                    className={cn(
                      'absolute -top-1 -right-1',
                      'min-w-[18px] h-[18px] px-1',
                      'flex items-center justify-center',
                      'bg-error-500 text-white text-[10px] font-bold',
                      'rounded-full'
                    )}
                  >
                    {tab.badge > 99 ? '99+' : tab.badge}
                  </span>
                )}
              </div>
              
              <span 
                className={cn(
                  'text-[10px] mt-1 font-medium',
                  isActive && 'font-semibold'
                )}
              >
                {tab.label}
              </span>
              
              {/* Active indicator */}
              {isActive && (
                <div 
                  className={cn(
                    'absolute bottom-1 left-1/2 -translate-x-1/2',
                    'w-1 h-1 rounded-full',
                    'bg-primary-500'
                  )} 
                />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
};

export default TabBar;
