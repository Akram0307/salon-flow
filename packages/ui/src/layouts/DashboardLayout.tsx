import React from 'react';
import { cn } from '../lib/utils';
import { 
  Home, 
  Calendar, 
  Users, 
  UserCircle, 
  BarChart3, 
  CreditCard, 
  MessageSquare, 
  Settings,
  Menu,
  X,
  Bell,
  Search,
  ChevronDown,
  LogOut,
  HelpCircle
} from 'lucide-react';
import { Avatar } from '../components/Avatar';
import { Badge } from '../components/Badge';

// Types
interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path: string;
  badge?: number;
  children?: NavItem[];
}

interface DashboardLayoutProps {
  children: React.ReactNode;
  salonName?: string;
  userName?: string;
  userRole?: string;
  userAvatar?: string;
  navItems?: NavItem[];
  activePath?: string;
  onNavigate?: (path: string) => void;
  onLogout?: () => void;
  notifications?: { id: string; title: string; time: string; unread: boolean }[];
}

// Default navigation items
const defaultNavItems: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: <Home className="h-5 w-5" />, path: '/' },
  { id: 'bookings', label: 'Bookings', icon: <Calendar className="h-5 w-5" />, path: '/bookings' },
  { id: 'customers', label: 'Customers', icon: <Users className="h-5 w-5" />, path: '/customers' },
  { id: 'staff', label: 'Staff', icon: <UserCircle className="h-5 w-5" />, path: '/staff' },
  { id: 'analytics', label: 'Analytics', icon: <BarChart3 className="h-5 w-5" />, path: '/analytics' },
  { id: 'payments', label: 'Payments', icon: <CreditCard className="h-5 w-5" />, path: '/payments' },
  { id: 'ai', label: 'AI Assistant', icon: <MessageSquare className="h-5 w-5" />, path: '/ai' },
  { id: 'settings', label: 'Settings', icon: <Settings className="h-5 w-5" />, path: '/settings' },
];

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  salonName = 'Salon Flow',
  userName = 'User',
  userRole = 'Owner',
  userAvatar,
  navItems = defaultNavItems,
  activePath = '/',
  onNavigate,
  onLogout,
  notifications = [],
}) => {
  const [sidebarOpen, setSidebarOpen] = React.useState(false);
  const [userMenuOpen, setUserMenuOpen] = React.useState(false);
  const [notificationsOpen, setNotificationsOpen] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState('');
  
  const unreadCount = notifications.filter(n => n.unread).length;
  
  const handleNavClick = (path: string) => {
    onNavigate?.(path);
    setSidebarOpen(false);
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform transition-transform duration-200 ease-in-out lg:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">SF</span>
              </div>
              <span className="font-semibold text-gray-900">{salonName}</span>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-1 rounded-md hover:bg-gray-100"
            >
              <X className="h-5 w-5 text-gray-500" />
            </button>
          </div>
          
          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.path)}
                className={cn(
                  'w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  activePath === item.path || activePath.startsWith(item.path + '/')
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )}
              >
                <div className="flex items-center space-x-3">
                  <span className={cn(
                    activePath === item.path || activePath.startsWith(item.path + '/')
                      ? 'text-primary-600'
                      : 'text-gray-400'
                  )}>
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </div>
                {item.badge !== undefined && item.badge > 0 && (
                  <Badge variant="default" size="sm">{item.badge}</Badge>
                )}
              </button>
            ))}
          </nav>
          
          {/* Help & Logout */}
          <div className="p-3 border-t border-gray-200">
            <button
              className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
            >
              <HelpCircle className="h-5 w-5 text-gray-400" />
              <span>Help & Support</span>
            </button>
            {onLogout && (
              <button
                onClick={onLogout}
                className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm text-red-600 hover:bg-red-50 transition-colors"
              >
                <LogOut className="h-5 w-5" />
                <span>Logout</span>
              </button>
            )}
          </div>
        </div>
      </aside>
      
      {/* Main content */}
      <div className="lg:pl-64">
        {/* Header */}
        <header className="sticky top-0 z-30 h-16 bg-white border-b border-gray-200">
          <div className="flex items-center justify-between h-full px-4 sm:px-6">
            {/* Mobile menu button & Search */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-md hover:bg-gray-100"
              >
                <Menu className="h-5 w-5 text-gray-500" />
              </button>
              
              {/* Search */}
              <div className="hidden sm:block relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-64 lg:w-80 h-10 pl-10 pr-4 rounded-lg border border-gray-200 bg-gray-50 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent focus:bg-white transition-all"
                />
              </div>
            </div>
            
            {/* Right side actions */}
            <div className="flex items-center space-x-3">
              {/* Notifications */}
              <div className="relative">
                <button
                  onClick={() => setNotificationsOpen(!notificationsOpen)}
                  className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <Bell className="h-5 w-5 text-gray-500" />
                  {unreadCount > 0 && (
                    <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                      {unreadCount}
                    </span>
                  )}
                </button>
                
                {notificationsOpen && notifications.length > 0 && (
                  <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <h3 className="font-semibold text-gray-900">Notifications</h3>
                    </div>
                    <div className="max-h-64 overflow-y-auto">
                      {notifications.map((notification) => (
                        <div
                          key={notification.id}
                          className={cn(
                            'px-4 py-3 hover:bg-gray-50 cursor-pointer',
                            notification.unread && 'bg-primary-50/50'
                          )}
                        >
                          <p className="text-sm text-gray-900">{notification.title}</p>
                          <p className="text-xs text-gray-500 mt-1">{notification.time}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              {/* User menu */}
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center space-x-2 p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <Avatar name={userName} src={userAvatar} size="sm" />
                  <span className="hidden sm:block text-sm font-medium text-gray-700">{userName}</span>
                  <ChevronDown className="h-4 w-4 text-gray-400" />
                </button>
                
                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <p className="font-medium text-gray-900">{userName}</p>
                      <p className="text-sm text-gray-500">{userRole}</p>
                    </div>
                    <button
                      onClick={() => {
                        handleNavClick('/settings');
                        setUserMenuOpen(false);
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      Profile Settings
                    </button>
                    {onLogout && (
                      <button
                        onClick={() => {
                          onLogout();
                          setUserMenuOpen(false);
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                      >
                        Logout
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>
        
        {/* Page content */}
        <main className="p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
};

export { DashboardLayout, defaultNavItems };
export type { NavItem, DashboardLayoutProps };
export default DashboardLayout;
