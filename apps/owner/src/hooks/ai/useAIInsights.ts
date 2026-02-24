/**
 * useAIInsights Hook - Fixed Version
 */

import { useState, useEffect, useCallback } from 'react';
import { aiService } from '../../services/aiService';
import type { AIInsight, MorningPulse, RevenueForecast, ChurnRiskAlert } from '../../types/ai';

export interface UseAIInsightsReturn {
  insights: AIInsight[];
  morningPulse: MorningPulse | null;
  revenueForecast: RevenueForecast | null;
  churnRiskAlerts: ChurnRiskAlert[];
  isLoading: boolean;
  isLoadingPulse: boolean;
  isLoadingForecast: boolean;
  isLoadingChurn: boolean;
  error: string | null;
  unreadCount: number;
  refetch: () => Promise<void>;
  refetchPulse: () => Promise<void>;
  markAsRead: (insightId: string) => void;
  markAllAsRead: () => void;
}

export const useAIInsights = (): UseAIInsightsReturn => {
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [morningPulse, setMorningPulse] = useState<MorningPulse | null>(null);
  const [revenueForecast, setRevenueForecast] = useState<RevenueForecast | null>(null);
  const [churnRiskAlerts, setChurnRiskAlerts] = useState<ChurnRiskAlert[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingPulse, setIsLoadingPulse] = useState(false);
  const [isLoadingForecast, setIsLoadingForecast] = useState(false);
  const [isLoadingChurn, setIsLoadingChurn] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchInsights = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await aiService.getInsights();
      setInsights(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch insights');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchMorningPulse = useCallback(async () => {
    setIsLoadingPulse(true);
    try {
      const data = await aiService.getMorningPulse();
      setMorningPulse(data);
    } catch (err) {
      console.error('Failed to fetch morning pulse:', err);
    } finally {
      setIsLoadingPulse(false);
    }
  }, []);

  const fetchRevenueForecast = useCallback(async () => {
    setIsLoadingForecast(true);
    try {
      const data = await aiService.getRevenueForecast();
      setRevenueForecast(data);
    } catch (err) {
      console.error('Failed to fetch revenue forecast:', err);
    } finally {
      setIsLoadingForecast(false);
    }
  }, []);

  const fetchChurnRisk = useCallback(async () => {
    setIsLoadingChurn(true);
    try {
      const data = await aiService.getChurnRiskAlerts();
      setChurnRiskAlerts(data);
    } catch (err) {
      console.error('Failed to fetch churn risk:', err);
    } finally {
      setIsLoadingChurn(false);
    }
  }, []);

  useEffect(() => {
    fetchInsights();
    fetchMorningPulse();
    fetchRevenueForecast();
    fetchChurnRisk();
  }, [fetchInsights, fetchMorningPulse, fetchRevenueForecast, fetchChurnRisk]);

  const markAsRead = useCallback((insightId: string) => {
    setInsights((prev) =>
      prev.map((insight) =>
        insight.id === insightId ? { ...insight, read: true } : insight
      )
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setInsights((prev) =>
      prev.map((insight) => ({ ...insight, read: true }))
    );
  }, []);

  const unreadCount = insights.filter((i) => !i.read).length;

  return {
    insights,
    morningPulse,
    revenueForecast,
    churnRiskAlerts,
    isLoading,
    isLoadingPulse,
    isLoadingForecast,
    isLoadingChurn,
    error,
    unreadCount,
    refetch: fetchInsights,
    refetchPulse: fetchMorningPulse,
    markAsRead,
    markAllAsRead,
  };
};

export default useAIInsights;
