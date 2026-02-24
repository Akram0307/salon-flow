/**
 * Billing Store for Manager PWA
 * Zustand store for billing state management
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  BillItem,
  CustomerInfo,
  PaymentMethodType,
  
} from '../types/billing';

interface BillingState {
  // Customer
  selectedCustomer: CustomerInfo | null;
  setSelectedCustomer: (customer: CustomerInfo | null) => void;

  // Bill Items
  items: BillItem[];
  addItem: (item: BillItem) => void;
  updateItem: (index: number, item: Partial<BillItem>) => void;
  removeItem: (index: number) => void;
  clearItems: () => void;

  // Payment
  paymentMethod: PaymentMethodType;
  setPaymentMethod: (method: PaymentMethodType) => void;
  amountReceived: number;
  setAmountReceived: (amount: number) => void;

  // Discounts
  membershipDiscount: number;
  setMembershipDiscount: (discount: number) => void;
  manualAdjustment: number;
  manualAdjustmentReason: string;
  setManualAdjustment: (amount: number, reason?: string) => void;

  // Override Modal State
  overrideModalOpen: boolean;
  overrideItemIndex: number | null;
  openOverrideModal: (index: number) => void;
  closeOverrideModal: () => void;

  // Calculated values
  getSubtotal: () => number;
  getGstAmount: () => number;
  getGrandTotal: () => number;
  getLoyaltyPoints: () => number;
  getChangeDue: () => number;

  // Reset
  resetBill: () => void;
}

const GST_RATE = 0.05; // 5% GST
const LOYALTY_RATE = 0.1; // 1 point per ₹10 (0.1 per ₹1)

export const useBillingStore = create<BillingState>()(
  persist(
    (set, get) => ({
      // Customer
      selectedCustomer: null,
      setSelectedCustomer: (customer) => set({ selectedCustomer: customer }),

      // Bill Items
      items: [],
      addItem: (item) => set((state) => ({ items: [...state.items, item] })),
      updateItem: (index, item) =>
        set((state) => ({
          items: state.items.map((i, idx) =>
            idx === index ? { ...i, ...item } : i
          ),
        })),
      removeItem: (index) =>
        set((state) => ({
          items: state.items.filter((_, idx) => idx !== index),
        })),
      clearItems: () => set({ items: [] }),

      // Payment
      paymentMethod: 'upi',
      setPaymentMethod: (method) => set({ paymentMethod: method }),
      amountReceived: 0,
      setAmountReceived: (amount) => set({ amountReceived: amount }),

      // Discounts
      membershipDiscount: 0,
      setMembershipDiscount: (discount) => set({ membershipDiscount: discount }),
      manualAdjustment: 0,
      manualAdjustmentReason: '',
      setManualAdjustment: (amount, reason = '') =>
        set({ manualAdjustment: amount, manualAdjustmentReason: reason }),

      // Override Modal State
      overrideModalOpen: false,
      overrideItemIndex: null,
      openOverrideModal: (index) =>
        set({ overrideModalOpen: true, overrideItemIndex: index }),
      closeOverrideModal: () =>
        set({ overrideModalOpen: false, overrideItemIndex: null }),

      // Calculated values
      getSubtotal: () => {
        const { items, membershipDiscount } = get();
        const subtotal = items.reduce((sum, item) => {
          const price = item.overridePrice ?? item.servicePrice;
          return sum + price * item.quantity;
        }, 0);
        return subtotal - membershipDiscount;
      },

      getGstAmount: () => {
        const subtotal = get().getSubtotal();
        return subtotal * GST_RATE;
      },

      getGrandTotal: () => {
        const subtotal = get().getSubtotal();
        const gst = get().getGstAmount();
        const { manualAdjustment } = get();
        return subtotal + gst + manualAdjustment;
      },

      getLoyaltyPoints: () => {
        const grandTotal = get().getGrandTotal();
        return Math.floor(grandTotal * LOYALTY_RATE);
      },

      getChangeDue: () => {
        const { amountReceived } = get();
        const grandTotal = get().getGrandTotal();
        return Math.max(0, amountReceived - grandTotal);
      },

      // Reset
      resetBill: () =>
        set({
          selectedCustomer: null,
          items: [],
          paymentMethod: 'upi',
          amountReceived: 0,
          membershipDiscount: 0,
          manualAdjustment: 0,
          manualAdjustmentReason: '',
          overrideModalOpen: false,
          overrideItemIndex: null,
        }),
    }),
    {
      name: 'billing-storage',
      partialize: (state) => ({
        items: state.items,
        selectedCustomer: state.selectedCustomer,
        paymentMethod: state.paymentMethod,
      }),
    }
  )
);
