/**
 * Billing Hooks for Manager PWA
 * React Query hooks for billing API operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@salon-flow/shared';
import type {
  PriceOverride,
  PriceOverrideCreate,
  PriceOverrideListResponse,
  StaffSuggestion,
  StaffSuggestionListResponse,
  SuggestionApproval,
  BillResponse,
  BillingCreate,
  ApprovalRules,
  ApprovalRulesUpdate,
} from '../types/billing';

// ============== Billing Endpoints ==============
const BILLING_ENDPOINTS = {
  OVERRIDES: '/billing/overrides',
  OVERRIDE: (id: string) => `/billing/overrides/${id}`,
  SUGGESTIONS: '/billing/suggestions',
  SUGGESTION_APPROVE: (id: string) => `/billing/suggestions/${id}/approve`,
  SUGGESTION_REJECT: (id: string) => `/billing/suggestions/${id}/reject`,
  BILLS: '/billing/bills',
  BILL: (id: string) => `/billing/bills/${id}`,
  RULES: '/billing/rules',
};

// ============== Price Override Hooks ==============

/**
 * Fetch list of price overrides
 */
export function usePriceOverrides(params?: {
  page?: number;
  page_size?: number;
  start_date?: string;
  end_date?: string;
}) {
  return useQuery<PriceOverrideListResponse>({
    queryKey: ['price-overrides', params],
    queryFn: () => api.get(BILLING_ENDPOINTS.OVERRIDES, { params }),
  });
}

/**
 * Create a new price override
 */
export function useCreatePriceOverride() {
  const queryClient = useQueryClient();

  return useMutation<PriceOverride, Error, PriceOverrideCreate>({
    mutationFn: (data) => api.post(BILLING_ENDPOINTS.OVERRIDES, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['price-overrides'] });
    },
  });
}

// ============== Staff Suggestion Hooks ==============

/**
 * Fetch list of staff suggestions
 */
export function useStaffSuggestions(params?: {
  status?: 'pending' | 'approved' | 'rejected' | 'expired';
  page?: number;
  page_size?: number;
}) {
  return useQuery<StaffSuggestionListResponse>({
    queryKey: ['staff-suggestions', params],
    queryFn: () => api.get(BILLING_ENDPOINTS.SUGGESTIONS, { params }),
    refetchInterval: 30000, // Refresh every 30 seconds for pending suggestions
  });
}

/**
 * Approve a staff suggestion
 */
export function useApproveSuggestion() {
  const queryClient = useQueryClient();

  return useMutation<StaffSuggestion, Error, { id: string; data?: SuggestionApproval }>({
    mutationFn: ({ id, data }) => api.post(BILLING_ENDPOINTS.SUGGESTION_APPROVE(id), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff-suggestions'] });
    },
  });
}

/**
 * Reject a staff suggestion
 */
export function useRejectSuggestion() {
  const queryClient = useQueryClient();

  return useMutation<StaffSuggestion, Error, { id: string; data: SuggestionApproval }>({
    mutationFn: ({ id, data }) => api.post(BILLING_ENDPOINTS.SUGGESTION_REJECT(id), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff-suggestions'] });
    },
  });
}

// ============== Bill Hooks ==============

/**
 * Generate a new bill
 */
export function useCreateBill() {
  const queryClient = useQueryClient();

  return useMutation<BillResponse, Error, BillingCreate>({
    mutationFn: (data) => api.post(BILLING_ENDPOINTS.BILLS, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookings'] });
      queryClient.invalidateQueries({ queryKey: ['payments'] });
    },
  });
}

/**
 * Get bill by ID
 */
export function useBill(id: string) {
  return useQuery<BillResponse>({
    queryKey: ['bill', id],
    queryFn: () => api.get(BILLING_ENDPOINTS.BILL(id)),
    enabled: !!id,
  });
}

// ============== Approval Rules Hooks ==============

/**
 * Get approval rules for salon
 */
export function useApprovalRules() {
  return useQuery<ApprovalRules>({
    queryKey: ['approval-rules'],
    queryFn: () => api.get(BILLING_ENDPOINTS.RULES),
  });
}

/**
 * Update approval rules
 */
export function useUpdateApprovalRules() {
  const queryClient = useQueryClient();

  return useMutation<ApprovalRules, Error, ApprovalRulesUpdate>({
    mutationFn: (data) => api.put(BILLING_ENDPOINTS.RULES, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['approval-rules'] });
    },
  });
}
