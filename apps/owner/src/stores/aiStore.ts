/**
 * AI Store - Zustand state management for AI features
 * Handles chat history, preferences, caching, and AI state
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { ChatMessage, AIInsight, MorningPulse, SmartAction } from '../types/ai';

// ============================================
// Types
// ============================================
export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
  context?: string;
}

export interface AIPreferences {
  voiceInputEnabled: boolean;
  autoSuggestEnabled: boolean;
  soundEnabled: boolean;
  markdownEnabled: boolean;
  theme: 'light' | 'dark' | 'auto';
  language: 'en' | 'hi' | 'te';
  cacheEnabled: boolean;
  cacheDuration: number; // minutes
}

export interface AIQuota {
  dailyLimit: number;
  usedToday: number;
  resetTime: string;
}

export interface AIState {
  // Chat State
  sessions: ChatSession[];
  activeSessionId: string | null;
  isChatOpen: boolean;
  isStreaming: boolean;
  streamingContent: string;

  // Insights State
  insights: AIInsight[];
  morningPulse: MorningPulse | null;
  unreadInsights: number;
  lastInsightsUpdate: string | null;

  // Smart Actions State
  smartActions: SmartAction[];
  pendingActions: string[];

  // Preferences & Settings
  preferences: AIPreferences;
  quota: AIQuota;

  // Connection State
  isConnected: boolean;
  connectionError: string | null;
  reconnectAttempts: number;

  // Loading States
  isLoadingInsights: boolean;
  isLoadingPulse: boolean;
  isLoadingActions: boolean;
}

export interface AIActions {
  // Chat Actions
  createSession: (title?: string, context?: string) => string;
  deleteSession: (sessionId: string) => void;
  setActiveSession: (sessionId: string | null) => void;
  addMessage: (sessionId: string, message: ChatMessage) => void;
  updateMessage: (sessionId: string, messageId: string, updates: Partial<ChatMessage>) => void;
  clearSession: (sessionId: string) => void;
  setChatOpen: (isOpen: boolean) => void;
  setStreaming: (isStreaming: boolean) => void;
  setStreamingContent: (content: string) => void;
  appendStreamingContent: (content: string) => void;

  // Insights Actions
  setInsights: (insights: AIInsight[]) => void;
  addInsight: (insight: AIInsight) => void;
  dismissInsight: (insightId: string) => void;
  setMorningPulse: (pulse: MorningPulse | null) => void;
  markInsightsRead: () => void;
  setInsightsLoading: (loading: boolean) => void;
  setPulseLoading: (loading: boolean) => void;

  // Smart Actions Actions
  setSmartActions: (actions: SmartAction[]) => void;
  addPendingAction: (actionId: string) => void;
  removePendingAction: (actionId: string) => void;
  completeAction: (actionId: string) => void;
  setActionsLoading: (loading: boolean) => void;

  // Preferences Actions
  updatePreferences: (prefs: Partial<AIPreferences>) => void;
  resetPreferences: () => void;

  // Quota Actions
  incrementQuota: () => void;
  resetQuota: () => void;
  setQuota: (quota: AIQuota) => void;

  // Connection Actions
  setConnected: (connected: boolean) => void;
  setConnectionError: (error: string | null) => void;
  incrementReconnectAttempts: () => void;
  resetReconnectAttempts: () => void;

  // Utility Actions
  clearAll: () => void;
  exportData: () => string;
  importData: (data: string) => void;
}

// ============================================
// Default Values
// ============================================
const defaultPreferences: AIPreferences = {
  voiceInputEnabled: true,
  autoSuggestEnabled: true,
  soundEnabled: false,
  markdownEnabled: true,
  theme: 'auto',
  language: 'en',
  cacheEnabled: true,
  cacheDuration: 60, // 1 hour
};

const defaultQuota: AIQuota = {
  dailyLimit: 100,
  usedToday: 0,
  resetTime: new Date().toISOString(),
};

const createDefaultState = (): AIState => ({
  sessions: [],
  activeSessionId: null,
  isChatOpen: false,
  isStreaming: false,
  streamingContent: '',
  insights: [],
  morningPulse: null,
  unreadInsights: 0,
  lastInsightsUpdate: null,
  smartActions: [],
  pendingActions: [],
  preferences: defaultPreferences,
  quota: defaultQuota,
  isConnected: false,
  connectionError: null,
  reconnectAttempts: 0,
  isLoadingInsights: false,
  isLoadingPulse: false,
  isLoadingActions: false,
});

// ============================================
// Store Creation
// ============================================
export const useAIStore = create<AIState & AIActions>()(
  persist(
    (set, get) => ({
      ...createDefaultState(),

      // Chat Actions
      createSession: (title?: string, context?: string) => {
        const session: ChatSession = {
          id: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          title: title || 'New Chat',
          messages: [],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          context,
        };
        set((state) => ({
          sessions: [session, ...state.sessions],
          activeSessionId: session.id,
        }));
        return session.id;
      },

      deleteSession: (sessionId: string) => {
        set((state) => ({
          sessions: state.sessions.filter((s) => s.id !== sessionId),
          activeSessionId: state.activeSessionId === sessionId 
            ? (state.sessions.find((s) => s.id !== sessionId)?.id || null)
            : state.activeSessionId,
        }));
      },

      setActiveSession: (sessionId: string | null) => {
        set({ activeSessionId: sessionId });
      },

      addMessage: (sessionId: string, message: ChatMessage) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === sessionId
              ? {
                  ...session,
                  messages: [...session.messages, message],
                  updatedAt: new Date().toISOString(),
                }
              : session
          ),
        }));
      },

      updateMessage: (sessionId: string, messageId: string, updates: Partial<ChatMessage>) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === sessionId
              ? {
                  ...session,
                  messages: session.messages.map((msg) =>
                    msg.id === messageId ? { ...msg, ...updates } : msg
                  ),
                  updatedAt: new Date().toISOString(),
                }
              : session
          ),
        }));
      },

      clearSession: (sessionId: string) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === sessionId
              ? { ...session, messages: [], updatedAt: new Date().toISOString() }
              : session
          ),
        }));
      },

      setChatOpen: (isOpen: boolean) => set({ isChatOpen: isOpen }),
      setStreaming: (isStreaming: boolean) => set({ isStreaming: isStreaming }),
      setStreamingContent: (content: string) => set({ streamingContent: content }),
      appendStreamingContent: (content: string) => {
        set((state) => ({ streamingContent: state.streamingContent + content }));
      },

      // Insights Actions
      setInsights: (insights: AIInsight[]) => {
        set({ 
          insights, 
          unreadInsights: insights.filter((i) => !i.read).length,
          lastInsightsUpdate: new Date().toISOString(),
        });
      },

      addInsight: (insight: AIInsight) => {
        set((state) => ({
          insights: [insight, ...state.insights],
          unreadInsights: state.unreadInsights + 1,
        }));
      },

      dismissInsight: (insightId: string) => {
        set((state) => ({
          insights: state.insights.filter((i) => i.id !== insightId),
        }));
      },

      setMorningPulse: (pulse: MorningPulse | null) => {
        set({ morningPulse: pulse });
      },

      markInsightsRead: () => {
        set({ unreadInsights: 0 });
      },

      setInsightsLoading: (loading: boolean) => set({ isLoadingInsights: loading }),
      setPulseLoading: (loading: boolean) => set({ isLoadingPulse: loading }),

      // Smart Actions Actions
      setSmartActions: (actions: SmartAction[]) => {
        set({ smartActions: actions });
      },

      addPendingAction: (actionId: string) => {
        set((state) => ({
          pendingActions: [...state.pendingActions, actionId],
        }));
      },

      removePendingAction: (actionId: string) => {
        set((state) => ({
          pendingActions: state.pendingActions.filter((id) => id !== actionId),
        }));
      },

      completeAction: (actionId: string) => {
        set((state) => ({
          smartActions: state.smartActions.map((action) =>
            action.id === actionId ? { ...action, completed: true, completedAt: new Date().toISOString() } : action
          ),
          pendingActions: state.pendingActions.filter((id) => id !== actionId),
        }));
      },

      setActionsLoading: (loading: boolean) => set({ isLoadingActions: loading }),

      // Preferences Actions
      updatePreferences: (prefs: Partial<AIPreferences>) => {
        set((state) => ({
          preferences: { ...state.preferences, ...prefs },
        }));
      },

      resetPreferences: () => {
        set({ preferences: defaultPreferences });
      },

      // Quota Actions
      incrementQuota: () => {
        set((state) => ({
          quota: { ...state.quota, usedToday: state.quota.usedToday + 1 },
        }));
      },

      resetQuota: () => {
        set({
          quota: {
            ...defaultQuota,
            resetTime: new Date().toISOString(),
          },
        });
      },

      setQuota: (quota: AIQuota) => {
        set({ quota });
      },

      // Connection Actions
      setConnected: (connected: boolean) => set({ isConnected: connected }),
      setConnectionError: (error: string | null) => set({ connectionError: error }),
      incrementReconnectAttempts: () => {
        set((state) => ({ reconnectAttempts: state.reconnectAttempts + 1 }));
      },
      resetReconnectAttempts: () => set({ reconnectAttempts: 0 }),

      // Utility Actions
      clearAll: () => {
        set(createDefaultState());
      },

      exportData: () => {
        const state = get();
        return JSON.stringify({
          sessions: state.sessions,
          preferences: state.preferences,
          quota: state.quota,
        });
      },

      importData: (data: string) => {
        try {
          const parsed = JSON.parse(data);
          set((state) => ({
            sessions: parsed.sessions || state.sessions,
            preferences: { ...state.preferences, ...parsed.preferences },
            quota: { ...state.quota, ...parsed.quota },
          }));
        } catch (error) {
          console.error('Failed to import AI data:', error);
        }
      },
    }),
    {
      name: 'salon-flow-ai-store',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        sessions: state.sessions,
        preferences: state.preferences,
        quota: state.quota,
      }),
    }
  )
);

// ============================================
// Selectors
// ============================================
export const selectActiveSession = (state: AIState & AIActions) => {
  if (!state.activeSessionId) return null;
  return state.sessions.find((s) => s.id === state.activeSessionId) || null;
};

export const selectSessionMessages = (state: AIState & AIActions, sessionId: string) => {
  const session = state.sessions.find((s) => s.id === sessionId);
  return session?.messages || [];
};

export const selectHighPriorityInsights = (state: AIState & AIActions) => {
  return state.insights.filter((i) => i.priority === 'high');
};

export const selectUnreadInsightsCount = (state: AIState & AIActions) => {
  return state.unreadInsights;
};

export const selectQuotaRemaining = (state: AIState & AIActions) => {
  return Math.max(0, state.quota.dailyLimit - state.quota.usedToday);
};

export default useAIStore;
