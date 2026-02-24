import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores';
import type { User } from '@salon-flow/shared';

export interface UseProtectedRouteReturn {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
}

/**
 * Hook for protecting routes that require authentication
 * Automatically redirects to login if user is not authenticated
 */
export const useProtectedRoute = (): UseProtectedRouteReturn => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, isLoading } = useAuthStore();

  useEffect(() => {
    // Only redirect after auth check is complete
    if (!isLoading && !isAuthenticated) {
      // Save the attempted URL for redirect after login
      const returnUrl = encodeURIComponent(location.pathname + location.search);
      navigate(`/login?returnUrl=${returnUrl}`, { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate, location]);

  return {
    isAuthenticated,
    isLoading,
    user,
  };
};

export default useProtectedRoute;
