import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePayments } from '@salon-flow/shared';
import { 
  Card, 
  Button, 
  Input,
  Table,
  EmptyState,
} from '@salon-flow/ui';
import { formatCurrency, formatDate } from '@salon-flow/shared';
import { 
  Search, 
  Download,
  DollarSign,
  CreditCard,
  Wallet,
  Banknote,
  Eye,
  Clock,
  CheckCircle,
  XCircle,
  RefreshCw,
} from 'lucide-react';

const PaymentsPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [methodFilter, setMethodFilter] = useState<string>('all');
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d' | 'all'>('30d');

  const { data: payments, isLoading, error} = usePayments({
    search: searchQuery || undefined,
    status: statusFilter !== 'all' ? statusFilter : undefined,
    method: methodFilter !== 'all' ? methodFilter : undefined,
    date_range: dateRange,
  });

  const stats = {
    totalRevenue: payments?.reduce((sum: number, p: any) => sum + (p.status === 'completed' ? p.amount : 0), 0) || 0,
    totalTransactions: payments?.length || 0,
    completedCount: payments?.filter((p: any) => p.status === 'completed').length || 0,
    pendingCount: payments?.filter((p: any) => p.status === 'pending').length || 0,
    refundedCount: payments?.filter((p: any) => p.status === 'refunded').length || 0,
  };

  const getMethodIcon = (method: string) => {
    switch (method) {
      case 'cash': return <Banknote className="h-4 w-4" />;
      case 'card': return <CreditCard className="h-4 w-4" />;
      case 'upi': return <Wallet className="h-4 w-4" />;
      default: return <DollarSign className="h-4 w-4" />;
    }
  };

  const getMethodBadge = (method: string) => {
    const variants: Record<string, { className: string; label: string }> = {
      cash: { className: 'bg-green-100 text-green-800', label: 'Cash' },
      card: { className: 'bg-blue-100 text-blue-800', label: 'Card' },
      upi: { className: 'bg-purple-100 text-purple-800', label: 'UPI' },
      wallet: { className: 'bg-orange-100 text-orange-800', label: 'Wallet' },
    };
    const variant = variants[method] || { className: 'bg-gray-100 text-gray-800', label: method };
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${variant.className}`}>
        {getMethodIcon(method)}
        {variant.label}
      </span>
    );
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { className: string; icon: any }> = {
      completed: { className: 'bg-green-100 text-green-800', icon: CheckCircle },
      pending: { className: 'bg-yellow-100 text-yellow-800', icon: Clock },
      failed: { className: 'bg-red-100 text-red-800', icon: XCircle },
      refunded: { className: 'bg-gray-100 text-gray-800', icon: RefreshCw },
    };
    const variant = variants[status] || { className: 'bg-gray-100 text-gray-800', icon: DollarSign };
    const Icon = variant.icon;
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${variant.className}`}>
        <Icon className="h-3 w-3" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const columns = [
    {
      key: 'id',
      header: 'Transaction ID',
      render: (payment: any) => (
        <div>
          <p className="font-mono text-sm text-gray-900">#{payment.id.slice(-8).toUpperCase()}</p>
          <p className="text-xs text-gray-500">{formatDate(payment.created_at)}</p>
        </div>
      ),
    },
    {
      key: 'customer',
      header: 'Customer',
      render: (payment: any) => (
        <div>
          <p className="font-medium text-gray-900">{payment.customer_name}</p>
          <p className="text-sm text-gray-500">{payment.customer_phone}</p>
        </div>
      ),
    },
    {
      key: 'booking',
      header: 'Booking',
      render: (payment: any) => (
        <div>
          <p className="text-sm text-gray-900">{payment.booking_service}</p>
          <p className="text-xs text-gray-500">{payment.staff_name}</p>
        </div>
      ),
    },
    {
      key: 'amount',
      header: 'Amount',
      render: (payment: any) => (
        <div className="text-right">
          <p className="font-bold text-gray-900">{formatCurrency(payment.amount)}</p>
          {payment.tip > 0 && (
            <p className="text-xs text-gray-500">+{formatCurrency(payment.tip)} tip</p>
          )}
        </div>
      ),
    },
    {
      key: 'method',
      header: 'Method',
      render: (payment: any) => getMethodBadge(payment.payment_method),
    },
    {
      key: 'status',
      header: 'Status',
      render: (payment: any) => getStatusBadge(payment.status),
    },
    {
      key: 'actions',
      header: '',
      render: (payment: any) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/payments/${payment.id}`);
          }}
        >
          <Eye className="h-4 w-4" />
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Payments</h1>
          <p className="text-gray-500 mt-1">Transaction history and management</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" leftIcon={<Download className="h-4 w-4" />}>
            Export
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
              <DollarSign className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-lg font-bold text-gray-900">{formatCurrency(stats.totalRevenue)}</p>
              <p className="text-xs text-gray-500">Total Revenue</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <CreditCard className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-lg font-bold text-gray-900">{stats.totalTransactions}</p>
              <p className="text-xs text-gray-500">Transactions</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center">
            <CheckCircle className="h-5 w-5 text-emerald-600" />
            </div>
            <div>
              <p className="text-lg font-bold text-gray-900">{stats.completedCount}</p>
              <p className="text-xs text-gray-500">Completed</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-yellow-100 flex items-center justify-center">
              <Clock className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-lg font-bold text-gray-900">{stats.pendingCount}</p>
              <p className="text-xs text-gray-500">Pending</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
              <RefreshCw className="h-5 w-5 text-gray-600" />
            </div>
            <div>
              <p className="text-lg font-bold text-gray-900">{stats.refundedCount}</p>
              <p className="text-xs text-gray-500">Refunded</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card padding="sm">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Search by customer, transaction ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              leftIcon={<Search className="h-4 w-4" />}
            />
          </div>
          <div className="flex gap-3">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value as any)}
              className="px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
              <option value="all">All Time</option>
            </select>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Status</option>
              <option value="completed">Completed</option>
              <option value="pending">Pending</option>
              <option value="failed">Failed</option>
              <option value="refunded">Refunded</option>
            </select>
            <select
              value={methodFilter}
              onChange={(e) => setMethodFilter(e.target.value)}
              className="px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Methods</option>
              <option value="cash">Cash</option>
              <option value="card">Card</option>
              <option value="upi">UPI</option>
              <option value="wallet">Wallet</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Table */}
      <Card padding="none">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading payments...</div>
        ) : error ? (
          <div className="p-8 text-center text-red-500">Failed to load payments</div>
        ) : !payments?.length ? (
          <EmptyState
            icon={<DollarSign className="h-12 w-12" />}
            title="No payments found"
            description="Try adjusting your filters"
          />
        ) : (
          <Table
            data={payments}
            columns={columns}
            onRowClick={(payment) => navigate(`/payments/${payment.id}`)}
            keyExtractor={(payment) => payment.id}
          />
        )}
      </Card>
    </div>
  );
};

export default PaymentsPage;
