/**
 * Organisms - Complex components
 * Business logic and feature components for the Salon Flow Owner PWA
 */

// Navigation
export { TabBar, type TabId } from './TabBar';

// Modals
export { BottomSheet } from './BottomSheet';

// AI Components
export { InsightsBar, type Insight, type InsightType, type InsightsBarProps } from './InsightsBar';

// Calendar
export { BookingCalendar, type CalendarBooking, type BookingStatus, type ViewMode, type BookingCalendarProps } from './BookingCalendar';

// Re-export existing dashboard components
export { default as AIWidget } from '../dashboard/AIWidget';
export { default as ActivityFeed } from '../dashboard/ActivityFeed';
export { default as QuickActions } from '../dashboard/QuickActions';
