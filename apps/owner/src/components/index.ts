/**
 * Components - Main Export File
 * 
 * Organized by Atomic Design methodology:
 * - Atoms: Basic building blocks
 * - Molecules: Simple combinations
 * - Organisms: Complex components
 * - Templates: Page layouts
 * - Pages: Screen components
 */

// Atoms
export * from './atoms';

// Molecules
export * from './molecules';

// Organisms
export * from './organisms';

// Templates
export * from './templates';

// Legacy component exports (direct file exports)
export { default as Button } from './ui/Button';
export { default as Input } from './ui/Input';
export { default as Badge } from './ui/Badge';
export { default as Avatar } from './ui/Avatar';
export { default as Skeleton } from './ui/Skeleton';
export { default as Card } from './ui/Card';
export { default as Modal } from './ui/Modal';
export { Table } from './ui/Table';
export type { TableColumn, TableProps } from './ui/Table';
export { default as Status } from './ui/Status';

// Dashboard components
export { default as BookingCard } from './dashboard/BookingCard';
export { default as StatCard } from './dashboard/StatCard';
export { default as AIWidget } from './dashboard/AIWidget';
export { default as ActivityFeed } from './dashboard/ActivityFeed';
export type { ActivityItem } from './dashboard/ActivityFeed';
export { default as QuickActions } from './dashboard/QuickActions';
export type { QuickAction } from './dashboard/QuickActions';

// Layout components
export { default as DashboardLayout } from './layout/DashboardLayout';
export { default as LegacyHeader } from './layout/Header';
export { default as Sidebar } from './layout/Sidebar';
