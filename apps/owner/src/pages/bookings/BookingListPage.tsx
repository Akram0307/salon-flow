import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, Search, Plus, Loader2 } from 'lucide-react';
import { useBookings, formatCurrency, formatDate, formatTime, type BookingStatus } from '@salon-flow/shared';
import { Button, Card, CardContent, Input } from '@salon-flow/ui';
import Status from '../../components/ui/Status';

const BookingListPage: React.FC = () => {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [dateFilter, setDateFilter] = useState('');

  const { data: bookings, isLoading } = useBookings({ 
    status: statusFilter as BookingStatus || undefined, 
    date: dateFilter 
  });

  const filteredBookings = bookings?.filter(booking => 
    booking.customerName?.toLowerCase().includes(search.toLowerCase()) ||
    booking.serviceName?.toLowerCase().includes(search.toLowerCase())
  ) || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Bookings</h1>
        <Button onClick={() => navigate('/bookings/new')}>
          <Plus className="h-4 w-4 mr-2" /> New Booking
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="py-4">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  placeholder="Search by customer or service..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border rounded-lg bg-white"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="confirmed">Confirmed</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <Input
              type="date"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="w-auto"
            />
          </div>
        </CardContent>
      </Card>

      {/* Bookings Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : filteredBookings.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No bookings found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Service</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Staff</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date & Time</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {filteredBookings.map((booking) => (
                    <tr 
                      key={booking.id} 
                      onClick={() => navigate(`/bookings/${booking.id}`)}
                      className="hover:bg-gray-50 cursor-pointer"
                    >
                      <td className="px-6 py-4">
                        <div className="font-medium">{booking.customerName || 'N/A'}</div>
                        <div className="text-sm text-gray-500">{booking.customerPhone || ''}</div>
                      </td>
                      <td className="px-6 py-4">{booking.serviceName || 'N/A'}</td>
                      <td className="px-6 py-4">{booking.staffName || 'Unassigned'}</td>
                      <td className="px-6 py-4">
                        <div>{formatDate(booking.startTime)}</div>
                        <div className="text-sm text-gray-500">{formatTime(booking.startTime)} - {formatTime(booking.endTime)}</div>
                      </td>
                      <td className="px-6 py-4">
                        <Status status={booking.status} />
                      </td>
                      <td className="px-6 py-4 font-medium">{formatCurrency(booking.totalAmount || 0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default BookingListPage;
