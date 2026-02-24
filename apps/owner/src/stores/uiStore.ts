import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
  duration?: number;
}

export interface ModalState {
  isOpen: boolean;
  type: string | null;
  data?: unknown;
}

export interface UIState {
  theme: 'light' | 'dark' | 'system';
  sidebarOpen: boolean;
  toasts: Toast[];
  modal: ModalState;
  isLoading: boolean;
  loadingMessage: string;
}

export interface UIActions {
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
  openModal: (type: string, data?: unknown) => void;
  closeModal: () => void;
  setLoading: (isLoading: boolean, message?: string) => void;
}

export type UIStore = UIState & UIActions;

const initialState: UIState = {
  theme: 'system',
  sidebarOpen: false,
  toasts: [],
  modal: {
    isOpen: false,
    type: null,
  },
  isLoading: false,
  loadingMessage: '',
};

export const useUIStore = create<UIStore>()(
  persist(
    (set, get) => ({
      ...initialState,
      
      setTheme: (theme) => set({ theme }),
      
      toggleSidebar: () => set((state) => ({ 
        sidebarOpen: !state.sidebarOpen 
      })),
      
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      
      addToast: (toast) => {
        const id = Math.random().toString(36).substring(2, 9);
        const newToast: Toast = { 
          ...toast, 
          id,
          duration: toast.duration || 5000 
        };
        
        set((state) => ({
          toasts: [...state.toasts, newToast],
        }));
        
        // Auto-remove toast after duration
        setTimeout(() => {
          get().removeToast(id);
        }, newToast.duration);
      },
      
      removeToast: (id) => set((state) => ({
        toasts: state.toasts.filter((t) => t.id !== id),
      })),
      
      clearToasts: () => set({ toasts: [] }),
      
      openModal: (type, data) => set({
        modal: {
          isOpen: true,
          type,
          data,
        },
      }),
      
      closeModal: () => set({
        modal: {
          isOpen: false,
          type: null,
          data: undefined,
        },
      }),
      
      setLoading: (isLoading, message = '') => set({
        isLoading,
        loadingMessage: message,
      }),
    }),
    {
      name: 'salon-flow-ui-storage',
      partialize: (state) => ({
        theme: state.theme,
        sidebarOpen: state.sidebarOpen,
      }),
    }
  )
);

export default useUIStore;
