import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { ManagerUser, Alert, DashboardStats } from '../types';

interface ManagerState {
  // User
  user: ManagerUser | null;
  setUser: (user: ManagerUser | null) => void;
  
  // UI State
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  
  // Dashboard
  dashboardStats: DashboardStats | null;
  setDashboardStats: (stats: DashboardStats) => void;
  
  // Alerts
  alerts: Alert[];
  addAlert: (alert: Alert) => void;
  markAlertRead: (id: string) => void;
  clearAlerts: () => void;
  
  // Selected Date (for calendar)
  selectedDate: string;
  setSelectedDate: (date: string) => void;
  
  // Selected Salon
  salonId: string | null;
  setSalonId: (id: string) => void;
}

export const useManagerStore = create<ManagerState>()(
  persist(
    (set) => ({
      // User
      user: null,
      setUser: (user) => set({ user }),
      
      // UI State
      sidebarCollapsed: false,
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      
      // Dashboard
      dashboardStats: null,
      setDashboardStats: (stats) => set({ dashboardStats: stats }),
      
      // Alerts
      alerts: [],
      addAlert: (alert) => set((state) => ({ alerts: [alert, ...state.alerts].slice(0, 50) })),
      markAlertRead: (id) => set((state) => ({
        alerts: state.alerts.map((a) => (a.id === id ? { ...a, read: true } : a)),
      })),
      clearAlerts: () => set({ alerts: [] }),
      
      // Selected Date
      selectedDate: new Date().toISOString().split('T')[0],
      setSelectedDate: (date) => set({ selectedDate: date }),
      
      // Salon
      salonId: null,
      setSalonId: (id) => set({ salonId: id }),
    }),
    {
      name: 'manager-storage',
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        salonId: state.salonId,
      }),
    }
  )
);
