import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Phone, Mail, Calendar, Edit, Loader2 } from 'lucide-react';
import { useCustomer, useBookings, formatCurrency, formatDate, formatTime } from '@salon-flow/shared';
import { Button, Card, CardHeader, CardTitle, CardContent, Avatar } from '@salon-flow/ui';
import Status from '../../components/ui/Status';

const CustomerDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: customer, isLoading: customerLoading } = useCustomer(id!);
  const { data: bookings } = useBookings({ customerId: id });

  if (customerLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900">Customer not found</h2>
        <Button onClick={() => navigate('/customers')} className="mt-4">Back to Customers</Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/customers')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{customer.name}</h1>
            <p className="text-gray-500">Customer Profile</p>
          </div>
        </div>
        <Button variant="outline" onClick={() => navigate(`/customers/${id}/edit`)}>
          <Edit className="h-4 w-4 mr-2" /> Edit
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Customer Info */}
        <div className="space-y-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col items-center text-center">
                <Avatar name={customer.name} size="xl" className="mb-4" />
                <h2 className="text-xl font-semibold">{customer.name}</h2>
                <div className="flex items-center gap-2 mt-2 text-gray-500">
                  <Phone className="h-4 w-4" />
                  <span>{customer.phone}</span>
                </div>
                {customer.email && (
                  <div className="flex items-center gap-2 mt-1 text-gray-500">
                    <Mail className="h-4 w-4" />
                    <span>{customer.email}</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Statistics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-500">Total Visits</span>
                <span className="font-medium">{customer.totalVisits || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Total Spent</span>
                <span className="font-medium">{formatCurrency(customer.totalSpent || 0)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Loyalty Points</span>
                <span className="font-medium">{customer.loyaltyPoints || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Avg. Spend</span>
                <span className="font-medium">{formatCurrency(customer.avgSpend || 0)}</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Booking History */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Booking History</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {bookings && bookings.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Service</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {bookings.map((booking) => (
                        <tr 
                          key={booking.id}
                          onClick={() => navigate(`/bookings/${booking.id}`)}
                          className="hover:bg-gray-50 cursor-pointer"
                        >
                          <td className="px-6 py-4">
                            <div>{formatDate(booking.startTime)}</div>
                            <div className="text-sm text-gray-500">{formatTime(booking.startTime)}</div>
                          </td>
                          <td className="px-6 py-4">{booking.serviceName || 'N/A'}</td>
                          <td className="px-6 py-4">
                            <Status status={booking.status} />
                          </td>
                          <td className="px-6 py-4 font-medium">{formatCurrency(booking.totalAmount || 0)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No booking history</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CustomerDetailPage;
