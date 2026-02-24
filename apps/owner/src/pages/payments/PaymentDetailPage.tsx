import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePayment } from '@salon-flow/shared';
import { 
  Card, 
  Button,
  Skeleton,
} from '@salon-flow/ui';
import { formatCurrency, formatDate, formatTime } from '@salon-flow/shared';
import { 
  ArrowLeft,
  DollarSign,
  CreditCard,
  Wallet,
  Banknote,
  Calendar,
  Clock,
  User,
  Scissors,
  CheckCircle,
  XCircle,
  RefreshCw,
  AlertCircle,
  Printer,
  Download,
  Receipt,
  Copy,
  Phone,
} from 'lucide-react';

const PaymentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: payment, isLoading, error } = usePayment(id!);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (error || !payment) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Payment Not Found</h2>
        <p className="text-gray-500 mb-4">The payment you're looking for doesn't exist.</p>
        <Button onClick={() => navigate('/payments')}>Back to Payments</Button>
      </div>
    );
  }

  const getMethodIcon = (method: string) => {
    switch (method) {
      case 'cash': return <Banknote className="h-5 w-5" />;
      case 'card': return <CreditCard className="h-5 w-5" />;
      case 'upi': return <Wallet className="h-5 w-5" />;
      default: return <DollarSign className="h-5 w-5" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { className: string; icon: any }> = {
      completed: { className: 'bg-green-100 text-green-800 border-green-200', icon: CheckCircle },
      pending: { className: 'bg-yellow-100 text-yellow-800 border-yellow-200', icon: Clock },
      failed: { className: 'bg-red-100 text-red-800 border-red-200', icon: XCircle },
      refunded: { className: 'bg-gray-100 text-gray-800 border-gray-200', icon: RefreshCw },
    };
    const variant = variants[status] || { className: 'bg-gray-100 text-gray-800', icon: DollarSign };
    const Icon = variant.icon;
    return (
      <span className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium border ${variant.className}`}>
        <Icon className="h-4 w-4" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const handlePrint = () => {
    window.print();
  };

  const handleCopyId = () => {
    navigator.clipboard.writeText(payment.id);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Payment Details</h1>
            <p className="text-gray-500 mt-1">Transaction #{payment.id.slice(-8).toUpperCase()}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={handlePrint} leftIcon={<Printer className="h-4 w-4" />}>
            Print
          </Button>
          <Button variant="outline" leftIcon={<Download className="h-4 w-4" />}>
            Download
          </Button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Payment Summary */}
          <Card padding="lg">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Payment Summary</h2>
                <p className="text-sm text-gray-500 mt-1">
                  {formatDate(payment.created_at)} at {formatTime(payment.created_at)}
                </p>
              </div>
              {getStatusBadge(payment.status)}
            </div>

            {/* Amount Breakdown */}
            <div className="space-y-3">
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-medium">{formatCurrency(payment.subtotal || payment.amount)}</span>
              </div>
              {payment.discount > 0 && (
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">Discount</span>
                  <span className="font-medium text-green-600">-{formatCurrency(payment.discount)}</span>
                </div>
              )}
              {payment.gst > 0 && (
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">GST (5%)</span>
                  <span className="font-medium">{formatCurrency(payment.gst)}</span>
                </div>
              )}
              {payment.tip > 0 && (
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">Tip</span>
                  <span className="font-medium">{formatCurrency(payment.tip)}</span>
                </div>
              )}
              <div className="flex justify-between py-3 bg-gray-50 rounded-lg px-3 mt-2">
                <span className="text-lg font-semibold text-gray-900">Total</span>
                <span className="text-lg font-bold text-gray-900">{formatCurrency(payment.total_amount || payment.amount)}</span>
              </div>
            </div>
          </Card>

          {/* Service Details */}
          <Card padding="lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Service Details</h3>
            <div className="space-y-4">
              {payment.services?.map((service: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center">
                      <Scissors className="h-5 w-5 text-primary-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{service.name}</p>
                      <p className="text-sm text-gray-500">{service.duration} min</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900">{formatCurrency(service.price)}</p>
                    {service.staff_name && (
                      <p className="text-sm text-gray-500">by {service.staff_name}</p>
                    )}
                  </div>
                </div>
              ))}
              {!payment.services && payment.booking_service && (
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center">
                      <Scissors className="h-5 w-5 text-primary-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{payment.booking_service}</p>
                      {payment.staff_name && (
                        <p className="text-sm text-gray-500">by {payment.staff_name}</p>
                      )}
                    </div>
                  </div>
                  <p className="font-medium text-gray-900">{formatCurrency(payment.amount)}</p>
                </div>
              )}
            </div>
          </Card>

          {/* Transaction Info */}
          <Card padding="lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Transaction Information</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                  <Receipt className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Transaction ID</p>
                  <div className="flex items-center gap-2">
                    <p className="font-mono text-sm font-medium">{payment.id}</p>
                    <button onClick={handleCopyId} className="text-gray-400 hover:text-gray-600">
                      <Copy className="h-3 w-3" />
                    </button>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                  {getMethodIcon(payment.payment_method)}
                </div>
                <div>
                  <p className="text-sm text-gray-500">Payment Method</p>
                  <p className="font-medium text-gray-900 capitalize">{payment.payment_method}</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                  <Calendar className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Date</p>
                  <p className="font-medium text-gray-900">{formatDate(payment.created_at)}</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-10 h-10 rounded-lg bg-orange-100 flex items-center justify-center">
                  <Clock className="h-5 w-5 text-orange-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Time</p>
                  <p className="font-medium text-gray-900">{formatTime(payment.created_at)}</p>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Customer Info */}
          <Card padding="lg">
            <h3 className="text-sm font-medium text-gray-500 mb-4">Customer</h3>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center">
                <User className="h-6 w-6 text-primary-600" />
              </div>
              <div>
                <p className="font-medium text-gray-900">{payment.customer_name}</p>
                <p className="text-sm text-gray-500">Customer</p>
              </div>
            </div>
            <div className="space-y-2">
              <a 
                href={`tel:${payment.customer_phone}`}
                className="flex items-center gap-2 text-gray-600 hover:text-primary-600"
              >
                <Phone className="h-4 w-4" />
                <span>{payment.customer_phone}</span>
              </a>
            </div>
            <Button 
              variant="outline" 
              fullWidth 
              className="mt-4"
              onClick={() => navigate(`/customers/${payment.customer_id}`)}
            >
              View Profile
            </Button>
          </Card>

          {/* Booking Info */}
          {payment.booking_id && (
            <Card padding="lg">
              <h3 className="text-sm font-medium text-gray-500 mb-4">Related Booking</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-gray-600">
                  <Calendar className="h-4 w-4" />
                  <span>{formatDate(payment.booking_date)}</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                  <Clock className="h-4 w-4" />
                  <span>{formatTime(payment.booking_time)}</span>
                </div>
              </div>
              <Button 
                variant="outline" 
                fullWidth 
                className="mt-4"
                onClick={() => navigate(`/bookings/${payment.booking_id}`)}
              >
                View Booking
              </Button>
            </Card>
          )}

          {/* Staff Info */}
          {payment.staff_name && (
            <Card padding="lg">
              <h3 className="text-sm font-medium text-gray-500 mb-4">Served By</h3>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
                  <User className="h-5 w-5 text-orange-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{payment.staff_name}</p>
                  <p className="text-sm text-gray-500">Staff Member</p>
                </div>
              </div>
              {payment.staff_id && (
                <Button 
                  variant="outline" 
                  fullWidth 
                  className="mt-4"
                  onClick={() => navigate(`/staff/${payment.staff_id}`)}
                >
                  View Profile
                </Button>
              )}
            </Card>
          )}

          {/* Quick Actions */}
          <Card padding="lg">
            <h3 className="text-sm font-medium text-gray-500 mb-4">Actions</h3>
            <div className="space-y-2">
              {payment.status === 'completed' && (
                <Button variant="outline" fullWidth leftIcon={<RefreshCw className="h-4 w-4" />}>
                  Process Refund
                </Button>
              )}
              {payment.status === 'pending' && (
                <Button variant="default" fullWidth leftIcon={<CheckCircle className="h-4 w-4" />}>
                  Mark as Paid
                </Button>
              )}
              <Button variant="outline" fullWidth leftIcon={<Receipt className="h-4 w-4" />}>
                Send Receipt
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default PaymentDetailPage;
