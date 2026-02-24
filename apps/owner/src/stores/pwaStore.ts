import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface OfflineQueueItem {
  id: string;
  type: 'booking' | 'customer' | 'staff' | 'payment' | 'settings';
  action: 'create' | 'update' | 'delete';
  data: any;
  timestamp: number;
  retryCount: number;
}

interface PWAState {
  // Install state
  isInstalled: boolean;
  installPrompt: Event | null;
  
  // Network state
  isOnline: boolean;
  lastSyncTime: number | null;
  
  // Offline queue
  offlineQueue: OfflineQueueItem[];
  isSyncing: boolean;
  
  // Service Worker state
  swRegistration: ServiceWorkerRegistration | null;
  updateAvailable: boolean;
  
  // Actions
  setInstalled: (installed: boolean) => void;
  setInstallPrompt: (prompt: Event | null) => void;
  setOnline: (online: boolean) => void;
  setLastSyncTime: (time: number) => void;
  addToQueue: (item: Omit<OfflineQueueItem, 'id' | 'timestamp' | 'retryCount'>) => void;
  removeFromQueue: (id: string) => void;
  clearQueue: () => void;
  setSyncing: (syncing: boolean) => void;
  incrementRetryCount: (id: string) => void;
  setSWRegistration: (reg: ServiceWorkerRegistration | null) => void;
  setUpdateAvailable: (available: boolean) => void;
  updateApp: () => Promise<void>;
}

export const usePWAStore = create<PWAState>()(
  persist(
    (set, get) => ({
      // Initial state
      isInstalled: false,
      installPrompt: null,
      isOnline: navigator.onLine,
      lastSyncTime: null,
      offlineQueue: [],
      isSyncing: false,
      swRegistration: null,
      updateAvailable: false,

      // Actions
      setInstalled: (installed) => set({ isInstalled: installed }),
      
      setInstallPrompt: (prompt) => set({ installPrompt: prompt }),
      
      setOnline: (online) => set({ isOnline: online }),
      
      setLastSyncTime: (time) => set({ lastSyncTime: time }),
      
      addToQueue: (item) => {
        const newItem: OfflineQueueItem = {
          ...item,
          id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          timestamp: Date.now(),
          retryCount: 0,
        };
        set((state) => ({
          offlineQueue: [...state.offlineQueue, newItem],
        }));
      },
      
      removeFromQueue: (id) => {
        set((state) => ({
          offlineQueue: state.offlineQueue.filter((item) => item.id !== id),
        }));
      },
      
      clearQueue: () => set({ offlineQueue: [] }),
      
      setSyncing: (syncing) => set({ isSyncing: syncing }),
      
      incrementRetryCount: (id) => {
        set((state) => ({
          offlineQueue: state.offlineQueue.map((item) =>
            item.id === id ? { ...item, retryCount: item.retryCount + 1 } : item
          ),
        }));
      },
      
      setSWRegistration: (reg) => set({ swRegistration: reg }),
      
      setUpdateAvailable: (available) => set({ updateAvailable: available }),
      
      updateApp: async () => {
        const { swRegistration } = get();
        if (swRegistration && swRegistration.waiting) {
          // Send skip waiting message to service worker
          swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
          
          // Reload the page to activate new service worker
          window.location.reload();
        }
      },
    }),
    {
      name: 'pwa-storage',
      partialize: (state) => ({
        offlineQueue: state.offlineQueue,
        lastSyncTime: state.lastSyncTime,
      }),
    }
  )
);

export default usePWAStore;
