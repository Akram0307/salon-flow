/**
 * Salon Flow Owner PWA - Dashboard Data Service
 * API integration for dashboard statistics, bookings, and AI insights
 */

import { useQuery, useQueryClient, UseQueryResult } from '@tanstack/react-query';
import type { ActivityItem } from '../components/dashboard/ActivityFeed';

// ============================================
// API Client
// ============================================
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

async function fetchWithAuth(endpoint: string): Promise<any> {
  const token = localStorage.getItem('salon-flow-access-token');
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

// ============================================
// Types
// ============================================
export interface DashboardStats {
  todayRevenue: {
    value: number;
    change: number;
    changeType: 'increase' | 'decrease' | 'neutral';
    currency: string;
  };
  todayBookings: {
    confirmed: number;
    pending: number;
    total: number;
    change: number;
  };
  activeCustomers: {
    total: number;
    new: number;
    change: number;
  };
  staffOnDuty: {
    present: number;
    total: number;
    onLeave: number;
  };
  insights: AIInsight[];
}

export interface AIInsight {
  id: string;
  type: 'info' | 'warning' | 'success' | 'action' | 'ai';
  message: string;
  detail?: string;
  action?: string;
  dismissible?: boolean;
}

export interface TodaysBooking {
  id: string;
  customer: {
    id: string;
    name: string;
    avatar?: string;
    phone?: string;
  };
  service: {
    id: string;
    name: string;
    duration: number;
    price: number;
  };
  time: string;
  status: 'confirmed' | 'pending' | 'cancelled' | 'completed' | 'in_progress';
  staff: {
    id: string;
    name: string;
    avatar?: string;
  };
  notes?: string;
}

// ============================================
// API Functions
// ============================================
export async function getDashboardStats(): Promise<DashboardStats> {
  try {
    return await fetchWithAuth('/dashboard/stats');
  } catch (error) {
    console.warn('Using mock dashboard stats:', error);
    return getMockDashboardStats();
  }
}

export async function getTodaysBookings(): Promise<TodaysBooking[]> {
  try {
    return await fetchWithAuth('/bookings/today');
  } catch (error) {
    console.warn('Using mock bookings:', error);
    return getMockTodaysBookings();
  }
}

export async function getRecentActivity(): Promise<ActivityItem[]> {
  try {
    return await fetchWithAuth('/activity/recent');
  } catch (error) {
    console.warn('Using mock activity:', error);
    return getMockRecentActivity();
  }
}

export async function getAIInsights(): Promise<AIInsight[]> {
  try {
    return await fetchWithAuth('/ai/insights');
  } catch (error) {
    console.warn('Using mock AI insights:', error);
    return getMockAIInsights();
  }
}

// ============================================
// React Query Hooks
// ============================================
export const dashboardQueryKeys = {
  all: ['dashboard'] as const,
  stats: () => [...dashboardQueryKeys.all, 'stats'] as const,
  bookings: () => [...dashboardQueryKeys.all, 'bookings'] as const,
  activity: () => [...dashboardQueryKeys.all, 'activity'] as const,
  insights: () => [...dashboardQueryKeys.all, 'insights'] as const,
};

export function useDashboardStats(): UseQueryResult<DashboardStats, Error> {
  return useQuery({
    queryKey: dashboardQueryKeys.stats(),
    queryFn: getDashboardStats,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000, // Refetch every 30 seconds for real-time feel
  });
}

export function useTodaysBookings(): UseQueryResult<TodaysBooking[], Error> {
  return useQuery({
    queryKey: dashboardQueryKeys.bookings(),
    queryFn: getTodaysBookings,
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 15 * 1000, // Refetch every 15 seconds
  });
}

export function useRecentActivity(): UseQueryResult<ActivityItem[], Error> {
  return useQuery({
    queryKey: dashboardQueryKeys.activity(),
    queryFn: getRecentActivity,
    staleTime: 1 * 60 * 1000, // 1 minute
  });
}

export function useAIInsights(): UseQueryResult<AIInsight[], Error> {
  return useQuery({
    queryKey: dashboardQueryKeys.insights(),
    queryFn: getAIInsights,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// ============================================
// Refresh Hook
// ============================================
export function useRefreshDashboard() {
  const queryClient = useQueryClient();
  
  return async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: dashboardQueryKeys.stats() }),
      queryClient.invalidateQueries({ queryKey: dashboardQueryKeys.bookings() }),
      queryClient.invalidateQueries({ queryKey: dashboardQueryKeys.activity() }),
      queryClient.invalidateQueries({ queryKey: dashboardQueryKeys.insights() }),
    ]);
  };
}

