/**
 * Billing & Subscription Settings Page
 */
import React, { useState } from 'react';
import {
  CreditCard,
  Check,
  Download,
  Plus,
  Zap,
  Building2,
  Users,
  Calendar,
  Crown,
  Receipt,
  Star,
} from 'lucide-react';
import { Button, Card, CardContent, CardHeader, CardTitle, Badge, Modal, ModalContent, ModalHeader, ModalFooter, Input } from '@salon-flow/ui';
import { cn } from '@/lib/utils';

const currentPlan = {
  name: 'Professional',
  price: 2999,
  billingCycle: 'monthly',
  nextBillingDate: '2026-03-15',
  features: [
    '3 Locations',
    '15 Staff Members',
    'Unlimited Bookings',
    'Advanced Analytics',
    'WhatsApp Integration',
  ],
};

const usageStats = {
  customers: { used: 2847, limit: 5000, label: 'Customers' },
  staff: { used: 8, limit: 15, label: 'Staff Members' },
  bookings: { used: 4521, limit: 'Unlimited', label: 'Bookings/Month' },
};

const billingHistory = [
  { id: 'INV-2026-001', date: '2026-02-15', amount: 2999, status: 'paid', description: 'Professional Plan - Feb 2026' },
  { id: 'INV-2026-002', date: '2026-01-15', amount: 2999, status: 'paid', description: 'Professional Plan - Jan 2026' },
  { id: 'INV-2025-012', date: '2025-12-15', amount: 2999, status: 'paid', description: 'Professional Plan - Dec 2025' },
];

const paymentMethods = [
  { id: 'pm_1', type: 'card', last4: '4242', brand: 'Visa', expMonth: 12, expYear: 2027, isDefault: true },
  { id: 'pm_2', type: 'card', last4: '8888', brand: 'Mastercard', expMonth: 8, expYear: 2026, isDefault: false },
];

const plans = [
  {
    id: 'starter',
    name: 'Starter',
    price: 999,
    description: 'Perfect for single location salons',
    features: ['1 Location', '5 Staff Members', '1000 Customers', 'Basic Analytics', 'Email Support'],
    popular: false,
  },
  {
    id: 'professional',
    name: 'Professional',
    price: 2999,
    description: 'Best for growing multi-location salons',
    features: ['3 Locations', '15 Staff Members', '5000 Customers', 'Advanced Analytics', 'WhatsApp Integration', 'Priority Support'],
    popular: true,
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 7999,
    description: 'For large salon chains and franchises',
    features: ['Unlimited Locations', 'Unlimited Staff', 'Unlimited Customers', 'AI Insights', 'Custom Integrations', 'Dedicated Account Manager', '24/7 Phone Support'],
    popular: false,
  },
];

