/**
 * Salon Flow Owner Dashboard - Main Dashboard Page
 * Comprehensive dashboard with all widgets and components
 */

import React, { useState, useEffect } from 'react';
import { cn } from '../lib/utils';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { StatCard } from '../components/dashboard/StatCard';
import { BookingCard, BookingList } from '../components/dashboard/BookingCard';
import { ActivityFeed } from '../components/dashboard/ActivityFeed';
import { QuickActions } from '../components/dashboard/QuickActions';
import { AIWidget } from '../components/dashboard/AIWidget';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Skeleton } from '../components/ui/Skeleton';
import type { ActivityItem, QuickAction } from '../components/dashboard';

// ============================================
// Mock Data
// ============================================
const mockStats = [
  {
    id: 'revenue',
    title: 'Today\'s Revenue',
    value: '₹24,500',
    change: 12.5,
    changeLabel: 'vs yesterday',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    color: 'primary' as const,
  },
  {
    id: 'bookings',
    title: 'Today\'s Bookings',
    value: '18',
    change: 8.3,
    changeLabel: 'vs yesterday',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
    color: 'secondary' as const,
  },
  {
    id: 'customers',
    title: 'New Customers',
    value: '5',
    change: -2.1,
    changeLabel: 'vs last week',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
    color: 'accent' as const,
  },
  {
    id: 'staff',
    title: 'Staff Active',
    value: '6/8',
    change: 0,
    changeLabel: 'on duty today',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    ),
    color: 'success' as const,
  },
];

const mockBookings = [
  {
    id: '1',
    customer: { name: 'Priya Sharma', phone: '+91 98765 43210' },
    service: { name: 'Hair Cut & Styling', duration: 45, price: 500 },
    staff: { name: 'Rahul Kumar' },
    time: '10:00 AM',
    date: 'Today',
    status: 'confirmed' as const,
  },
  {
    id: '2',
    customer: { name: 'Anjali Patel' },
    service: { name: 'Facial & Cleanup', duration: 60, price: 1200 },
    staff: { name: 'Sneha Reddy' },
    time: '10:30 AM',
    date: 'Today',
    status: 'in-progress' as const,
  },
  {
    id: '3',
    customer: { name: 'Vikram Singh' },
    service: { name: 'Beard Trim', duration: 20, price: 200 },
    staff: { name: 'Rahul Kumar' },
    time: '11:00 AM',
    date: 'Today',
    status: 'pending' as const,
  },
  {
    id: '4',
    customer: { name: 'Meera Krishnan' },
    service: { name: 'Hair Color', duration: 120, price: 3500 },
    time: '11:30 AM',
    date: 'Today',
    status: 'pending' as const,
  },
];

const mockActivities: ActivityItem[] = [
  {
    id: '1',
    type: 'booking',
    title: 'New booking created',
    description: 'Priya Sharma booked Hair Cut & Styling',
    timestamp: new Date(Date.now() - 5 * 60000),
    user: { name: 'System' },
  },
  {
    id: '2',
    type: 'payment',
    title: 'Payment received',
    description: '₹1,200 from Anjali Patel via UPI',
    timestamp: new Date(Date.now() - 15 * 60000),
    user: { name: 'Sneha Reddy' },
  },
  {
    id: '3',
    type: 'ai',
    title: 'AI generated marketing campaign',
    description: 'Weekend special promotion ready for review',
    timestamp: new Date(Date.now() - 30 * 60000),
    actionable: true,
    actionLabel: 'Review',
  },
  {
    id: '4',
    type: 'customer',
    title: 'New customer registered',
    description: 'Vikram Singh signed up via WhatsApp',
    timestamp: new Date(Date.now() - 45 * 60000),
  },
  {
    id: '5',
    type: 'staff',
    title: 'Staff shift updated',
    description: 'Rahul Kumar\'s shift changed to 9 AM - 6 PM',
    timestamp: new Date(Date.now() - 60 * 60000),
    user: { name: 'Admin' },
  },
];

const quickActions: QuickAction[] = [
  {
    id: 'new-booking',
    label: 'New Booking',
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
    ),
    color: 'primary',
    onClick: () => console.log('New booking'),
  },
  {
    id: 'add-customer',
    label: 'Add Customer',
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
      </svg>
    ),
    color: 'secondary',
    onClick: () => console.log('Add customer'),
  },
  {
    id: 'ai-assistant',
    label: 'AI Assistant',
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    color: 'accent',
    onClick: () => console.log('AI assistant'),
    badge: 'New',
  },
  {
    id: 'send-message',
    label: 'Send Message',
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    ),
    color: 'success',
    onClick: () => console.log('Send message'),
  },
];

