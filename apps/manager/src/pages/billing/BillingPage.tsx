/**
 * BillingPage - POS/Billing Interface for Manager PWA
 * Service selection, customer management, staff assignment, bill generation
 */

import React, { useState, useMemo } from 'react';
import {
  Search,
  Plus,
  User,
  Trash2,
  Edit3,
  CreditCard,
  Check,
  X,
  RefreshCw,
  ShoppingCart,
} from 'lucide-react';
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Badge,
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
  Modal,
  ModalContent,
  ModalHeader,
  ModalTitle,
  ModalDescription,
  ModalFooter,
  Skeleton,
} from '@salon-flow/ui';
import { formatCurrency, formatPhone } from '@salon-flow/shared';
import { useServices } from '@salon-flow/shared';
import { useStaffList } from '@salon-flow/shared';
import { useCustomers, useCreateCustomer } from '@salon-flow/shared';
import { useBillingStore } from '../../store/useBillingStore';
import { useCreateBill, useApprovalRules } from '../../hooks/useBilling';
import { BillSummary } from '../../components/billing/BillSummary';
import { PriceOverrideDialog } from '../../components/billing/PriceOverrideDialog';
import type {
  BillItem,
  
  
  OverrideReasonCode,
} from '../../types/billing';
import { PAYMENT_METHODS } from '../../types/billing';

