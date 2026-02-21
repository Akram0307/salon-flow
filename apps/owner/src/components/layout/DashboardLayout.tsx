/**
 * Salon Flow Owner Dashboard - Dashboard Layout Component
 * Main layout wrapper with sidebar, header, and content area
 */

import React, { useState, forwardRef } from 'react';
import { Outlet } from 'react-router-dom';
import { cn } from '../../lib/utils';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import type { BaseComponentProps } from '../../types/design-system';

// ============================================
// Dashboard Layout Types
// ============================================
export interface DashboardLayoutProps extends BaseComponentProps {
  title?: string;
  subtitle?: string;
  user?: {
    name: string;
    email: string;
    avatar?: string;
    role?: string;
  };
  notifications?: Array<{
    id: string;
    title: string;
    message: string;
    type: 'info' | 'success' | 'warning' | 'error';
    timestamp: Date | string;
    read: boolean;
  }>;
  onSearch?: (query: string) => void;
  onNotificationClick?: (id: string) => void;
  onNotificationReadAll?: () => void;
  onSettingsClick?: () => void;
  onLogout?: () => void;
  sidebarCollapsed?: boolean;
  onSidebarToggle?: () => void;
}

// ============================================
// Dashboard Layout Component
// ============================================
export const DashboardLayout = forwardRef<HTMLDivElement, DashboardLayoutProps>(
  (
    {
      title,
      subtitle,
      user,
      notifications = [],
      onSearch,
      onNotificationClick,
      onNotificationReadAll,
      onSettingsClick,
      onLogout,
      sidebarCollapsed: controlledCollapsed,
      onSidebarToggle: controlledToggle,
      className,
      children,
    },
    ref
  ) => {
    // Internal state for uncontrolled mode
    const [internalCollapsed, setInternalCollapsed] = useState(false);
    
    // Use controlled or internal state
    const collapsed = controlledCollapsed ?? internalCollapsed;
    const handleToggle = () => {
      if (controlledToggle) {
        controlledToggle();
      } else {
        setInternalCollapsed(!internalCollapsed);
      }
    };

    return (
      <div ref={ref} className={cn('min-h-screen bg-surface-50 dark:bg-surface-900', className)}>
        {/* Sidebar */}
        <Sidebar
          collapsed={collapsed}
          onToggle={handleToggle}
        />

        {/* Main Content Area */}
        <div
          className={cn(
            'transition-all duration-300 ease-smooth',
            collapsed ? 'ml-[72px]' : 'ml-64'
          )}
        >
          {/* Header */}
          <Header
            title={title}
            subtitle={subtitle}
            user={user}
            notifications={notifications}
            onSearch={onSearch}
            onNotificationClick={onNotificationClick}
            onNotificationReadAll={onNotificationReadAll}
            onSettingsClick={onSettingsClick}
            onLogout={onLogout}
          />

          {/* Page Content */}
          <main className="p-4 sm:p-6">
            {children || <Outlet />}
          </main>
        </div>

        {/* Mobile Sidebar Overlay */}
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden hidden"
          onClick={handleToggle}
          aria-hidden="true"
        />
      </div>
    );
  }
);

DashboardLayout.displayName = 'DashboardLayout';

// ============================================
// Page Container Component
// ============================================
export interface PageContainerProps extends BaseComponentProps {
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full' | '7xl';
}

export const PageContainer: React.FC<PageContainerProps> = ({
  maxWidth = '7xl',
  className,
  children,
}) => {
  const maxWidthStyles: Record<string, string> = {
    sm: 'max-w-screen-sm',
    md: 'max-w-screen-md',
    lg: 'max-w-screen-lg',
    xl: 'max-w-screen-xl',
    '2xl': 'max-w-screen-2xl',
    full: 'max-w-full',
    '7xl': 'max-w-7xl',
  };

  return (
    <div className={cn('mx-auto', maxWidthStyles[maxWidth], className)}>
      {children}
    </div>
  );
};

// ============================================
// Page Header Component
// ============================================
export interface PageHeaderProps extends BaseComponentProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
  breadcrumbs?: Array<{ label: string; href?: string }>;
  backButton?: {
    label: string;
    onClick: () => void;
  };
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  actions,
  breadcrumbs,
  backButton,
  className,
}) => {
  return (
    <div className={cn('mb-6', className)}>
      {/* Breadcrumbs */}
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav className="mb-2" aria-label="Breadcrumb">
          <ol className="flex items-center gap-2 text-sm text-surface-500 dark:text-surface-400">
            {breadcrumbs.map((crumb, index) => (
              <li key={index} className="flex items-center gap-2">
                {index > 0 && (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                )}
                {crumb.href ? (
                  <a href={crumb.href} className="hover:text-primary-600 dark:hover:text-primary-400">
                    {crumb.label}
                  </a>
                ) : (
                  <span>{crumb.label}</span>
                )}
              </li>
            ))}
          </ol>
        </nav>
      )}

      {/* Back Button */}
      {backButton && (
        <button
          onClick={backButton.onClick}
          className="mb-4 flex items-center gap-2 text-sm text-surface-600 dark:text-surface-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          {backButton.label}
        </button>
      )}

      {/* Title Row */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-white">{title}</h1>
          {subtitle && (
            <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">{subtitle}</p>
          )}
        </div>
        {actions && <div className="flex items-center gap-3">{actions}</div>}
      </div>
    </div>
  );
};

// ============================================
// Grid Layout Components
// ============================================
export interface GridProps extends BaseComponentProps {
  cols?: 1 | 2 | 3 | 4 | 5 | 6 | 12;
  gap?: 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl';
}

export const Grid: React.FC<GridProps> = ({
  cols = 3,
  gap = 'md',
  className,
  children,
}) => {
  const colsStyles: Record<number, string> = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
    5: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-5',
    6: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6',
    12: 'grid-cols-12',
  };

  const gapStyles: Record<string, string> = {
    none: 'gap-0',
    xs: 'gap-1',
    sm: 'gap-2',
    md: 'gap-4',
    lg: 'gap-6',
    xl: 'gap-8',
  };

  return (
    <div className={cn('grid', colsStyles[cols], gapStyles[gap], className)}>
      {children}
    </div>
  );
};

// ============================================
// Section Component
// ============================================
export interface SectionProps extends BaseComponentProps {
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
  collapsible?: boolean;
  defaultCollapsed?: boolean;
}

export const Section: React.FC<SectionProps> = ({
  title,
  subtitle,
  actions,
  collapsible = false,
  defaultCollapsed = false,
  className,
  children,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);

  return (
    <section className={cn('mb-8', className)}>
      {(title || actions) && (
        <div className="flex items-center justify-between mb-4">
          <div>
            {title && (
              <h2 className="text-lg font-semibold text-surface-900 dark:text-white">{title}</h2>
            )}
            {subtitle && (
              <p className="text-sm text-surface-500 dark:text-surface-400">{subtitle}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            {actions}
            {collapsible && (
              <button
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="p-1 rounded hover:bg-surface-100 dark:hover:bg-surface-700 text-surface-500"
              >
                <svg
                  className={cn('w-5 h-5 transition-transform', isCollapsed && 'rotate-180')}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            )}
          </div>
        </div>
      )}
      {!isCollapsed && children}
    </section>
  );
};

export default DashboardLayout;