// ============================================
// Dashboard Page Component
// ============================================
export const Dashboard: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [date] = useState(new Date());

  useEffect(() => {
    // Simulate data loading
    const timer = setTimeout(() => setIsLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  const formatGreeting = () => {
    const hour = date.getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const formatDate = () => {
    return date.toLocaleDateString('en-IN', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-white">
              {formatGreeting()}, Owner!
            </h1>
            <p className="text-surface-500 dark:text-surface-400">{formatDate()}</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export Report
            </Button>
            <Button size="sm">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              New Booking
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {isLoading
            ? Array.from({ length: 4 }).map((_, i) => (
                <Card key={i} className="p-6">
                  <Skeleton className="h-4 w-24 mb-2" />
                  <Skeleton className="h-8 w-32 mb-2" />
                  <Skeleton className="h-3 w-20" />
                </Card>
              ))
            : mockStats.map((stat) => (
                <StatCard key={stat.id} {...stat} />
              ))}
        </div>

        {/* Quick Actions */}
        <Card title="Quick Actions" className="p-6">
          {isLoading ? (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-24 rounded-xl" />
              ))}
            </div>
          ) : (
            <QuickActions actions={quickActions} columns={4} size="md" />
          )}
        </Card>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Upcoming Bookings */}
          <div className="lg:col-span-2">
            <Card
              title="Upcoming Bookings"
              subtitle="Today's schedule"
              className="p-6"
              actions={
                <Button variant="ghost" size="sm">
                  View All
                  <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Button>
              }
            >
              {isLoading ? (
                <div className="space-y-3">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <Skeleton key={i} className="h-20 rounded-xl" />
                  ))}
                </div>
              ) : (
                <BookingList bookings={mockBookings} />
              )}
            </Card>
          </div>

          {/* Activity Feed */}
          <div>
            <Card
              title="Recent Activity"
              subtitle="Latest updates"
              className="p-4"
            >
              {isLoading ? (
                <div className="space-y-3">
                  {Array.from({ length: 4 }).map((_, i) => (
                    <div key={i} className="flex gap-3">
                      <Skeleton className="w-8 h-8 rounded-lg" />
                      <div className="flex-1">
                        <Skeleton className="h-4 w-3/4 mb-1" />
                        <Skeleton className="h-3 w-1/2" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <ActivityFeed activities={mockActivities} maxItems={5} />
              )}
            </Card>
          </div>
        </div>

        {/* Revenue Chart Placeholder */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="Revenue Overview" subtitle="Last 7 days" className="p-6">
            {isLoading ? (
              <Skeleton className="h-64 w-full" />
            ) : (
              <div className="h-64 flex items-center justify-center bg-surface-50 dark:bg-surface-700/50 rounded-lg">
                <div className="text-center">
                  <svg className="w-12 h-12 mx-auto text-surface-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <p className="text-sm text-surface-500 dark:text-surface-400">
                    Revenue chart will be displayed here
                  </p>
                  <p className="text-xs text-surface-400 dark:text-surface-500 mt-1">
                    Integration with Recharts coming soon
                  </p>
                </div>
              </div>
            )}
          </Card>

          <Card title="Popular Services" subtitle="This week" className="p-6">
            {isLoading ? (
              <Skeleton className="h-64 w-full" />
            ) : (
              <div className="space-y-4">
                {[
                  { name: 'Hair Cut & Styling', count: 45, revenue: '₹22,500', percentage: 85 },
                  { name: 'Facial & Cleanup', count: 32, revenue: '₹38,400', percentage: 70 },
                  { name: 'Hair Color', count: 18, revenue: '₹63,000', percentage: 50 },
                  { name: 'Beard Trim', count: 28, revenue: '₹5,600', percentage: 60 },
                  { name: 'Manicure & Pedicure', count: 15, revenue: '₹12,000', percentage: 40 },
                ].map((service, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-surface-900 dark:text-white">
                        {service.name}
                      </span>
                      <span className="text-sm text-surface-500 dark:text-surface-400">
                        {service.count} bookings
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-2 bg-surface-100 dark:bg-surface-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full"
                          style={{ width: `${service.percentage}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-surface-700 dark:text-surface-300">
                        {service.revenue}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>

      {/* AI Widget */}
      <AIWidget
        onSendMessage={async (message) => {
          // Simulate AI response
          await new Promise((resolve) => setTimeout(resolve, 1500));
          return `I received your message: "${message}". I'm here to help you manage your salon efficiently. What would you like to know?`;
        }}
      />
    </DashboardLayout>
  );
};

export default Dashboard;
