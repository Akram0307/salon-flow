// @salon-flow/ui - Main exports

// ============== Components ==============
export * from './components';

// ============== Layouts ==============
export { DashboardLayout, defaultNavItems } from './layouts/DashboardLayout';
export type { NavItem, DashboardLayoutProps } from './layouts/DashboardLayout';

// ============== Utilities ==============
export { cn, formatBytes, capitalize, generateId, debounce, throttle } from './lib/utils';
