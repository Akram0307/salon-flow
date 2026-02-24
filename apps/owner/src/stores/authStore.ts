import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { User } from '@salon-flow/shared';

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  accessToken: string | null;
  refreshToken: string | null;
}

export interface AuthActions {
  setUser: (user: User | null) => void;
  setTokens: (accessToken: string, refreshToken?: string) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  login: (user: User, accessToken: string, refreshToken?: string) => void;
  logout: () => void;
  clearError: () => void;
}

export type AuthStore = AuthState & AuthActions;

// Start with isLoading: false to avoid blocking the UI
// The persist middleware will rehydrate the state if there's stored data
const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false, // Changed from true to false
  error: null,
  accessToken: null,
  refreshToken: null,
};

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      ...initialState,

      setUser: (user) => set({
        user,
        isAuthenticated: !!user
      }),

      setTokens: (accessToken, refreshToken) => set({
        accessToken,
        refreshToken: refreshToken || null
      }),

      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error }),

      login: (user, accessToken, refreshToken) => {
        // Also store in localStorage for useAuth hook compatibility
        if (typeof window !== 'undefined') {
          localStorage.setItem('salon_flow_auth_token', accessToken);
          localStorage.setItem('salon_flow_user', JSON.stringify(user));
        }

        return set({
          user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
          accessToken,
          refreshToken: refreshToken || null,
        });
      },

      logout: () => {
        // Clear localStorage items used by useAuth hook
        if (typeof window !== 'undefined') {
          localStorage.removeItem('salon_flow_auth_token');
          localStorage.removeItem('salon_flow_user');
        }
        return set(initialState);
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'salon-flow-auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
);
