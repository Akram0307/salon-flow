import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom'
import IntegrationsPage from './pages/Settings/IntegrationsPage'

const queryClient = new QueryClient()

// Navigation Component
const Navigation: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/bookings', label: 'Bookings', icon: '📅' },
    { path: '/customers', label: 'Customers', icon: '👥' },
    { path: '/staff', label: 'Staff', icon: '💇' },
    { path: '/analytics', label: 'Analytics', icon: '📈' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
  ]

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <span className="text-2xl">💇</span>
            <span className="text-xl font-bold text-purple-600">Salon Flow</span>
            <span className="text-sm text-gray-400 ml-2">Owner Portal</span>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-purple-100 text-purple-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`
                }
              >
                <span className="mr-1">{item.icon}</span>
                {item.label}
              </NavLink>
            ))}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  `block px-4 py-2 rounded-lg text-sm font-medium ${
                    isActive
                      ? 'bg-purple-100 text-purple-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`
                }
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </NavLink>
            ))}
          </div>
        )}
      </div>
    </nav>
  )
}

// Dashboard Placeholder
const DashboardPage: React.FC = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">Dashboard</h1>
    <div className="grid md:grid-cols-3 gap-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900">Today's Bookings</h3>
        <p className="text-3xl font-bold text-purple-600 mt-2">24</p>
        <p className="text-sm text-gray-500 mt-1">+12% from yesterday</p>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900">Revenue Today</h3>
        <p className="text-3xl font-bold text-green-600 mt-2">₹12,450</p>
        <p className="text-sm text-gray-500 mt-1">+8% from yesterday</p>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900">Active Customers</h3>
        <p className="text-3xl font-bold text-blue-600 mt-2">156</p>
        <p className="text-sm text-gray-500 mt-1">+5 this week</p>
      </div>
    </div>
  </div>
)

// Settings Page with Sub-navigation
const SettingsPage: React.FC = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold text-gray-900 mb-6">Settings</h1>
    
    <div className="flex flex-wrap gap-2 mb-6">
      <NavLink
        to="/settings"
        end
        className={({ isActive }) =>
          `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            isActive
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`
        }
      >
        General
      </NavLink>
      <NavLink
        to="/settings/integrations"
        className={({ isActive }) =>
          `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            isActive
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`
        }
      >
        Integrations
      </NavLink>
      <NavLink
        to="/settings/billing"
        className={({ isActive }) =>
          `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            isActive
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`
        }
      >
        Billing
      </NavLink>
      <NavLink
        to="/settings/team"
        className={({ isActive }) =>
          `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            isActive
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`
        }
      >
        Team
      </NavLink>
    </div>
    
    <Routes>
      <Route index element={<GeneralSettings />} />
      <Route path="integrations" element={<IntegrationsPage />} />
      <Route path="billing" element={<BillingSettings />} />
      <Route path="team" element={<TeamSettings />} />
    </Routes>
  </div>
)

// Placeholder Settings Pages
const GeneralSettings: React.FC = () => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <h2 className="text-xl font-semibold text-gray-900 mb-4">General Settings</h2>
    <p className="text-gray-500">Configure your salon's basic information.</p>
  </div>
)

const BillingSettings: React.FC = () => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <h2 className="text-xl font-semibold text-gray-900 mb-4">Billing Settings</h2>
    <p className="text-gray-500">Manage your subscription and payment methods.</p>
  </div>
)

const TeamSettings: React.FC = () => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <h2 className="text-xl font-semibold text-gray-900 mb-4">Team Settings</h2>
    <p className="text-gray-500">Manage team members and permissions.</p>
  </div>
)

// Placeholder Pages
const BookingsPage: React.FC = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold text-gray-900">Bookings</h1>
    <p className="text-gray-500 mt-2">Manage your salon's bookings.</p>
  </div>
)

const CustomersPage: React.FC = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold text-gray-900">Customers</h1>
    <p className="text-gray-500 mt-2">View and manage customer profiles.</p>
  </div>
)

const StaffPage: React.FC = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold text-gray-900">Staff</h1>
    <p className="text-gray-500 mt-2">Manage your team members.</p>
  </div>
)

const AnalyticsPage: React.FC = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
    <p className="text-gray-500 mt-2">View business insights and reports.</p>
  </div>
)

// Main App
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
          <Navigation />
          
          <main>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/bookings" element={<BookingsPage />} />
              <Route path="/customers" element={<CustomersPage />} />
              <Route path="/staff" element={<StaffPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/settings/*" element={<SettingsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          
          <footer className="text-center py-6 text-gray-400 text-sm">
            <p>AI-powered Salon Management SaaS</p>
            <p className="mt-1">Environment: Development</p>
          </footer>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
