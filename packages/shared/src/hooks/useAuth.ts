import { useState, useEffect, useCallback } from 'react';
import type { User, AuthState } from '../types';
import { apiClient } from '../api/client';

export interface UseAuthReturn extends AuthState {
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
}

const AUTH_TOKEN_KEY = 'salon_flow_auth_token';
const USER_KEY = 'salon_flow_user';

export const useAuth = (): UseAuthReturn => {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  });

  // Initialize auth state from localStorage
  useEffect(() => {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    const userJson = localStorage.getItem(USER_KEY);

    if (token && userJson) {
      try {
        const user: User = JSON.parse(userJson);
        setState({
          user,
          isLoading: false,
          isAuthenticated: true,
        });
      } catch {
        // Invalid stored data
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        setState({
          user: null,
          isLoading: false,
          isAuthenticated: false,
        });
      }
    } else {
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
      });
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const response = await apiClient.post('/auth/login', {
        email,
        password,
      });

      const { access_token, user } = response.data;

      // Store token and user
      localStorage.setItem(AUTH_TOKEN_KEY, access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(user));

      setState({
        user,
        isLoading: false,
        isAuthenticated: true,
      });
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'Login failed';
      setState(prev => ({ 
        ...prev, 
        isLoading: false, 
        isAuthenticated: false,
        error: message 
      }));
      throw new Error(message);
    }
  }, []);

  const register = useCallback(async (email: string, password: string, name?: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const response = await apiClient.post('/auth/register', {
        email,
        password,
        name,
      });

      const { access_token, user } = response.data;

      // Store token and user
      localStorage.setItem(AUTH_TOKEN_KEY, access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(user));

      setState({
        user,
        isLoading: false,
        isAuthenticated: true,
      });
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'Registration failed';
      setState(prev => ({ 
        ...prev, 
        isLoading: false,
        error: message 
      }));
      throw new Error(message);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      // Call backend logout if needed
      await apiClient.post('/auth/logout').catch(() => {
        // Ignore logout API errors
      });
    } finally {
      // Always clear local storage
      localStorage.removeItem(AUTH_TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
      });
    }
  }, []);

  const resetPassword = useCallback(async (email: string) => {
    try {
      await apiClient.post('/auth/reset-password', { email });
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'Password reset failed';
      throw new Error(message);
    }
  }, []);

  return {
    error: state.error || null,
    user: state.user,
    isLoading: state.isLoading,
    isAuthenticated: state.isAuthenticated,
    login,
    register,
    logout,
    resetPassword,
  };
};