export const BillingPage: React.FC = () => {
  // State
  const [serviceSearch, setServiceSearch] = useState('');
  const [customerSearch, setCustomerSearch] = useState('');
  const [showNewCustomer, setShowNewCustomer] = useState(false);
  const [showBillPreview, setShowBillPreview] = useState(false);
  const [newCustomerData, setNewCustomerData] = useState({
    name: '',
    phone: '',
    email: '',
  });

  // Store
  const {
    selectedCustomer,
    setSelectedCustomer,
    items,
    addItem,
    updateItem,
    removeItem,
    clearItems,
    paymentMethod,
    setPaymentMethod,
    amountReceived,
    setAmountReceived,
    membershipDiscount,
    overrideModalOpen,
    overrideItemIndex,
    openOverrideModal,
    closeOverrideModal,
    getSubtotal,
    getGstAmount,
    getGrandTotal,
    getLoyaltyPoints,
    getChangeDue,
    resetBill,
  } = useBillingStore();

  // Queries
  const { data: servicesData, isLoading: servicesLoading } = useServices();
  const { data: staffData } = useStaffList();
  const { data: customersData, refetch: refetchCustomers } = useCustomers(
    customerSearch ? { search: customerSearch } : undefined
  );
  const { data: _approvalRules } = useApprovalRules();

  // Mutations
  const createBill = useCreateBill();
  const createCustomer = useCreateCustomer();

  // Derived data
  const services = servicesData || [];
  const staff = staffData || [];
  const customers = customersData || [];

  const filteredServices = useMemo(() => {
    if (!serviceSearch) return services;
    const search = serviceSearch.toLowerCase();
    return services.filter(
      (s: any) =>
        s.name.toLowerCase().includes(search) ||
        s.category?.toLowerCase().includes(search)
    );
  }, [services, serviceSearch]);

  // Calculated values
  const subtotal = getSubtotal();
  const gstAmount = getGstAmount();
  const grandTotal = getGrandTotal();
  const loyaltyPoints = getLoyaltyPoints();
  const changeDue = getChangeDue();

  // Handlers
  const handleAddService = (service: any) => {
    const newItem: BillItem = {
      serviceId: service.id,
      serviceName: service.name,
      servicePrice: service.price,
      staffId: staff[0]?.id || '',
      staffName: staff[0]?.name || `${staff[0]?.firstName || ''} ${staff[0]?.lastName || ''}`.trim(),
      quantity: 1,
    };
    addItem(newItem);
    setServiceSearch('');
  };

  const handleStaffChange = (index: number, staffId: string) => {
    const selectedStaff = staff.find((s: any) => s.id === staffId);
    if (selectedStaff) {
      updateItem(index, {
        staffId: selectedStaff.id,
        staffName: selectedStaff.name || `${selectedStaff.firstName || ''} ${selectedStaff.lastName || ''}`.trim(),
      });
    }
  };

  const handleOverrideConfirm = (
    overridePrice: number,
    reasonCode: OverrideReasonCode,
    reasonText?: string
  ) => {
    if (overrideItemIndex !== null) {
      updateItem(overrideItemIndex, {
        overridePrice,
        overrideReason: reasonCode,
        overrideReasonText: reasonText,
      });
    }
    closeOverrideModal();
  };

  const handleCreateCustomer = async () => {
    if (!newCustomerData.name || !newCustomerData.phone) return;

    try {
      // Split name into firstName and lastName for CreateCustomerData
      const nameParts = newCustomerData.name.trim().split(/\s+/);
      const firstName = nameParts[0] || '';
      const lastName = nameParts.slice(1).join(' ') || '';
      
      const customer = await createCustomer.mutateAsync({
        firstName,
        lastName,
        phone: newCustomerData.phone,
        email: newCustomerData.email || undefined,
      });

      setSelectedCustomer({
        id: customer.id,
        name: customer.name,
        phone: customer.phone,
        email: customer.email,
        loyaltyPoints: customer.loyaltyPoints || 0,
        membershipTier: customer.membershipTier || 'none',
        totalVisits: customer.totalVisits || 0,
        totalSpent: customer.totalSpent || 0,
      });

      setShowNewCustomer(false);
      setNewCustomerData({ name: '', phone: '', email: '' });
      refetchCustomers();
    } catch (err) {
      console.error('Failed to create customer:', err);
    }
  };

  const handleGenerateBill = async () => {
    if (!selectedCustomer || items.length === 0) return;

    try {
      const billData = {
        booking_id: `walk-in-${Date.now()}`,
        services: items.map((item) => ({
          service_id: item.serviceId,
          service_name: item.serviceName,
          staff_id: item.staffId,
          staff_name: item.staffName,
          original_price: item.servicePrice,
          override_price: item.overridePrice,
          quantity: item.quantity,
        })),
        membership_discount_percent: membershipDiscount,
        manual_adjustment: 0,
        payment_method: paymentMethod,
        amount_received: amountReceived,
      };

      await createBill.mutateAsync(billData);
      setShowBillPreview(true);

      // Reset after successful bill
      setTimeout(() => {
        resetBill();
        setShowBillPreview(false);
      }, 5000);
    } catch (err) {
      console.error('Failed to generate bill:', err);
    }
  };

  const canGenerateBill = selectedCustomer && items.length > 0 && amountReceived >= grandTotal;

  return (
    <div className="h-full flex flex-col lg:flex-row gap-4 p-4">
      {/* Left Panel - Service Selection & Items */}
      <div className="flex-1 flex flex-col gap-4 min-w-0">
        {/* Service Search */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <ShoppingCart className="h-5 w-5" />
              Add Services
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                value={serviceSearch}
                onChange={(e) => setServiceSearch(e.target.value)}
                placeholder="Search services..."
                className="pl-9"
              />
            </div>

            {/* Service Grid */}
            {servicesLoading ? (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-3">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <Skeleton key={i} className="h-16" />
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-3 max-h-48 overflow-y-auto">
                {filteredServices.slice(0, 12).map((service: any) => (
                  <button
                    key={service.id}
                    onClick={() => handleAddService(service)}
                    className="p-3 border rounded-lg hover:bg-purple-50 hover:border-purple-300 transition-colors text-left"
                  >
                    <p className="font-medium text-sm truncate">{service.name}</p>
                    <p className="text-purple-600 font-semibold">
                      {formatCurrency(service.price)}
                    </p>
                    <p className="text-xs text-gray-500">{service.duration} min</p>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Bill Items */}
        <Card className="flex-1">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Bill Items</CardTitle>
              {items.length > 0 && (
                <Button variant="ghost" size="sm" onClick={clearItems}>
                  <Trash2 className="h-4 w-4 mr-1" />
                  Clear All
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {items.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <ShoppingCart className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No items added</p>
                <p className="text-sm">Search and add services above</p>
              </div>
            ) : (
              <div className="space-y-3">
                {items.map((item, index) => (
                  <div
                    key={`${item.serviceId}-${index}`}
                    className="border rounded-lg p-3 space-y-2"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-medium">{item.serviceName}</p>
                        <div className="flex items-center gap-2 mt-1">
                          {item.overridePrice !== undefined && (
                            <Badge variant="secondary" className="text-xs">
                              Override: {formatCurrency(item.overridePrice)}
                            </Badge>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-purple-600">
                          {formatCurrency(item.overridePrice ?? item.servicePrice)}
                        </p>
                        {item.overridePrice !== undefined && (
                          <p className="text-xs line-through text-gray-400">
                            {formatCurrency(item.servicePrice)}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Staff Selection */}
                    <div className="flex items-center gap-2">
                      <Select
                        value={item.staffId}
                        onValueChange={(v) => handleStaffChange(index, v)}
                      >
                        <SelectTrigger className="h-8 text-sm">
                          <SelectValue placeholder="Select staff" />
                        </SelectTrigger>
                        <SelectContent>
                          {staff.map((s: any) => (
                            <SelectItem key={s.id} value={s.id}>
                              {s.name || `${s.firstName || ''} ${s.lastName || ''}`.trim()}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>

                      <Button
                        variant="outline"
                        size="sm"
                        className="h-8"
                        onClick={() => openOverrideModal(index)}
                      >
                        <Edit3 className="h-3 w-3 mr-1" />
                        Override
                      </Button>

                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 text-red-500"
                        onClick={() => removeItem(index)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Right Panel - Customer & Payment */}
      <div className="w-full lg:w-96 flex flex-col gap-4">
        {/* Customer Selection */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <User className="h-5 w-5" />
              Customer
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selectedCustomer ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                  <div>
                    <p className="font-medium">{selectedCustomer.name}</p>
                    <p className="text-sm text-gray-600">
                      {formatPhone(selectedCustomer.phone)}
                    </p>
                    {selectedCustomer.loyaltyPoints !== undefined && selectedCustomer.loyaltyPoints > 0 && (
                      <div className="flex items-center gap-1 mt-1">
                        <span className="text-yellow-500">⭐</span>
                        <span className="text-sm text-yellow-700">
                          {selectedCustomer.loyaltyPoints} points
                        </span>
                      </div>
                    )}
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedCustomer(null)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>

                {/* Membership Discount */}
                {selectedCustomer.membershipTier && selectedCustomer.membershipTier !== 'none' && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Membership Discount</span>
                    <Badge variant="secondary">
                      {selectedCustomer.membershipTier}
                    </Badge>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    value={customerSearch}
                    onChange={(e) => setCustomerSearch(e.target.value)}
                    placeholder="Search customers..."
                    className="pl-9"
                  />
                </div>

                {customerSearch && (
                  <div className="max-h-40 overflow-y-auto space-y-1">
                    {customers.slice(0, 5).map((customer: any) => (
                      <button
                        key={customer.id}
                        onClick={() => {
                          setSelectedCustomer({
                            id: customer.id,
                            name: customer.name,
                            phone: customer.phone,
                            email: customer.email,
                            loyaltyPoints: customer.loyaltyPoints,
                            membershipTier: customer.membershipTier,
                            totalVisits: customer.totalVisits,
                            totalSpent: customer.totalSpent,
                          });
                          setCustomerSearch('');
                        }}
                        className="w-full p-2 text-left hover:bg-gray-50 rounded-lg transition-colors"
                      >
                        <p className="font-medium text-sm">{customer.name}</p>
                        <p className="text-xs text-gray-500">{formatPhone(customer.phone)}</p>
                      </button>
                    ))}
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full mt-2"
                      onClick={() => setShowNewCustomer(true)}
                    >
                      <Plus className="h-4 w-4 mr-1" />
                      New Customer
                    </Button>
                  </div>
                )}

                {!customerSearch && (
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => setShowNewCustomer(true)}
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Add New Customer
                  </Button>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Payment Section */}
        <Card className="flex-1">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <CreditCard className="h-5 w-5" />
              Payment
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Payment Method */}
            <div className="grid grid-cols-2 gap-2">
              {PAYMENT_METHODS.map((method) => (
                <button
                  key={method.value}
                  onClick={() => setPaymentMethod(method.value)}
                  className={`p-3 border rounded-lg text-center transition-colors ${
                    paymentMethod === method.value
                      ? 'bg-purple-100 border-purple-300'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <span className="text-xl">{method.icon}</span>
                  <p className="text-sm font-medium mt-1">{method.label}</p>
                </button>
              ))}
            </div>

            {/* Amount Received */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Amount Received</label>
              <Input
                type="number"
                value={amountReceived || ''}
                onChange={(e) => setAmountReceived(parseFloat(e.target.value) || 0)}
                placeholder="Enter amount"
                className="text-lg font-semibold"
              />
              {changeDue > 0 && (
                <p className="text-sm text-green-600">
                  Change: {formatCurrency(changeDue)}
                </p>
              )}
            </div>

            {/* Quick Amount Buttons */}
            <div className="flex gap-2 flex-wrap">
              {[100, 200, 500, 1000, 2000].map((amount) => (
                <Button
                  key={amount}
                  variant="outline"
                  size="sm"
                  onClick={() => setAmountReceived(amount)}
                >
                  ₹{amount}
                </Button>
              ))}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setAmountReceived(Math.ceil(grandTotal))}
              >
                Exact
              </Button>
            </div>

            {/* Summary */}
            <div className="border-t pt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span>Subtotal</span>
                <span>{formatCurrency(subtotal)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>GST (5%)</span>
                <span>{formatCurrency(gstAmount)}</span>
              </div>
              <div className="flex justify-between font-semibold text-lg">
                <span>Total</span>
                <span className="text-purple-600">{formatCurrency(grandTotal)}</span>
              </div>
              {loyaltyPoints > 0 && (
                <div className="flex justify-between text-sm text-yellow-600">
                  <span>Loyalty Points</span>
                  <span>+{loyaltyPoints}</span>
                </div>
              )}
            </div>

            {/* Generate Bill Button */}
            <Button
              className="w-full bg-purple-600 hover:bg-purple-700"
              size="lg"
              onClick={handleGenerateBill}
              disabled={!canGenerateBill || createBill.isPending}
            >
              {createBill.isPending ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Check className="h-4 w-4 mr-2" />
              )}
              Generate Bill
            </Button>

            {!selectedCustomer && (
              <p className="text-xs text-center text-gray-500">
                Select a customer to generate bill
              </p>
            )}
            {selectedCustomer && items.length === 0 && (
              <p className="text-xs text-center text-gray-500">
                Add services to generate bill
              </p>
            )}
            {selectedCustomer && items.length > 0 && amountReceived < grandTotal && (
              <p className="text-xs text-center text-red-500">
                Amount received is less than total
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Price Override Dialog */}
      <PriceOverrideDialog
        open={overrideModalOpen}
        onOpenChange={closeOverrideModal}
        item={overrideItemIndex !== null ? items[overrideItemIndex] : null}
        onConfirm={handleOverrideConfirm}
      />

      {/* New Customer Modal */}
      <Modal open={showNewCustomer} onOpenChange={setShowNewCustomer}>
        <ModalContent className="sm:max-w-md">
          <ModalHeader>
            <ModalTitle>Add New Customer</ModalTitle>
            <ModalDescription>
              Create a new customer record
            </ModalDescription>
          </ModalHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Name *</label>
              <Input
                value={newCustomerData.name}
                onChange={(e) =>
                  setNewCustomerData({ ...newCustomerData, name: e.target.value })
                }
                placeholder="Customer name"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">WhatsApp Number *</label>
              <Input
                value={newCustomerData.phone}
                onChange={(e) =>
                  setNewCustomerData({ ...newCustomerData, phone: e.target.value })
                }
                placeholder="WhatsApp number"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Email</label>
              <Input
                type="email"
                value={newCustomerData.email}
                onChange={(e) =>
                  setNewCustomerData({ ...newCustomerData, email: e.target.value })
                }
                placeholder="Email (optional)"
              />
            </div>
          </div>
          <ModalFooter>
            <Button variant="outline" onClick={() => setShowNewCustomer(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleCreateCustomer}
              disabled={!newCustomerData.name || !newCustomerData.phone || createCustomer.isPending}
              className="bg-purple-600 hover:bg-purple-700"
            >
              {createCustomer.isPending ? 'Creating...' : 'Create Customer'}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Bill Preview Modal */}
      <Modal open={showBillPreview} onOpenChange={setShowBillPreview}>
        <ModalContent className="sm:max-w-lg">
          <ModalHeader>
            <ModalTitle>Bill Generated Successfully!</ModalTitle>
          </ModalHeader>
          <div className="py-4">
            <BillSummary
              items={items}
              subtotal={subtotal}
              gstAmount={gstAmount}
              gstPercent={5}
              grandTotal={grandTotal}
              loyaltyPoints={loyaltyPoints}
              paymentMethod={paymentMethod}
              customerName={selectedCustomer?.name}
              customerPhone={selectedCustomer?.phone}
              showActions={true}
            />
          </div>
          <ModalFooter>
            <Button
              onClick={() => {
                resetBill();
                setShowBillPreview(false);
              }}
              className="bg-purple-600 hover:bg-purple-700"
            >
              New Bill
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </div>
  );
};

export default BillingPage;
