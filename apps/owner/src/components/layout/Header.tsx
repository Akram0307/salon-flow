/**
 * Salon Flow Owner Dashboard - Header Component
 * Professional header with search, notifications, and user menu
 */

import React, { useState, forwardRef } from 'react';
import { cn } from '../../lib/utils';
import { Avatar } from '../ui/Avatar';
import { Badge } from '../ui/Badge';
import type { BaseComponentProps } from '../../types/design-system';

// ============================================
// Header Types
// ============================================
export interface HeaderProps extends BaseComponentProps {
  title?: string;
  subtitle?: string;
  showSearch?: boolean;
  onSearch?: (query: string) => void;
  user?: {
    name: string;
    email: string;
    avatar?: string;
    role?: string;
  };
  salon?: {
    name: string;
    logo?: string;
  };
  notifications?: NotificationItem[];
  onNotificationClick?: (id: string) => void;
  onNotificationReadAll?: () => void;
  onUserMenuClick?: () => void;
  onSettingsClick?: () => void;
  onLogout?: () => void;
  leftContent?: React.ReactNode;
  rightContent?: React.ReactNode;
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: Date | string;
  read: boolean;
}

// ============================================
// Header Component
// ============================================
export const Header = forwardRef<HTMLHeaderElement, HeaderProps>(
  (
    {
      title,
      subtitle,
      showSearch = true,
      onSearch,
      user,
      salon,
      notifications = [],
      onNotificationClick,
      onNotificationReadAll,
      onUserMenuClick,
      onSettingsClick,
      onLogout,
      leftContent,
      rightContent,
      className,
    },
    ref
  ) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [showNotifications, setShowNotifications] = useState(false);
    const [showUserMenu, setShowUserMenu] = useState(false);

    const unreadCount = notifications.filter((n) => !n.read).length;

    const handleSearch = (e: React.FormEvent) => {
      e.preventDefault();
      onSearch?.(searchQuery);
    };

    return (
      <header
        ref={ref}
        className={cn(
          'sticky top-0 z-30 h-16',
          'bg-white/80 dark:bg-surface-800/80 backdrop-blur-md',
          'border-b border-surface-200 dark:border-surface-700',
          className
        )}
      >
        <div className="h-full px-4 sm:px-6 flex items-center justify-between gap-4">
          {/* Left Section */}
          <div className="flex items-center gap-4 flex-1 min-w-0">
            {leftContent}

            {/* Page Title */}
            {(title || subtitle) && (
              <div className="hidden sm:block min-w-0">
                {title && (
                  <h1 className="text-lg font-semibold text-surface-900 dark:text-white truncate">
                    {title}
                  </h1>
                )}
                {subtitle && (
                  <p className="text-sm text-surface-500 dark:text-surface-400 truncate">
                    {subtitle}
                  </p>
                )}
              </div>
            )}

            {/* Search */}
            {showSearch && (
              <form onSubmit={handleSearch} className="flex-1 max-w-md hidden md:block">
                <div className="relative">
                  <svg
                    className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                  <input
                    type="search"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search bookings, customers, services..."
                    className="w-full pl-10 pr-4 py-2 text-sm rounded-lg bg-surface-100 dark:bg-surface-700 border-0 focus:ring-2 focus:ring-primary-500 text-surface-900 dark:text-white placeholder:text-surface-400"
                  />
                </div>
              </form>
            )}
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-2 sm:gap-3">
            {rightContent}

            {/* AI Assistant Quick Access */}
            <button
n              className="p-2 rounded-lg bg-gradient-to-r from-primary-500 to-accent-500 text-white hover:shadow-glow transition-shadow"
              aria-label="Open AI Assistant"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            </button>

            {/* Notifications */}
            <div className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="relative p-2 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-700 text-surface-600 dark:text-surface-400 transition-colors"
                aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ''}`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                  />
                </svg>
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-4 h-4 text-xs font-bold text-white bg-error-500 rounded-full flex items-center justify-center">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </button>

              {/* Notifications Dropdown */}
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-surface-800 rounded-xl shadow-lg border border-surface-200 dark:border-surface-700 overflow-hidden">
                  <div className="px-4 py-3 border-b border-surface-100 dark:border-surface-700 flex items-center justify-between">
                    <h3 className="font-semibold text-surface-900 dark:text-white">Notifications</h3>
                    {unreadCount > 0 && (
                      <button
                        onClick={onNotificationReadAll}
                        className="text-xs text-primary-600 hover:text-primary-700"
                      >
                        Mark all read
                      </button>
                    )}
                  </div>
                  <div className="max-h-80 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="px-4 py-8 text-center text-surface-500">
                        No notifications
                      </div>
                    ) : (
                      notifications.slice(0, 5).map((notification) => (
                        <button
                          key={notification.id}
                          onClick={() => onNotificationClick?.(notification.id)}
                          className={cn(
                            'w-full px-4 py-3 text-left hover:bg-surface-50 dark:hover:bg-surface-700/50 border-b border-surface-100 dark:border-surface-700 last:border-0',
                            !notification.read && 'bg-primary-50/50 dark:bg-primary-900/10'
                          )}
                        >
                          <p className="text-sm font-medium text-surface-900 dark:text-white">
                            {notification.title}
                          </p>
                          <p className="text-xs text-surface-500 dark:text-surface-400 mt-0.5">
                            {notification.message}
                          </p>
                        </button>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
              >
                <Avatar
                  name={user?.name || 'User'}
                  src={user?.avatar}
                  size="sm"
                />
                <div className="hidden sm:block text-left">
                  <p className="text-sm font-medium text-surface-900 dark:text-white">
                    {user?.name || 'User'}
                  </p>
                  <p className="text-xs text-surface-500 dark:text-surface-400">
                    {user?.role || 'Owner'}
                  </p>
                </div>
                <svg
                  className="hidden sm:block w-4 h-4 text-surface-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* User Dropdown */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-surface-800 rounded-xl shadow-lg border border-surface-200 dark:border-surface-700 overflow-hidden">
                  <div className="px-4 py-3 border-b border-surface-100 dark:border-surface-700">
                    <p className="font-medium text-surface-900 dark:text-white">{user?.name}</p>
                    <p className="text-sm text-surface-500 dark:text-surface-400">{user?.email}</p>
                  </div>
                  <div className="py-1">
                    <button
                      onClick={onSettingsClick}
                      className="w-full px-4 py-2 text-left text-sm text-surface-700 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-700/50 flex items-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      Settings
                    </button>
                    <button
                      onClick={onLogout}
                      className="w-full px-4 py-2 text-left text-sm text-error-600 hover:bg-surface-50 dark:hover:bg-surface-700/50 flex items-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>
    );
  }
);

Header.displayName = 'Header';

export default Header;