// ============================================
// Mock Data (Fallback)
// ============================================
function getMockDashboardStats(): DashboardStats {
  return {
    todayRevenue: {
      value: 12450,
      change: 8.5,
      changeType: 'increase',
      currency: '₹',
    },
    todayBookings: {
      confirmed: 8,
      pending: 2,
      total: 10,
      change: 12.5,
    },
    activeCustomers: {
      total: 156,
      new: 3,
      change: -2.1,
    },
    staffOnDuty: {
      present: 4,
      total: 6,
      onLeave: 2,
    },
    insights: [
      {
        id: '1',
        type: 'ai',
        message: '3 slots empty tomorrow - fill them?',
        action: 'Take Action',
        dismissible: true,
      },
      {
        id: '2',
        type: 'info',
        message: "Priya's birthday next week - send offer?",
        detail: 'Customer loyalty opportunity',
        action: 'View',
        dismissible: true,
      },
    ],
  };
}

function getMockTodaysBookings(): TodaysBooking[] {
  return [
    {
      id: '1',
      customer: {
        id: 'c1',
        name: 'Priya Sharma',
        avatar: undefined,
      },
      service: {
        id: 's1',
        name: 'Hair Cut & Styling',
        duration: 45,
        price: 500,
      },
      time: '10:00 AM',
      status: 'confirmed',
      staff: {
        id: 'st1',
        name: 'Rahul Kumar',
      },
    },
    {
      id: '2',
      customer: {
        id: 'c2',
        name: 'Anjali Patel',
        avatar: undefined,
      },
      service: {
        id: 's2',
        name: 'Facial & Cleanup',
        duration: 60,
        price: 1200,
      },
      time: '10:30 AM',
      status: 'in_progress',
      staff: {
        id: 'st2',
        name: 'Sneha Reddy',
      },
    },
    {
      id: '3',
      customer: {
        id: 'c3',
        name: 'Vikram Singh',
        avatar: undefined,
      },
      service: {
        id: 's3',
        name: 'Beard Trim',
        duration: 20,
        price: 200,
      },
      time: '11:00 AM',
      status: 'pending',
      staff: {
        id: 'st1',
        name: 'Rahul Kumar',
      },
    },
    {
      id: '4',
      customer: {
        id: 'c4',
        name: 'Meera Krishnan',
        avatar: undefined,
      },
      service: {
        id: 's4',
        name: 'Hair Color',
        duration: 120,
        price: 3500,
      },
      time: '11:30 AM',
      status: 'confirmed',
      staff: {
        id: 'st3',
        name: 'Divya Menon',
      },
    },
  ];
}

function getMockRecentActivity(): ActivityItem[] {
  return [
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
      title: 'Staff clocked in',
      description: 'Rahul Kumar started shift at 9:00 AM',
      timestamp: new Date(Date.now() - 60 * 60000),
    },
  ];
}

function getMockAIInsights(): AIInsight[] {
  return [
    {
      id: '1',
      type: 'ai',
      message: '3 slots empty tomorrow - fill them?',
      detail: 'Try WhatsApp blast to regular customers',
      action: 'Take Action',
      dismissible: true,
    },
    {
      id: '2',
      type: 'warning',
      message: 'Revenue down 12% vs last week',
      detail: 'Wednesday was particularly slow',
      action: 'Analyze',
      dismissible: true,
    },
    {
      id: '3',
      type: 'info',
      message: "Priya's birthday next week - send offer?",
      detail: 'Send personalized discount',
      action: 'View',
      dismissible: true,
    },
  ];
}

export default {
  getDashboardStats,
  getTodaysBookings,
  getRecentActivity,
  getAIInsights,
};