const BillingSettingsPage: React.FC = () => {
  const [isUpgradeModalOpen, setIsUpgradeModalOpen] = useState(false);
  const [isAddCardModalOpen, setIsAddCardModalOpen] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [isGstEnabled, setIsGstEnabled] = useState(true);

  const handleUpgrade = (planId: string) => {
    setSelectedPlan(planId);
    setTimeout(() => {
      setIsUpgradeModalOpen(false);
      setSelectedPlan(null);
    }, 1500);
  };

  const handleDownloadInvoice = (invoiceId: string) => {
    console.log(`Downloading invoice ${invoiceId}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Billing & Subscription</h1>
      </div>

      <Card className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Crown className="w-5 h-5" />
                <span className="text-sm font-medium text-indigo-100">Current Plan</span>
              </div>
              <h2 className="text-3xl font-bold">{currentPlan.name}</h2>
              <p className="text-indigo-100 mt-1">
                ₹{currentPlan.price.toLocaleString('en-IN')}/month • Next billing: {new Date(currentPlan.nextBillingDate).toLocaleDateString('en-IN')}
              </p>
            </div>
            <Button
              onClick={() => setIsUpgradeModalOpen(true)}
              className="bg-white text-indigo-600 hover:bg-indigo-50 min-h-[44px]"
            >
              <Zap className="w-4 h-4 mr-2" />
              Upgrade Plan
            </Button>
          </div>
          <div className="flex flex-wrap gap-2 mt-4">
            {currentPlan.features.map((feature, idx) => (
              <Badge key={idx} className="bg-white/20 text-white border-0">
                <Check className="w-3 h-3 mr-1" />
                {feature}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="w-5 h-5 text-indigo-600" />
            Usage Statistics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(usageStats).map(([key, stat]) => (
              <div key={key} className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</span>
                  {key === 'customers' && <Users className="w-4 h-4 text-gray-400" />}
                  {key === 'staff' && <Building2 className="w-4 h-4 text-gray-400" />}
                  {key === 'bookings' && <Calendar className="w-4 h-4 text-gray-400" />}
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">
                    {stat.used.toLocaleString('en-IN')}
                  </span>
                  <span className="text-sm text-gray-500">
                    / {typeof stat.limit === 'number' ? stat.limit.toLocaleString('en-IN') : stat.limit}
                  </span>
                </div>
                {typeof stat.limit === 'number' && (
                  <div className="mt-2 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={cn(
                        'h-full rounded-full transition-all',
                        (stat.used / stat.limit) > 0.9 ? 'bg-rose-500' : (stat.used / stat.limit) > 0.7 ? 'bg-amber-500' : 'bg-emerald-500'
                      )}
                      style={{ width: `${Math.min((stat.used / stat.limit) * 100, 100)}%` }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-indigo-600" />
              Payment Methods
            </CardTitle>
            <Button variant="outline" size="sm" onClick={() => setIsAddCardModalOpen(true)}>
              <Plus className="w-4 h-4 mr-1" />
              Add Card
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {paymentMethods.map((method) => (
            <div
              key={method.id}
              className={cn(
                'flex items-center justify-between p-4 rounded-lg border',
                method.isDefault
                  ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                  : 'border-gray-200 dark:border-gray-700'
              )}
            >
              <div className="flex items-center gap-3">
                <div className="w-12 h-8 bg-gray-200 dark:bg-gray-700 rounded flex items-center justify-center text-xs font-medium">
                  {method.brand}
                </div>
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">
                    •••• {method.last4}
                  </p>
                  <p className="text-sm text-gray-500">
                    Expires {method.expMonth}/{method.expYear}
                  </p>
                </div>
              </div>
              {method.isDefault ? (
                <Badge variant="success">Default</Badge>
              ) : (
                <Button variant="ghost" size="sm">
                  Set Default
                </Button>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Receipt className="w-5 h-5 text-indigo-600" />
            Billing History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {billingHistory.map((invoice) => (
              <div
                key={invoice.id}
                className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
              >
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">{invoice.description}</p>
                  <div className="flex items-center gap-2 mt-1 text-sm text-gray-500">
                    <span>{invoice.id}</span>
                    <span>•</span>
                    <span>{new Date(invoice.date).toLocaleDateString('en-IN')}</span>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="font-semibold text-gray-900 dark:text-white">
                      ₹{invoice.amount.toLocaleString('en-IN')}
                    </p>
                    <Badge variant={invoice.status === 'paid' ? 'success' : 'warning'} className="text-xs">
                      {invoice.status === 'paid' ? 'Paid' : 'Pending'}
                    </Badge>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDownloadInvoice(invoice.id)}
                  >
                    <Download className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg">
                <Receipt className="w-5 h-5 text-indigo-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white">GST Invoices</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Include GST breakdown in all invoices
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setIsGstEnabled(!isGstEnabled)}
              className={cn(
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                isGstEnabled ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600'
              )}
            >
              <span
                className={cn(
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  isGstEnabled ? 'translate-x-6' : 'translate-x-1'
                )}
              />
            </button>
          </div>
        </CardContent>
      </Card>

      <Modal open={isUpgradeModalOpen} onOpenChange={setIsUpgradeModalOpen}>
        <ModalContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <ModalHeader>Choose Your Plan</ModalHeader>
          <div className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {plans.map((plan) => (
                <Card
                  key={plan.id}
                  className={cn(
                    'relative cursor-pointer transition-all',
                    plan.popular && 'border-indigo-500 ring-2 ring-indigo-500',
                    selectedPlan === plan.id && 'ring-2 ring-indigo-500'
                  )}
                  onClick={() => handleUpgrade(plan.id)}
                >
                  {plan.popular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <Badge className="bg-indigo-600">
                        <Star className="w-3 h-3 mr-1" />
                        Most Popular
                      </Badge>
                    </div>
                  )}
                  <CardContent className="p-6">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">{plan.name}</h3>
                    <p className="text-sm text-gray-500 mt-1">{plan.description}</p>
                    <div className="mt-4">
                      <span className="text-3xl font-bold text-gray-900 dark:text-white">
                        ₹{plan.price.toLocaleString('en-IN')}
                      </span>
                      <span className="text-gray-500">/month</span>
                    </div>
                    <ul className="mt-4 space-y-2">
                      {plan.features.map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm">
                          <Check className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                          <span className="text-gray-600 dark:text-gray-300">{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <Button
                      className="w-full mt-6"
                      variant={plan.popular ? 'default' : 'outline'}
                      disabled={selectedPlan === plan.id}
                    >
                      {selectedPlan === plan.id ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                          Processing...
                        </>
                      ) : plan.id === 'professional' ? (
                        'Current Plan'
                      ) : (
                        'Upgrade'
                      )}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </ModalContent>
      </Modal>

      <Modal open={isAddCardModalOpen} onOpenChange={setIsAddCardModalOpen}>
        <ModalContent className="max-w-md">
          <ModalHeader>Add Payment Method</ModalHeader>
          <div className="p-4 space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Card Number</label>
              <Input placeholder="1234 5678 9012 3456" maxLength={19} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Expiry</label>
                <Input placeholder="MM/YY" maxLength={5} />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">CVC</label>
                <Input placeholder="123" maxLength={3} />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Cardholder Name</label>
              <Input placeholder="Name on card" />
            </div>
          </div>
          <ModalFooter>
            <Button variant="outline" onClick={() => setIsAddCardModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setIsAddCardModalOpen(false)}>
              Add Card
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </div>
  );
};

export default BillingSettingsPage;
