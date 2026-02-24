/**
 * useSmartActions Hook - Fixed Version
 */

import { useState, useCallback } from 'react';
import { aiService } from '../../services/aiService';
import type { SmartAction, SmartReplyContext } from '../../types/ai';

export interface CampaignParams {
  type: 'birthday' | 'promotional' | 'rebooking' | 'winback' | 'festival';
  target_segment: string;
  occasion?: string;
}

export interface UseSmartActionsReturn {
  actions: SmartAction[];
  isLoading: boolean;
  error: string | null;
  generateCampaign: (params: CampaignParams) => Promise<void>;
  getSmartReplies: (context: SmartReplyContext) => Promise<string[]>;
  executeAction: (actionId: string) => Promise<void>;
  dismissAction: (actionId: string) => void;
}

export const useSmartActions = (): UseSmartActionsReturn => {
  const [actions, setActions] = useState<SmartAction[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateCampaign = useCallback(async (params: CampaignParams) => {
    setIsLoading(true);
    setError(null);

    try {
      const campaign = await aiService.generateCampaign(params);
      const newAction: SmartAction = {
        id: `action_${Date.now()}`,
        type: 'campaign',
        title: 'New Campaign Generated',
        description: campaign.message,
        priority: 'medium',
        status: 'pending',
        createdAt: new Date().toISOString(),
        params: { campaign },
      };
      setActions((prev) => [newAction, ...prev]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate campaign');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getSmartReplies = useCallback(async (context: SmartReplyContext): Promise<string[]> => {
    try {
      return await aiService.getSmartReplies(context.customer_name || '', context.last_message || '');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get smart replies');
      return [];
    }
  }, []);

  const executeAction = useCallback(async (actionId: string) => {
    setActions((prev) =>
      prev.map((action) =>
        action.id === actionId ? { ...action, status: 'completed' as const } : action
      )
    );
  }, []);

  const dismissAction = useCallback((actionId: string) => {
    setActions((prev) => prev.filter((action) => action.id !== actionId));
  }, []);

  return {
    actions,
    isLoading,
    error,
    generateCampaign,
    getSmartReplies,
    executeAction,
    dismissAction,
  };
};

export default useSmartActions;
