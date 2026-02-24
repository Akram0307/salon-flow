/**
 * MobileLayout Template
 * 
 * Complete mobile page layout with header, scrollable content,
 * and tab bar navigation. Handles safe areas and mobile viewport.
 * 
 * @example
 * <MobileLayout 
 *   activeTab="home"
 *   onTabChange={setActiveTab}
 *   header={{ title: "Dashboard", showBack: false }}
 * >
 *   <DashboardContent />
 * </MobileLayout>
 */

import React from 'react';
import { cn } from '@/lib/utils';
import { SafeArea } from '../atoms/SafeArea';
import { Header } from '../molecules/Header';
import { TabBar, TabId } from '../organisms/TabBar';

interface MobileLayoutProps {
  children: React.ReactNode;
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
  header?: {
    title: string;
    subtitle?: string;
    showBack?: boolean;
    onBack?: () => void;
    rightActions?: React.ReactNode[];
  };
  className?: string;
  contentClassName?: string;
  hideTabBar?: boolean;
  hideHeader?: boolean;
}

export const MobileLayout: React.FC<MobileLayoutProps> = ({
  children,
  activeTab,
  onTabChange,
  header,
  className,
  contentClassName,
  hideTabBar = false,
  hideHeader = false,
}) => {
  return (
    <SafeArea 
      top 
      className={cn(
        'flex flex-col h-full bg-surface-50 dark:bg-surface-900',
        className
      )}
    >
      {/* Header */}
      {!hideHeader && header && (
        <Header
          title={header.title}
          subtitle={header.subtitle}
          showBack={header.showBack}
          onBack={header.onBack}
          rightActions={header.rightActions}
          sticky
        />
      )}

      {/* Main Content */}
      <main 
        className={cn(
          'flex-1 overflow-y-auto',
          'px-4 py-4',
          !hideTabBar && 'pb-24', // Space for tab bar
          contentClassName
        )}
      >
        {children}
      </main>

      {/* Tab Bar */}
      {!hideTabBar && (
        <TabBar
          activeTab={activeTab}
          onTabChange={onTabChange}
        />
      )}
    </SafeArea>
  );
};

export default MobileLayout;
