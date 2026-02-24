/**
 * Salon Flow Owner PWA - Dashboard Home Screen
 * Task 2.2: Main dashboard with business overview, AI insights, and quick actions
 *
 * Features:
 * - AI Insights Bar with rotating insights
 * - KPI Stat Cards Grid (2x2 on mobile)
 * - Quick Actions horizontal scrollable row
 * - Today's Schedule Preview
 * - Recent Activity Feed
 * - AI Widget floating button
 * - Pull-to-refresh support
 * - Full dark mode support
 * - Mobile Bottom Navigation
 */

import React, { useState, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  CalendarPlus,
  UserPlus,
  Users,
  BarChart3,
  Megaphone,
  IndianRupee,
  Calendar,
  Users2,
  Clock,
  ChevronRight,
  Sparkles,
  Lightbulb,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  MoreHorizontal,
  X,
  Home,
  BarChart2,
  Settings,
  LogOut,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/stores/authStore';
import { useTenantStore } from '@/stores/tenantStore';
import { InsightsBar } from '@/components/organisms/InsightsBar';
import { AIWidget } from '@/components/dashboard/AIWidget';
import { ActivityFeed } from '@/components/dashboard/ActivityFeed';
import { Avatar, Badge, Button, Card, Skeleton } from '@/components/atoms';
import type { QuickAction } from '@/components/dashboard';
import type { Insight } from '@/components/organisms/InsightsBar';
import {
  useDashboardStats,
  useTodaysBookings,
  useRecentActivity,
  useAIInsights,
  useRefreshDashboard,
  type TodaysBooking,
} from '@/services/dashboardService';

// ============================================
// Types
// ============================================
interface StatCardData {
  id: string;
  icon: React.ReactNode;
  iconBg: string;
  value: string;
  label: string;
  trend: 'up' | 'down' | 'neutral';
  trendValue: string;
  onWhy?: () => void;
  onOptimize?: () => void;
}

// ============================================
// Mobile Bottom Navigation Component
// ============================================
const MobileBottomNav: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  

  const navItems = [
    { id: 'home', label: 'Home', icon: Home, path: '/dashboard' },
    { id: 'bookings', label: 'Bookings', icon: Calendar, path: '/bookings' },
    { id: 'analytics', label: 'Analytics', icon: BarChart2, path: '/analytics' },
    { id: 'settings', label: 'Settings', icon: Settings, path: '/settings' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 bg-white dark:bg-surface-800 border-t border-surface-200 dark:border-surface-700 px-4 py-2">
      <div className="flex items-center justify-around max-w-md mx-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path || location.pathname.startsWith(item.path);
          return (
            <button
              key={item.id}
              onClick={() => navigate(item.path)}
              className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-colors ${
                isActive ? 'text-primary-600 dark:text-primary-400' : 'text-surface-500 dark:text-surface-400'
              }`}
              aria-label={item.label}
              role="link"
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon className="w-5 h-5" />
              <span className="text-xs font-medium">{item.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};

// ============================================
// Dashboard Page Component
// ============================================
const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { currentSalon } = useTenantStore();
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showAIInsights, setShowAIInsights] = useState(true);
  
  // React Query hooks for data fetching
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
  } = useDashboardStats();
  
  const {
    data: bookings,
    isLoading: bookingsLoading,
    error: bookingsError,
  } = useTodaysBookings();
  
  const {
    data: activities,
    isLoading: activitiesLoading,
    error: activitiesError,
  } = useRecentActivity();
  
  const { data: aiInsights } = useAIInsights();
  
  const refreshDashboard = useRefreshDashboard();

  // Pull-to-refresh handler
  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      await refreshDashboard();
    } finally {
      setIsRefreshing(false);
    }
  }, [refreshDashboard]);

  // ============================================
  // Quick Actions Configuration
  // ============================================
  const quickActions: QuickAction[] = [
    {
      id: 'new-booking',
      label: 'New Booking',
      icon: <CalendarPlus className="w-5 h-5" />,
      color: 'primary',
      onClick: () => navigate('/bookings/new'),
    },
    {
      id: 'add-customer',
      label: 'Add Customer',
      icon: <UserPlus className="w-5 h-5" />,
      color: 'secondary',
      onClick: () => navigate('/customers/new'),
    },
    {
      id: 'add-staff',
      label: 'Add Staff',
      icon: <Users className="w-5 h-5" />,
      color: 'accent',
      onClick: () => navigate('/staff/new'),
    },
    {
      id: 'view-reports',
      label: 'Reports',
      icon: <BarChart3 className="w-5 h-5" />,
      color: 'success',
      onClick: () => navigate('/analytics'),
    },
    {
      id: 'send-campaign',
      label: 'Campaign',
      icon: <Megaphone className="w-5 h-5" />,
      color: 'warning',
      onClick: () => navigate('/marketing/campaigns'),
    },
  ];

  // ============================================
  // Prepare Stat Cards Data
  // ============================================
  const statCards: StatCardData[] = React.useMemo(() => {
    if (!stats) return [];
    
    return [
      {
        id: 'revenue',
        icon: <IndianRupee className="w-5 h-5" />,
        iconBg: 'bg-success-100 text-success-600 dark:bg-success-900/30 dark:text-success-400',
        value: `${stats.todayRevenue.currency}${stats.todayRevenue.value.toLocaleString('en-IN')}`,
        label: "Today's Revenue",
        trend: stats.todayRevenue.change >= 0 ? 'up' : 'down',
        trendValue: `${stats.todayRevenue.change >= 0 ? '+' : ''}${stats.todayRevenue.change}% vs yesterday`,
        onWhy: () => console.log('AI: Why revenue changed'),
        onOptimize: () => console.log('AI: Optimize revenue'),
      },
      {
        id: 'bookings',
        icon: <Calendar className="w-5 h-5" />,
        iconBg: 'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400',
        value: `${stats.todayBookings.confirmed + stats.todayBookings.pending}`,
        label: "Today's Bookings",
        trend: stats.todayBookings.change >= 0 ? 'up' : 'down',
        trendValue: `${stats.todayBookings.confirmed} confirmed, ${stats.todayBookings.pending} pending`,
        onWhy: () => console.log('AI: Why bookings changed'),
        onOptimize: () => console.log('AI: Optimize bookings'),
      },
      {
        id: 'customers',
        icon: <Users2 className="w-5 h-5" />,
        iconBg: 'bg-secondary-100 text-secondary-600 dark:bg-secondary-900/30 dark:text-secondary-400',
        value: stats.activeCustomers.total.toString(),
        label: 'Active Customers',
        trend: stats.activeCustomers.change >= 0 ? 'up' : 'down',
        trendValue: `${stats.activeCustomers.new} new this week`,
        onWhy: () => console.log('AI: Why customer activity changed'),
        onOptimize: () => console.log('AI: Optimize customer retention'),
      },
      {
        id: 'staff',
        icon: <Clock className="w-5 h-5" />,
        iconBg: 'bg-accent-100 text-accent-600 dark:bg-accent-900/30 dark:text-accent-400',
        value: `${stats.staffOnDuty.present}/${stats.staffOnDuty.total}`,
        label: 'Staff on Duty',
        trend: 'neutral',
        trendValue: `${stats.staffOnDuty.onLeave} on leave`,
        onWhy: () => console.log('AI: Staff availability'),
        onOptimize: () => console.log('AI: Optimize staffing'),
      },
    ];
  }, [stats]);

  // ============================================
  // Prepare Insights for InsightsBar
  // ============================================
  const insights: Insight[] = React.useMemo(() => {
    if (!aiInsights) return [];
    
    return aiInsights.map((insight) => ({
      id: insight.id,
      type: insight.type,
      message: insight.message,
      detail: insight.detail,
      action: insight.action,
      dismissible: insight.dismissible !== false,
      onAction: insight.action ? () => {
        console.log(`Action clicked: ${insight.action}`);
        // Handle different actions based on insight
        if (insight.message.includes('slots empty')) {
          navigate('/bookings');
        } else if (insight.message.includes('birthday')) {
          navigate('/customers');
        } else if (insight.message.includes('Revenue')) {
          navigate('/analytics');
        }
      } : undefined,
    }));
  }, [aiInsights, navigate]);

  // ============================================
  // Handle Insights Dismiss
  // ============================================
  const handleDismissInsight = useCallback((id: string) => {
    console.log(`Dismissed insight: ${id}`);
    // In a real app, you'd call an API to dismiss
  }, []);

  // ============================================
  // Get Greeting based on time
  // ============================================
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-900">
      {/* Main Content Container */}
      <div className="max-w-md mx-auto pb-24">
        
        {/* ============================================
            HEADER SECTION
        ============================================ */}
        <header className="sticky top-0 z-30 bg-white/80 dark:bg-surface-800/80 backdrop-blur-md border-b border-surface-200 dark:border-surface-700 px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-surface-500 dark:text-surface-400">
                {getGreeting()}
              </p>
              <h1 className="text-xl font-bold text-surface-900 dark:text-white">
                {user?.displayName || 'Salon Owner'}
              </h1>
              <p className="text-xs text-surface-400 dark:text-surface-500">
                {currentSalon?.name || 'Your Salon'}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className={cn(
                  'p-2 rounded-full hover:bg-surface-100 dark:hover:bg-surface-700',
                  'transition-colors duration-200',
                  isRefreshing && 'animate-spin'
                )}
                aria-label="Refresh dashboard"
              >
                <RefreshCw className="w-5 h-5 text-surface-600 dark:text-surface-400" />
              </button>
              <button
                onClick={async () => {
                  await logout();
                  navigate('/login');
                }}
                className="p-2 rounded-full hover:bg-surface-100 dark:hover:bg-surface-700 text-error-600 transition-colors"
                aria-label="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
              <div
                className="cursor-pointer"
                onClick={() => navigate('/settings')}
              >
                <Avatar
                  alt={user?.displayName || 'User'}
                  src={user?.photoURL}
                  size="md"
                />
              </div>
            </div>
          </div>
        </header>

        {/* ============================================
            SCROLLABLE CONTENT
        ============================================ */}
        <main className="px-4 py-4 space-y-6">
          
          {/* ----------------------------------------
              AI INSIGHTS BAR
          ---------------------------------------- */}
          {showAIInsights && insights.length > 0 && (
            <section className="relative">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-sm font-semibold text-surface-700 dark:text-surface-300 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-primary-500" />
                  AI Insights
                </h2>
                <button
                  onClick={() => setShowAIInsights(false)}
                  className="p-1 rounded hover:bg-surface-200 dark:hover:bg-surface-700"
                >
                  <X className="w-4 h-4 text-surface-400" />
                </button>
              </div>
              <InsightsBar
                insights={insights}
                onDismiss={handleDismissInsight}
                maxVisible={2}
              />
            </section>
          )}

          {/* ----------------------------------------
              KPI STAT CARDS GRID
          ---------------------------------------- */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-base font-semibold text-surface-900 dark:text-white">
                Overview
              </h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/analytics')}
              >
                View All
              </Button>
            </div>
            
            {statsLoading ? (
              <div className="grid grid-cols-2 gap-3">
                {[1, 2, 3, 4].map((i) => (
                  <Card key={i} className="p-4">
                    <Skeleton className="w-10 h-10 rounded-lg mb-3" />
                    <Skeleton className="h-8 w-20 mb-2" />
                    <Skeleton className="h-4 w-24" />
                  </Card>
                ))}
              </div>
            ) : statsError ? (
              <Card className="p-4 text-center">
                <p className="text-sm text-error-600 dark:text-error-400">
                  Failed to load stats
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-2"
                  onClick={handleRefresh}
                >
                  Retry
                </Button>
              </Card>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                {statCards.map((card) => (
                  <Card
                    key={card.id}
                    className="p-4 flex flex-col"
                  >
                    {/* Icon */}
                    <div className={cn(
                      'w-10 h-10 rounded-lg flex items-center justify-center mb-3',
                      card.iconBg
                    )}>
                      {card.icon}
                    </div>
                    
                    {/* Value */}
                    <div className="text-2xl font-bold text-surface-900 dark:text-white mb-1">
                      {card.value}
                    </div>
                    
                    {/* Label */}
                    <div className="text-xs text-surface-500 dark:text-surface-400 mb-2">
                      {card.label}
                    </div>
                    
                    {/* Trend */}
                    <div className={cn(
                      'flex items-center gap-1 text-xs',
                      card.trend === 'up' && 'text-success-600 dark:text-success-400',
                      card.trend === 'down' && 'text-error-600 dark:text-error-400',
                      card.trend === 'neutral' && 'text-surface-500 dark:text-surface-400'
                    )}>
                      {card.trend === 'up' && <TrendingUp className="w-3 h-3" />}
                      {card.trend === 'down' && <TrendingDown className="w-3 h-3" />}
                      <span>{card.trendValue}</span>
                    </div>
                    
                    {/* AI Action Buttons */}
                    <div className="flex items-center gap-2 mt-3 pt-3 border-t border-surface-100 dark:border-surface-700">
                      {card.onWhy && (
                        <button
                          onClick={card.onWhy}
                          className="flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium bg-indigo-50 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/30 transition-colors"
                        >
                          <Lightbulb className="w-3 h-3" />
                          Why?
                        </button>
                      )}
                      {card.onOptimize && (
                        <button
                          onClick={card.onOptimize}
                          className="flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-primary-900/30 transition-colors"
                        >
                          <Sparkles className="w-3 h-3" />
                          Optimize
                        </button>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </section>

          {/* ----------------------------------------
              QUICK ACTIONS SECTION
          ---------------------------------------- */}
          <section>
            <h2 className="text-base font-semibold text-surface-900 dark:text-white mb-3">
              Quick Actions
            </h2>
            <div className="overflow-x-auto -mx-4 px-4 pb-2 scrollbar-hide">
              <div className="flex gap-3 min-w-max">
                {quickActions.map((action) => (
                  <button
                    key={action.id}
                    onClick={action.onClick}
                    className={cn(
                      'flex flex-col items-center gap-2 p-3 rounded-xl min-w-[80px]',
                      'transition-all duration-200 active:scale-95',
                      'border border-surface-200 dark:border-surface-700',
                      action.color === 'primary' && 'bg-primary-50 dark:bg-primary-900/20 hover:bg-primary-100 dark:hover:bg-primary-900/30',
                      action.color === 'secondary' && 'bg-secondary-50 dark:bg-secondary-900/20 hover:bg-secondary-100 dark:hover:bg-secondary-900/30',
                      action.color === 'accent' && 'bg-accent-50 dark:bg-accent-900/20 hover:bg-accent-100 dark:hover:bg-accent-900/30',
                      action.color === 'success' && 'bg-success-50 dark:bg-success-900/20 hover:bg-success-100 dark:hover:bg-success-900/30',
                      action.color === 'warning' && 'bg-warning-50 dark:bg-warning-900/20 hover:bg-warning-100 dark:hover:bg-warning-900/30',
                    )}
                  >
                    <div className={cn(
                      'w-12 h-12 rounded-full flex items-center justify-center',
                      action.color === 'primary' && 'bg-primary-100 dark:bg-primary-800 text-primary-600 dark:text-primary-400',
                      action.color === 'secondary' && 'bg-secondary-100 dark:bg-secondary-800 text-secondary-600 dark:text-secondary-400',
                      action.color === 'accent' && 'bg-accent-100 dark:bg-accent-800 text-accent-600 dark:text-accent-400',
                      action.color === 'success' && 'bg-success-100 dark:bg-success-800 text-success-600 dark:text-success-400',
                      action.color === 'warning' && 'bg-warning-100 dark:bg-warning-800 text-warning-600 dark:text-warning-400',
                    )}>
                      {action.icon}
                    </div>
                    <span className="text-xs font-medium text-surface-700 dark:text-surface-300 whitespace-nowrap">
                      {action.label}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </section>

          {/* ----------------------------------------
              TODAY'S SCHEDULE PREVIEW
          ---------------------------------------- */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-base font-semibold text-surface-900 dark:text-white">
                Today's Schedule
              </h2>
              <Button
                variant="ghost"
                size="sm"
                className="flex items-center gap-1"
                onClick={() => navigate('/bookings')}
              >
                View All
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
            
            {bookingsLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <Card key={i} className="p-4">
                    <div className="flex gap-3">
                      <Skeleton className="w-12 h-12 rounded-full" />
                      <div className="flex-1 space-y-2">
                        <Skeleton className="h-4 w-32" />
                        <Skeleton className="h-3 w-24" />
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : bookingsError ? (
              <Card className="p-4 text-center">
                <p className="text-sm text-error-600 dark:text-error-400">
                  Failed to load bookings
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-2"
                  onClick={handleRefresh}
                >
                  Retry
                </Button>
              </Card>
            ) : bookings && bookings.length > 0 ? (
              <div className="space-y-3">
                {bookings.slice(0, 4).map((booking) => (
                  <BookingCardMini
                    key={booking.id}
                    booking={booking}
                    onPress={() => navigate(`/bookings/${booking.id}`)}
                  />
                ))}
              </div>
            ) : (
              <Card className="p-6 text-center">
                <Calendar className="w-12 h-12 mx-auto text-surface-400 mb-3" />
                <p className="text-sm text-surface-500 dark:text-surface-400">
                  No bookings today
                </p>
                <Button
                  className="mt-3"
                  size="sm"
                  onClick={() => navigate('/bookings/new')}
                >
                  Create Booking
                </Button>
              </Card>
            )}
          </section>

          {/* ----------------------------------------
              RECENT ACTIVITY FEED
          ---------------------------------------- */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-base font-semibold text-surface-900 dark:text-white">
                Recent Activity
              </h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/activity')}
              >
                View All
              </Button>
            </div>
            
            {activitiesLoading ? (
              <Card className="p-4 space-y-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="flex gap-3">
                    <Skeleton className="w-10 h-10 rounded-lg" />
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-4 w-40" />
                      <Skeleton className="h-3 w-24" />
                    </div>
                  </div>
                ))}
              </Card>
            ) : activitiesError ? (
              <Card className="p-4 text-center">
                <p className="text-sm text-error-600 dark:text-error-400">
                  Failed to load activity
                </p>
              </Card>
            ) : activities && activities.length > 0 ? (
              <Card className="p-2">
                <ActivityFeed
                  activities={activities.slice(0, 5)}
                  showTimestamp
                  maxItems={5}
                />
              </Card>
            ) : (
              <Card className="p-6 text-center">
                <MoreHorizontal className="w-12 h-12 mx-auto text-surface-400 mb-3" />
                <p className="text-sm text-surface-500 dark:text-surface-400">
                  No recent activity
                </p>
              </Card>
            )}
          </section>
        </main>
      </div>

      {/* ============================================
          AI WIDGET (FLOATING)
      ============================================ */}
      <AIWidget
        position="bottom-right"
        title="AI Assistant"
        suggestions={[
          'Show today\'s bookings',
          'What are my top customers?',
          'Generate weekend promotion',
          'Optimize staff schedule',
          'Analyze revenue trends',
        ]}
        onSendMessage={async (message) => {
          console.log('AI Query:', message);
          // Simulate AI response - in real app, call AI service
          return `I found some insights about: "${message}"`;
        }}
      />

      {/* ============================================
          MOBILE BOTTOM NAVIGATION
      ============================================ */}
      <MobileBottomNav />
    </div>
  );
};

// ============================================
// Booking Card Mini Component
// ============================================
interface BookingCardMiniProps {
  booking: TodaysBooking;
  onPress?: () => void;
}

const BookingCardMini: React.FC<BookingCardMiniProps> = ({ booking, onPress }) => {
  const statusColors: Record<string, string> = {
    confirmed: 'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-300',
    pending: 'bg-warning-100 text-warning-700 dark:bg-warning-900/30 dark:text-warning-300',
    cancelled: 'bg-error-100 text-error-700 dark:bg-error-900/30 dark:text-error-300',
    completed: 'bg-surface-100 text-surface-600 dark:bg-surface-700 dark:text-surface-400',
    in_progress: 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300',
  };

  return (
    <Card
      className="p-3 cursor-pointer hover:shadow-md transition-shadow"
      onClick={onPress}
    >
      <div className="flex items-center gap-3">
        {/* Avatar */}
        <Avatar
          alt={booking.customer.name}
          src={booking.customer.avatar}
          size="md"
        />
        
        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h3 className="font-medium text-surface-900 dark:text-white truncate">
              {booking.customer.name}
            </h3>
            <Badge
              variant="subtle"
              className={statusColors[booking.status] || statusColors.pending}
            >
              {booking.status.replace('_', ' ')}
            </Badge>
          </div>
          <p className="text-sm text-surface-500 dark:text-surface-400 truncate">
            {booking.service.name}
          </p>
          <div className="flex items-center gap-3 mt-1 text-xs text-surface-400 dark:text-surface-500">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {booking.time}
            </span>
            <span className="flex items-center gap-1">
              <Users className="w-3 h-3" />
              {booking.staff.name}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default Dashboard;
