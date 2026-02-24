/**
 * Billing Types for Manager PWA
 * Based on backend schemas from services/api/app/schemas/billing.py
 */

// ============== Enums ==============

export type OverrideReasonCode =
  | 'loyalty'
  | 'service_recovery'
  | 'promotion'
  | 'staff_suggestion'
  | 'price_match'
  | 'custom';

export type SuggestionType =
  | 'discount'
  | 'complimentary'
  | 'upgrade'
  | 'custom';

export type SuggestionStatus =
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'expired';

export type PaymentMethodType = 'cash' | 'card' | 'upi' | 'wallet';

// ============== Price Override Types ==============

export interface PriceOverrideBase {
  service_id: string;
  service_name: string;
  original_price: number;
  new_price: number;
  reason_code: OverrideReasonCode;
  reason_text?: string;
  suggested_by?: string;
}

export interface PriceOverrideCreate extends PriceOverrideBase {
  booking_id: string;
}

export interface PriceOverride extends PriceOverrideBase {
  id: string;
  salon_id: string;
  booking_id: string;
  discount_percent: number;
  approved_by: string;
  approved_at: string;
  created_at: string;
  approver_name?: string;
  suggester_name?: string;
}

export interface PriceOverrideListResponse {
  items: PriceOverride[];
  total: number;
  page: number;
  page_size: number;
  total_discount: number;
}

// ============== Staff Suggestion Types ==============

export interface StaffSuggestionBase {
  booking_id: string;
  suggestion_type: SuggestionType;
  service_id?: string;
  service_name?: string;
  original_price: number;
  suggested_price: number;
  discount_percent: number;
  reason: string;
}

export interface StaffSuggestionCreate extends StaffSuggestionBase {}

export interface StaffSuggestion extends StaffSuggestionBase {
  id: string;
  salon_id: string;
  staff_id: string;
  staff_name: string;
  status: SuggestionStatus;
  reviewed_by?: string;
  reviewed_at?: string;
  rejection_reason?: string;
  created_at: string;
  expires_at: string;
  customer_name?: string;
  customer_phone?: string;
  impact_amount: number;
}

export interface StaffSuggestionListResponse {
  items: StaffSuggestion[];
  total: number;
  pending_count: number;
  approved_count: number;
  rejected_count: number;
}

export interface SuggestionApproval {
  approved: boolean;
  rejection_reason?: string;
}

// ============== Billing Types ==============

export interface BillingServiceItem {
  service_id: string;
  service_name: string;
  staff_id: string;
  staff_name: string;
  original_price: number;
  override_price?: number;
  override_id?: string;
  quantity: number;
}

export interface BillingCreate {
  booking_id: string;
  services: BillingServiceItem[];
  membership_discount_percent: number;
  manual_adjustment: number;
  manual_adjustment_reason?: string;
  payment_method: PaymentMethodType;
  amount_received: number;
}

export interface BillResponse {
  id: string;
  salon_id: string;
  booking_id: string;
  invoice_number: string;
  customer_name: string;
  customer_phone: string;
  services: BillingServiceItem[];
  subtotal: number;
  membership_discount: number;
  manual_adjustment: number;
  gst_amount: number;
  gst_percent: number;
  grand_total: number;
  payment_method: PaymentMethodType;
  amount_received: number;
  change_due: number;
  loyalty_points_earned: number;
  created_at: string;
  created_by: string;
}

// ============== Approval Rules Types ==============

export interface ApprovalRules {
  id: string;
  salon_id: string;
  auto_approve_threshold: number;
  manager_approval_threshold: number;
  owner_approval_threshold: number;
  max_discount_per_day: number;
  require_reason_for_discount: boolean;
  allow_staff_suggestions: boolean;
  suggestion_expiry_minutes: number;
  created_at: string;
  updated_at: string;
}

export interface ApprovalRulesUpdate {
  auto_approve_threshold?: number;
  manager_approval_threshold?: number;
  owner_approval_threshold?: number;
  max_discount_per_day?: number;
  require_reason_for_discount?: boolean;
  allow_staff_suggestions?: boolean;
  suggestion_expiry_minutes?: number;
}

// ============== UI State Types ==============

export interface BillItem {
  serviceId: string;
  serviceName: string;
  servicePrice: number;
  staffId: string;
  staffName: string;
  quantity: number;
  overridePrice?: number;
  overrideReason?: OverrideReasonCode;
  overrideReasonText?: string;
}

export interface BillingState {
  selectedCustomer: CustomerInfo | null;
  items: BillItem[];
  paymentMethod: PaymentMethodType;
  amountReceived: number;
  membershipDiscount: number;
  manualAdjustment: number;
  manualAdjustmentReason: string;
}

export interface CustomerInfo {
  id: string;
  name: string;
  phone: string;
  email?: string;
  loyaltyPoints?: number;
  membershipTier?: 'none' | 'bronze' | 'silver' | 'gold' | 'platinum';
  totalVisits?: number;
  totalSpent?: number;
}

// ============== Reason Options ==============

export const OVERRIDE_REASONS: { value: OverrideReasonCode; label: string }[] = [
  { value: 'loyalty', label: 'Loyalty Discount' },
  { value: 'service_recovery', label: 'Service Recovery' },
  { value: 'promotion', label: 'Promotion' },
  { value: 'staff_suggestion', label: 'Staff Suggestion' },
  { value: 'price_match', label: 'Price Match' },
  { value: 'custom', label: 'Custom Reason' },
];

export const PAYMENT_METHODS: { value: PaymentMethodType; label: string; icon: string }[] = [
  { value: 'upi', label: 'UPI', icon: '📱' },
  { value: 'cash', label: 'Cash', icon: '💵' },
  { value: 'card', label: 'Card', icon: '💳' },
  { value: 'wallet', label: 'Wallet', icon: '👛' },
];
