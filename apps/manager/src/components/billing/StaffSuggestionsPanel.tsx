/**
 * StaffSuggestionsPanel Component
 * Displays pending staff discount suggestions with approve/reject actions
 */

import React from 'react';
import { Check, X, Clock, User, AlertCircle, RefreshCw } from 'lucide-react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  Badge,
  Skeleton,
} from '@salon-flow/ui';
import { formatCurrency, formatRelativeTime } from '@salon-flow/shared';
import {
  useStaffSuggestions,
  useApproveSuggestion,
  useRejectSuggestion,
} from '../../hooks/useBilling';
import type { StaffSuggestion, SuggestionStatus } from '../../types/billing';

interface StaffSuggestionsPanelProps {
  onViewAll?: () => void;
  compact?: boolean;
}

const SUGGESTION_TYPE_LABELS: Record<string, string> = {
  discount: 'Discount',
  complimentary: 'Complimentary',
  upgrade: 'Upgrade',
  custom: 'Custom',
};

const STATUS_COLORS: Record<SuggestionStatus, string> = {
  pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  approved: 'bg-green-100 text-green-800 border-green-200',
  rejected: 'bg-red-100 text-red-800 border-red-200',
  expired: 'bg-gray-100 text-gray-800 border-gray-200',
};

export const StaffSuggestionsPanel: React.FC<StaffSuggestionsPanelProps> = ({
  onViewAll,
  compact = false,
}) => {
  const [filter, setFilter] = React.useState<'pending' | 'all'>('pending');

  const { data, isLoading, error, refetch } = useStaffSuggestions(
    filter === 'pending' ? { status: 'pending' } : undefined
  );

  const approveMutation = useApproveSuggestion();
  const rejectMutation = useRejectSuggestion();

  const handleApprove = async (id: string) => {
    try {
      await approveMutation.mutateAsync({ id, data: { approved: true } });
    } catch (err) {
      console.error('Failed to approve suggestion:', err);
    }
  };

  const handleReject = async (id: string, reason?: string) => {
    try {
      await rejectMutation.mutateAsync({
        id,
        data: { approved: false, rejection_reason: reason },
      });
    } catch (err) {
      console.error('Failed to reject suggestion:', err);
    }
  };

  const renderSuggestion = (suggestion: StaffSuggestion) => {
    const discountPercent = suggestion.original_price > 0
      ? ((suggestion.original_price - suggestion.suggested_price) / suggestion.original_price) * 100
      : 0;

    const isExpiringSoon = new Date(suggestion.expires_at).getTime() - Date.now() < 5 * 60 * 1000; // 5 minutes

    return (
      <div
        key={suggestion.id}
        className="border rounded-lg p-4 space-y-3 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
              <User className="h-4 w-4 text-purple-600" />
            </div>
            <div>
              <p className="font-medium text-sm">{suggestion.staff_name}</p>
              <p className="text-xs text-gray-500">
                {formatRelativeTime(suggestion.created_at)}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className={STATUS_COLORS[suggestion.status]}>
              {suggestion.status}
            </Badge>
            {suggestion.status === 'pending' && isExpiringSoon && (
              <AlertCircle className="h-4 w-4 text-red-500" />
            )}
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-3 space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Service</span>
            <span className="font-medium text-sm">{suggestion.service_name || 'N/A'}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Type</span>
            <Badge variant="secondary">
              {SUGGESTION_TYPE_LABELS[suggestion.suggestion_type]}
            </Badge>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Original Price</span>
            <span className="text-sm">{formatCurrency(suggestion.original_price)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Suggested Price</span>
            <span className="font-medium text-green-600">
              {formatCurrency(suggestion.suggested_price)}
              <span className="text-xs text-gray-500 ml-1">
                (-{discountPercent.toFixed(0)}%)
              </span>
            </span>
          </div>
          {suggestion.customer_name && (
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Customer</span>
              <span className="text-sm">{suggestion.customer_name}</span>
            </div>
          )}
        </div>

        <div className="bg-amber-50 rounded-lg p-2">
          <p className="text-sm text-amber-800">
            <span className="font-medium">Reason: </span>
            {suggestion.reason}
          </p>
        </div>

        {suggestion.status === 'pending' && (
          <div className="flex gap-2 pt-2">
            <Button
              variant="default"
              size="sm"
              className="flex-1 bg-green-600 hover:bg-green-700"
              onClick={() => handleApprove(suggestion.id)}
              disabled={approveMutation.isPending}
            >
              <Check className="h-4 w-4 mr-1" />
              Approve
            </Button>
            <Button
              variant="default"
              size="sm"
              className="flex-1 text-red-600 border-red-200 hover:bg-red-50"
              onClick={() => {
                const reason = prompt('Enter rejection reason (optional):');
                handleReject(suggestion.id, reason || undefined);
              }}
              disabled={rejectMutation.isPending}
            >
              <X className="h-4 w-4 mr-1" />
              Reject
            </Button>
          </div>
        )}

        {suggestion.status === 'rejected' && suggestion.rejection_reason && (
          <div className="bg-red-50 rounded-lg p-2">
            <p className="text-sm text-red-800">
              <span className="font-medium">Rejection Reason: </span>
              {suggestion.rejection_reason}
            </p>
          </div>
        )}

        {suggestion.status === 'pending' && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <Clock className="h-3 w-3" />
            <span>
              Expires {formatRelativeTime(suggestion.expires_at)}
            </span>
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Staff Suggestions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
              <Skeleton className="h-20 w-full" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Staff Suggestions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">
            <p className="text-red-500 mb-2">Failed to load suggestions</p>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-4 w-4 mr-1" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const suggestions = data?.items || [];
  const pendingCount = data?.pending_count || 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <div className="flex items-center gap-2">
          <CardTitle className="text-lg">Staff Suggestions</CardTitle>
          {pendingCount > 0 && (
            <Badge variant="danger" className="ml-2">
              {pendingCount} pending
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button            variant={filter === 'pending' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('pending')}
          >
            Pending
          </Button>
          <Button            variant={filter === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('all')}
          >
            All
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {suggestions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No {filter === 'pending' ? 'pending ' : ''}suggestions</p>
          </div>
        ) : (
          <div className="space-y-4">
            {(compact ? suggestions.slice(0, 3) : suggestions).map(renderSuggestion)}
            {compact && suggestions.length > 3 && (
              <Button                variant="outline"
                className="w-full"
                onClick={onViewAll}
              >
                View All ({suggestions.length})
              </Button>
            )}
          </div>
        )}

        {/* Stats Summary */}
        {data && !compact && (
          <div className="mt-6 pt-4 border-t grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-yellow-600">{data.pending_count}</p>
              <p className="text-xs text-gray-500">Pending</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">{data.approved_count}</p>
              <p className="text-xs text-gray-500">Approved</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-red-600">{data.rejected_count}</p>
              <p className="text-xs text-gray-500">Rejected</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default StaffSuggestionsPanel;
