/**
 * PriceOverrideDialog Component
 * Dialog for creating price overrides with approval workflow
 */

import React, { useState, useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalTitle,
  ModalDescription,
  ModalFooter,
  Button,
  Input,
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
  Badge,
} from '@salon-flow/ui';
import { formatCurrency } from '@salon-flow/shared';
import { useApprovalRules, useCreatePriceOverride } from '../../hooks/useBilling';
import type { OverrideReasonCode, BillItem } from '../../types/billing';
import { OVERRIDE_REASONS } from '../../types/billing';

interface PriceOverrideDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  item: BillItem | null;
  bookingId?: string;
  onConfirm: (overridePrice: number, reasonCode: OverrideReasonCode, reasonText?: string) => void;
}

export const PriceOverrideDialog: React.FC<PriceOverrideDialogProps> = ({
  open,
  onOpenChange,
  item,
  bookingId,
  onConfirm,
}) => {
  const [newPrice, setNewPrice] = useState<string>('');
  const [reasonCode, setReasonCode] = useState<OverrideReasonCode>('custom');
  const [reasonText, setReasonText] = useState('');
  const [managerPin, setManagerPin] = useState('');
  const [error, setError] = useState<string | null>(null);

  const { data: approvalRules } = useApprovalRules();
  const createOverride = useCreatePriceOverride();

  // Reset state when dialog opens
  useEffect(() => {
    if (open && item) {
      setNewPrice(item.servicePrice.toString());
      setReasonCode('custom');
      setReasonText('');
      setManagerPin('');
      setError(null);
    }
  }, [open, item]);

  if (!item) return null;

  const originalPrice = item.servicePrice;
  const parsedNewPrice = parseFloat(newPrice) || 0;
  const discountPercent = originalPrice > 0
    ? ((originalPrice - parsedNewPrice) / originalPrice) * 100
    : 0;

  // Determine approval threshold
  const getApprovalStatus = () => {
    if (!approvalRules || discountPercent <= 0) {
      return { needsApproval: false, level: 'none' };
    }

    if (discountPercent <= approvalRules.auto_approve_threshold) {
      return { needsApproval: false, level: 'auto' };
    }
    if (discountPercent <= approvalRules.manager_approval_threshold) {
      return { needsApproval: true, level: 'manager' };
    }
    return { needsApproval: true, level: 'owner' };
  };

  const approvalStatus = getApprovalStatus();

  const isValidPrice = parsedNewPrice >= 0 && parsedNewPrice <= originalPrice;
  const isValidReason = reasonText.length >= 10 || reasonCode !== 'custom';
  const isValidPin = !approvalStatus.needsApproval || managerPin.length >= 4;

  const handleConfirm = async () => {
    if (!isValidPrice) {
      setError('Please enter a valid price (0 to original price)');
      return;
    }

    if (!isValidReason) {
      setError('Please provide a reason (at least 10 characters)');
      return;
    }

    if (approvalStatus.needsApproval && !isValidPin) {
      setError('Manager PIN is required for this discount level');
      return;
    }

    try {
      // If we have a booking ID, create the override via API
      if (bookingId) {
        await createOverride.mutateAsync({
          booking_id: bookingId,
          service_id: item.serviceId,
          service_name: item.serviceName,
          original_price: originalPrice,
          new_price: parsedNewPrice,
          reason_code: reasonCode,
          reason_text: reasonText || undefined,
        });
      }

      onConfirm(parsedNewPrice, reasonCode, reasonText || undefined);
      onOpenChange(false);
    } catch (err) {
      setError('Failed to create price override. Please try again.');
    }
  };

  return (
    <Modal open={open} onOpenChange={onOpenChange}>
      <ModalContent className="sm:max-w-md">
        <ModalHeader>
          <ModalTitle className="flex items-center gap-2">
            Price Override
            {approvalStatus.needsApproval && (
              <Badge variant="warning" className="ml-2">
                {approvalStatus.level === 'owner' ? 'Owner Approval' : 'Manager Approval'} Required
              </Badge>
            )}
          </ModalTitle>
          <ModalDescription>
            Adjust the price for {item.serviceName}
          </ModalDescription>
        </ModalHeader>

        <div className="space-y-4 py-4">
          {/* Original Price Display */}
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Original Price</span>
              <span className="font-semibold">{formatCurrency(originalPrice)}</span>
            </div>
          </div>

          {/* New Price Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium">New Price</label>
            <Input
              type="number"
              value={newPrice}
              onChange={(e) => setNewPrice(e.target.value)}
              min={0}
              max={originalPrice}
              step={1}
              className="text-lg font-semibold"
            />
            {isValidPrice && discountPercent > 0 && (
              <div className="flex items-center gap-2 text-sm">
                <Badge variant={discountPercent > 20 ? 'danger' : 'secondary'}>
                  {discountPercent.toFixed(1)}% discount
                </Badge>
                <span className="text-gray-500">
                  Save {formatCurrency(originalPrice - parsedNewPrice)}
                </span>
              </div>
            )}
          </div>

          {/* Reason Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Reason</label>
            <Select
              value={reasonCode}
              onValueChange={(value) => setReasonCode(value as OverrideReasonCode)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select reason" />
              </SelectTrigger>
              <SelectContent>
                {OVERRIDE_REASONS.map((reason) => (
                  <SelectItem key={reason.value} value={reason.value}>
                    {reason.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Custom Reason Text */}
          {(reasonCode === 'custom' || approvalStatus.needsApproval) && (
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Details {approvalStatus.needsApproval && <span className="text-red-500">*</span>}
              </label>
              <Input
                value={reasonText}
                onChange={(e) => setReasonText(e.target.value)}
                placeholder="Explain the reason for this discount..."
                className={reasonText.length > 0 && reasonText.length < 10 ? 'border-yellow-500' : ''}
              />
              {reasonText.length > 0 && reasonText.length < 10 && (
                <p className="text-xs text-yellow-600">
                  {10 - reasonText.length} more characters needed
                </p>
              )}
            </div>
          )}

          {/* Approval Threshold Indicator */}
          {approvalRules && discountPercent > approvalRules.auto_approve_threshold && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
              <div className="flex items-start gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-500 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium text-amber-800">
                    {approvalStatus.level === 'owner' ? 'Owner Approval' : 'Manager Approval'} Required
                  </p>
                  <p className="text-amber-600 mt-1">
                    Discounts over {approvalStatus.level === 'owner'
                      ? `${approvalRules.manager_approval_threshold}%`
                      : `${approvalRules.auto_approve_threshold}%`
                    } require authorization.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Manager PIN Input */}
          {approvalStatus.needsApproval && (
            <div className="space-y-2">
              <label className="text-sm font-medium">
                {approvalStatus.level === 'owner' ? 'Owner' : 'Manager'} PIN <span className="text-red-500">*</span>
              </label>
              <Input
                type="password"
                value={managerPin}
                onChange={(e) => setManagerPin(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="Enter PIN"
                maxLength={6}
                className="text-center text-2xl tracking-widest"
              />
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-600">
              {error}
            </div>
          )}
        </div>

        <ModalFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={!isValidPrice || !isValidReason || !isValidPin || createOverride.isPending}
            className="bg-purple-600 hover:bg-purple-700"
          >
            {createOverride.isPending ? 'Processing...' : 'Confirm Override'}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default PriceOverrideDialog;
