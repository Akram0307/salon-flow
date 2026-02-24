import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  ArrowLeft, Calendar, Clock, Phone, DollarSign, 
  Scissors, Edit, Trash2, XCircle, AlertCircle, Loader2
} from 'lucide-react';
import { api, BOOKING_ENDPOINTS, useBooking, useCancelBooking, formatCurrency, formatDate, formatTime, formatDateTime } from '@salon-flow/shared';
import { Button, Card, CardHeader, CardTitle, CardContent, Avatar, Modal } from '@salon-flow/ui';
import Status from '../../components/ui/Status';

const BookingDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);

  const { data: booking, isLoading, error } = useBooking(id!);
  const cancelMutation = useCancelBooking();

  const deleteMutation = useMutation({
    mutationFn: async () => {
      await api.delete(BOOKING_ENDPOINTS.DELETE(id!));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookings'] });
      navigate('/bookings');
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error || !booking) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900">Booking not found</h2>
        <Button onClick={() => navigate('/bookings')} className="mt-4">Back to Bookings</Button>
      </div>
    );
  }

  const handleCancel = () => {
    cancelMutation.mutate({ id: id!, reason: 'Cancelled by owner' }, {
      onSuccess: () => {
        setShowCancelModal(false);
        queryClient.invalidateQueries({ queryKey: ['booking', id] });
      }
    });
  };

  const handleDelete = () => {
    deleteMutation.mutate();
  };

  const isCancelled = (booking.status as string) === 'cancelled';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/bookings')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Booking Details</h1>
            <p className="text-gray-500">#{booking.id?.slice(0, 8)}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate(`/bookings/${id}/edit`)}>
            <Edit className="h-4 w-4 mr-2" /> Edit
          </Button>
          {!isCancelled && (
            <Button variant="outline" onClick={() => setShowCancelModal(true)}>
              <XCircle className="h-4 w-4 mr-2" /> Cancel
            </Button>
          )}
          <Button variant="destructive" onClick={() => setShowDeleteModal(true)}>
            <Trash2 className="h-4 w-4 mr-2" /> Delete
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Appointment Information</span>
                <Status status={booking.status} />
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3">
                  <Scissors className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Service</p>
                    <p className="font-medium">{booking.serviceName || 'N/A'}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Clock className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Duration</p>
                    <p className="font-medium">{booking.serviceDuration ? `${booking.serviceDuration} min` : 'N/A'}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Calendar className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Date & Time</p>
                    <p className="font-medium">
                      {formatDate(booking.startTime)} at {formatTime(booking.startTime)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <DollarSign className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Amount</p>
                    <p className="font-medium">{formatCurrency(booking.totalAmount || 0)}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Staff</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <Avatar name={booking.staffName || 'Staff'} size="lg" />
                <div>
                  <p className="font-medium">{booking.staffName || 'Unassigned'}</p>
                  <p className="text-sm text-gray-500">Stylist</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Customer Info */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Customer</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Avatar name={booking.customerName || 'Customer'} size="lg" />
                <div>
                  <p className="font-medium">{booking.customerName || 'Unknown'}</p>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-gray-600">
                  <Phone className="h-4 w-4" />
                  <span>{booking.customerPhone || 'N/A'}</span>
                </div>
              </div>
              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => navigate(`/customers/${booking.customerId}`)}
              >
                View Customer Profile
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Booking History</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-500">
                Created: {booking.createdAt ? formatDateTime(booking.createdAt) : 'N/A'}
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Cancel Modal */}
      <Modal isOpen={showCancelModal} onClose={() => setShowCancelModal(false)}>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-2">Cancel Booking</h3>
          <p className="text-gray-600 mb-4">Are you sure you want to cancel this booking?</p>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowCancelModal(false)}>No, Keep it</Button>
            <Button variant="destructive" onClick={handleCancel} disabled={cancelMutation.isPending}>
              {cancelMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Yes, Cancel'}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Delete Modal */}
      <Modal isOpen={showDeleteModal} onClose={() => setShowDeleteModal(false)}>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-2">Delete Booking</h3>
          <p className="text-gray-600 mb-4">This action cannot be undone. Are you sure?</p>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowDeleteModal(false)}>Cancel</Button>
            <Button variant="destructive" onClick={handleDelete} disabled={deleteMutation.isPending}>
              {deleteMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Delete'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default BookingDetailPage;
