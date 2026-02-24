/**
 * Settings Page - Main Settings Hub with Tabbed Navigation
 * Mobile-responsive with collapsible sidebar
 */
import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  User,
  Users,
  Scissors,
  Bell,
  CreditCard,
  Puzzle,
  ChevronLeft,
  Menu,
  X,
  Settings,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Settings navigation items
const settingsNavItems = [
  { id: 'profile', label: 'Profile', icon: User, path: '/settings/profile' },
  { id: 'staff', label: 'Staff', icon: Users, path: '/settings/staff' },
  { id: 'services', label: 'Services', icon: Scissors, path: '/settings/services' },
  { id: 'notifications', label: 'Notifications', icon: Bell, path: '/settings/notifications' },
  { id: 'billing', label: 'Billing', icon: CreditCard, path: '/settings/billing' },
  { id: 'integrations', label: 'Integrations', icon: Puzzle, path: '/settings/integrations' },
];

const SettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Get current active tab from URL
  const currentPath = location.pathname;
  const activeTab = settingsNavItems.find(item => currentPath.includes(item.id))?.id || 'profile';

  const handleNavClick = (path: string) => {
    navigate(path);
    setIsMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Mobile Header */}
      <div className="lg:hidden bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
          >
            <ChevronLeft className="w-5 h-5 mr-1" />
            <span className="text-sm font-medium">Back</span>
          </button>
          <h1 className="text-lg font-semibold text-gray-900 dark:text-white">Settings</h1>
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            {isMobileMenuOpen ? (
              <X className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            ) : (
              <Menu className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            )}
          </button>
        </div>
      </div>

      <div className="flex max-w-7xl mx-auto">
        {/* Sidebar Navigation */}
        <aside
          className={cn(
            'fixed inset-y-0 left-0 z-40 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transform transition-transform duration-200 ease-in-out lg:translate-x-0 lg:static lg:h-[calc(100vh-64px)]',
            isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
          )}
        >
          {/* Desktop Header */}
          <div className="hidden lg:flex items-center px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <Settings className="w-5 h-5 text-indigo-600 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Settings</h2>
          </div>

          {/* Navigation Items */}
          <nav className="p-4 space-y-1">
            {settingsNavItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;

              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.path)}
                  className={cn(
                    'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors duration-200 min-h-[44px]',
                    isActive
                      ? 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 border-l-4 border-indigo-600'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  )}
                >
                  <Icon
                    className={cn(
                      'w-5 h-5',
                      isActive
                        ? 'text-indigo-600 dark:text-indigo-400'
                        : 'text-gray-400 dark:text-gray-500'
                    )}
                  />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Mobile Close Button */}
          <div className="lg:hidden p-4 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setIsMobileMenuOpen(false)}
              className="w-full py-2 px-4 bg-gray-100 dark:bg-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Close Menu
            </button>
          </div>
        </aside>

        {/* Mobile Overlay */}
        {isMobileMenuOpen && (
          <div
            className="fixed inset-0 bg-black/50 z-30 lg:hidden"
            onClick={() => setIsMobileMenuOpen(false)}
          />
        )}

        {/* Main Content Area */}
        <main className="flex-1 p-4 lg:p-8">
          <div className="max-w-4xl">
            {/* Desktop Breadcrumb */}
            <div className="hidden lg:flex items-center text-sm text-gray-500 dark:text-gray-400 mb-6">
              <span>Settings</span>
              <span className="mx-2">/</span>
              <span className="text-gray-900 dark:text-white font-medium capitalize">
                {settingsNavItems.find(item => item.id === activeTab)?.label || 'Profile'}
              </span>
            </div>

            {/* Content Placeholder - Child routes will render here */}
            <div className="text-center py-12">
              <Settings className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Select a Settings Category
              </h3>
              <p className="text-gray-500 dark:text-gray-400 max-w-sm mx-auto">
                Choose a category from the sidebar to manage your salon settings
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default SettingsPage;
