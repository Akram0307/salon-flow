import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { ProtectedRoute } from '@/components/auth';
import { InstallPrompt, OfflineBanner } from '@/components/pwa';
import { OnboardingLayout } from '@/components/templates/OnboardingLayout';
import LoginPage from './pages/auth/LoginPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import RegisterPage from './pages/auth/RegisterPage';
import DashboardPage from './pages/DashboardPage';

// Settings Pages
import {
  SettingsPage,
  ProfilePage,
  StaffSettingsPage,
  ServicesSettingsPage,
  NotificationsSettingsPage,
  BillingSettingsPage,
  IntegrationsPage,
} from './pages/settings';

// Onboarding Steps
import Step1Salon from './pages/onboarding/Step1Salon';
import Step2Layout from './pages/onboarding/Step2Layout';
import Step3Services from './pages/onboarding/Step3Services';
import Step4Staff from './pages/onboarding/Step4Staff';
import Step5Hours from './pages/onboarding/Step5Hours';
import Complete from './pages/onboarding/Complete';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

// Placeholder Pages - To be implemented in future tasks
const BookingsPage: React.FC = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold text-gray-900">Bookings</h1>
    <p className="text-gray-500 mt-2">Manage your salon's bookings.</p>
  </div>
);

const CustomersPage: React.FC = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold text-gray-900">Customers</h1>
    <p className="text-gray-500 mt-2">View and manage customer profiles.</p>
  </div>
);

const StaffPage: React.FC = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold text-gray-900">Staff</h1>
    <p className="text-gray-500 mt-2">Manage your team members.</p>
  </div>
);

const AnalyticsPage: React.FC = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
    <p className="text-gray-500 mt-2">View business insights and reports.</p>
  </div>
);

// Settings Layout Wrapper
const SettingsLayout: React.FC = () => (
  <SettingsPage />
);

// Main App Component
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {/* PWA Components */}
        <OfflineBanner />
        <InstallPrompt />
        
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          
          {/* Onboarding Routes - Protected */}
          <Route
            path="/onboarding"
            element={
              <ProtectedRoute>
                <OnboardingLayout><Outlet /></OnboardingLayout>
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/onboarding/step-1" replace />} />
            <Route path="step-1" element={<Step1Salon />} />
            <Route path="step-2" element={<Step2Layout />} />
            <Route path="step-3" element={<Step3Services />} />
            <Route path="step-4" element={<Step4Staff />} />
            <Route path="step-5" element={<Step5Hours />} />
            <Route path="complete" element={<Complete />} />
          </Route>
          
          {/* Protected Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/bookings"
            element={
              <ProtectedRoute>
                <BookingsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/customers"
            element={
              <ProtectedRoute>
                <CustomersPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/staff"
            element={
              <ProtectedRoute>
                <StaffPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <AnalyticsPage />
              </ProtectedRoute>
            }
          />
          
          {/* Settings Routes */}
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <SettingsLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/settings/profile" replace />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="staff" element={<StaffSettingsPage />} />
            <Route path="services" element={<ServicesSettingsPage />} />
            <Route path="notifications" element={<NotificationsSettingsPage />} />
            <Route path="billing" element={<BillingSettingsPage />} />
            <Route path="integrations" element={<IntegrationsPage />} />
          </Route>
          
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
