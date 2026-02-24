import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { Plus, Loader2 } from 'lucide-react';
import { useBookings, formatCurrency, formatTime } from '@salon-flow/shared';
import { Button, Card, CardContent, Modal } from '@salon-flow/ui';
import Status from '../../components/ui/Status';
import type { Booking } from '@salon-flow/shared';

const BookingsPage: React.FC = () => {
  const navigate = useNavigate();
  const [currentDate] = useState(new Date());
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);
  const [showModal, setShowModal] = useState(false);

  // Get date range for current month
  const dateRange = useMemo(() => {
    const start = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const end = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
    return {
      startDate: start.toISOString().split('T')[0],
      endDate: end.toISOString().split('T')[0],
    };
  }, [currentDate]);

  const { data: bookings, isLoading } = useBookings(dateRange);

  // Transform bookings to calendar events
  const events = useMemo(() => {
    return (bookings || []).map((booking) => ({
      id: booking.id,
      title: `${booking.customerName || 'Customer'} - ${booking.serviceName || 'Service'}`,
      start: booking.startTime,
      end: booking.endTime,
      backgroundColor: getStatusColor(booking.status),
      borderColor: getStatusColor(booking.status),
      extendedProps: {
        booking,
      },
    }));
  }, [bookings]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return '#22c55e';
      case 'completed': return '#22c55e';
      case 'in_progress': return '#3b82f6';
      case 'pending': return '#f59e0b';
      case 'cancelled':
      case 'canceled': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const handleEventClick = (info: any) => {
    const booking = info.event.extendedProps.booking as Booking;
    setSelectedBooking(booking);
    setShowModal(true);
  };

  const handleDateClick = (info: any) => {
    navigate(`/bookings/new?date=${info.dateStr}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Calendar</h1>
        <Button onClick={() => navigate('/bookings/new')}>
          <Plus className="h-4 w-4 mr-2" /> New Booking
        </Button>
      </div>

      <Card>
        <CardContent className="p-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-96">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : (
            <FullCalendar
              plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
              initialView="dayGridMonth"
              headerToolbar={{
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay',
              }}
              events={events}
              eventClick={handleEventClick}
              dateClick={handleDateClick}
              height="auto"
              nowIndicator
              editable
              selectable
            />
          )}
        </CardContent>
      </Card>

      {/* Booking Detail Modal */}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)}>
        {selectedBooking && (
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Booking Details</h3>
              <Status status={selectedBooking.status} />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-500">Customer:</span>
                <span className="font-medium">{selectedBooking.customerName || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Service:</span>
                <span className="font-medium">{selectedBooking.serviceName || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Time:</span>
                <span className="font-medium">{formatTime(selectedBooking.startTime)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Amount:</span>
                <span className="font-medium">{formatCurrency(selectedBooking.totalAmount || 0)}</span>
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <Button 
                variant="outline" 
                className="flex-1"
                onClick={() => {
                  setShowModal(false);
                  navigate(`/bookings/${selectedBooking.id}`);
                }}
              >
                View Details
              </Button>
              <Button 
                className="flex-1"
                onClick={() => {
                  setShowModal(false);
                  navigate(`/bookings/${selectedBooking.id}/edit`);
                }}
              >
                Edit
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default BookingsPage;
