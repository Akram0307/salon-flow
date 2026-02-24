import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth as useSharedAuth } from '@salon-flow/shared';
import { useAuthStore } from '@/stores';
import type { User } from '@salon-flow/shared';

export interface UseAuthReturn {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
}

/**
 * Enhanced auth hook that combines shared auth with local Zustand store
 * Provides seamless integration between Firebase Auth and local state
 */
export const useAuth = (): UseAuthReturn => {
  const navigate = useNavigate();
  const sharedAuth = useSharedAuth();
  const store = useAuthStore();
  const [initialized, setInitialized] = useState(false);

  // Initialize auth state - check for stored token and set loading to false
  useEffect(() => {
    if (!initialized) {
      // If we have a stored token, consider authenticated until proven otherwise
      const hasToken = !!store.accessToken;
      
      // If no token, immediately set loading to false (not authenticated)
      if (!hasToken && store.isLoading) {
        store.setLoading(false);
      }
      
      setInitialized(true);
    }
  }, [initialized, store]);

  // Sync shared auth state with local store
  useEffect(() => {
    if (sharedAuth.user !== store.user) {
      store.setUser(sharedAuth.user);
    }
    if (sharedAuth.isLoading !== store.isLoading && initialized) {
      store.setLoading(sharedAuth.isLoading);
    }
  }, [sharedAuth.user, sharedAuth.isLoading, store, initialized]);

  const login = useCallback(async (email: string, password: string) => {
    try {
      store.setLoading(true);
      store.setError(null);
      await sharedAuth.login(email, password);
      // Tokens will be set by API client interceptors
      navigate('/dashboard');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Login failed';
      store.setError(message);
      throw error;
    } finally {
      store.setLoading(false);
    }
  }, [sharedAuth, store, navigate]);

  const logout = useCallback(async () => {
    try {
      store.setLoading(true);
      await sharedAuth.logout();
      store.logout();
      navigate('/login');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Logout failed';
      store.setError(message);
      throw error;
    } finally {
      store.setLoading(false);
    }
  }, [sharedAuth, store, navigate]);

  const register = useCallback(async (email: string, password: string, name?: string) => {
    try {
      store.setLoading(true);
      store.setError(null);
      await sharedAuth.register(email, password, name);
      navigate('/dashboard');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Registration failed';
      store.setError(message);
      throw error;
    } finally {
      store.setLoading(false);
    }
  }, [sharedAuth, store, navigate]);

  const resetPassword = useCallback(async (email: string) => {
    try {
      store.setLoading(true);
      store.setError(null);
      await sharedAuth.resetPassword(email);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Password reset failed';
      store.setError(message);
      throw error;
    } finally {
      store.setLoading(false);
    }
  }, [sharedAuth, store]);

  return {
    user: store.user,
    isAuthenticated: store.isAuthenticated,
    isLoading: store.isLoading,
    error: store.error,
    login,
    logout,
    register,
    resetPassword,
  };
};

export default useAuth;
