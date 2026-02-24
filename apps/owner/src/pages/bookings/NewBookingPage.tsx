import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Calendar, Clock, User, Scissors, Loader2, Search } from 'lucide-react';
import { 
  useCreateBooking, 
  useCustomers, 
  useServices, 
  useStaffList,
  bookingFormSchema,
  formatCurrency,
  type BookingFormData
} from '@salon-flow/shared';
import { Button, Card, CardHeader, CardTitle, CardContent, Input, Modal } from '@salon-flow/ui';
import type { Customer, Service } from '@salon-flow/shared';

const NewBookingPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const preselectedDate = searchParams.get('date') || new Date().toISOString().split('T')[0];

  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [customerSearch, setCustomerSearch] = useState('');
  const [showCustomerModal, setShowCustomerModal] = useState(false);

  const createBooking = useCreateBooking();
  const { data: customers } = useCustomers({ search: customerSearch });
  const { data: services } = useServices();
  const { data: staffList } = useStaffList();

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<any>({
    resolver: zodResolver(bookingFormSchema),
    defaultValues: {
      date: preselectedDate,
      startTime: '09:00',
    },
  });

  const selectedServiceId = watch('serviceId');
  
  // Update selected service when serviceId changes
  useEffect(() => {
    if (selectedServiceId && services) {
      const service = services.find(s => s.id === selectedServiceId);
      setSelectedService(service || null);
    }
  }, [selectedServiceId, services]);

  const onSubmit = async (data: BookingFormData) => {
    try {
      await createBooking.mutateAsync({
        customerId: data.customerId,
        services: [{ serviceId: data.serviceId, staffId: data.staffId || undefined }],
        date: data.date,
        startTime: data.startTime,
        notes: data.notes,
      } as any);
      navigate('/bookings');
    } catch (error) {
      console.error('Failed to create booking:', error);
    }
  };

  const handleCustomerSelect = (customer: Customer) => {
    setSelectedCustomer(customer);
    setValue('customerId', customer.id);
    setShowCustomerModal(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">New Booking</h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Customer Selection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" /> Customer
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selectedCustomer ? (
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">{selectedCustomer.name}</p>
                  <p className="text-sm text-gray-500">{selectedCustomer.phone}</p>
                </div>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setSelectedCustomer(null);
                    setValue('customerId', '');
                  }}
                >
                  Change
                </Button>
              </div>
            ) : (
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => setShowCustomerModal(true)}
                className="w-full"
              >
                <Search className="h-4 w-4 mr-2" /> Select Customer
              </Button>
            )}
            <input type="hidden" {...register('customerId')} />
            {errors.customerId && <p className="text-red-500 text-sm mt-1">{errors.customerId?.message?.toString()}</p>}
          </CardContent>
        </Card>

        {/* Service Selection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Scissors className="h-5 w-5" /> Service
            </CardTitle>
          </CardHeader>
          <CardContent>
            <select 
              {...register('serviceId')}
              className="w-full px-3 py-2 border rounded-lg"
            >
              <option value="">Select a service</option>
              {services?.map(service => (
                <option key={service.id} value={service.id}>
                  {service.name} - {formatCurrency(service.price)} ({service.duration} min)
                </option>
              ))}
            </select>
            {errors.serviceId && <p className="text-red-500 text-sm mt-1">{errors.serviceId?.message?.toString()}</p>}
          </CardContent>
        </Card>

        {/* Staff Selection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" /> Staff
            </CardTitle>
          </CardHeader>
          <CardContent>
            <select 
              {...register('staffId')}
              className="w-full px-3 py-2 border rounded-lg"
            >
              <option value="">Select staff member</option>
              {staffList?.map(staff => (
                <option key={staff.id} value={staff.id}>
                  {staff.name}
                </option>
              ))}
            </select>
            {errors.staffId && <p className="text-red-500 text-sm mt-1">{errors.staffId?.message?.toString()}</p>}
          </CardContent>
        </Card>

        {/* Date & Time */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" /> Date & Time
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
                <Input type="date" {...register('date')} />
                {errors.date && <p className="text-red-500 text-sm mt-1">{errors.date?.message?.toString()}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
                <Input type="time" {...register('startTime')} />
                {errors.startTime && <p className="text-red-500 text-sm mt-1">{errors.startTime?.message?.toString()}</p>}
              </div>
            </div>
            {selectedService && (
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Clock className="h-4 w-4" />
                Duration: {selectedService.duration} minutes
              </div>
            )}
          </CardContent>
        </Card>

        {/* Notes */}
        <Card>
          <CardHeader>
            <CardTitle>Notes</CardTitle>
          </CardHeader>
          <CardContent>
            <textarea 
              {...register('notes')}
              placeholder="Add any special requests or notes..."
              className="w-full px-3 py-2 border rounded-lg min-h-[100px]"
            />
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex gap-4">
          <Button type="button" variant="outline" onClick={() => navigate('/bookings')}>
            Cancel
          </Button>
          <Button type="submit" disabled={createBooking.isPending}>
            {createBooking.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              'Create Booking'
            )}
          </Button>
        </div>
      </form>

      {/* Customer Selection Modal */}
      <Modal isOpen={showCustomerModal} onClose={() => setShowCustomerModal(false)}>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Select Customer</h3>
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <Input
              placeholder="Search customers..."
              value={customerSearch}
              onChange={(e) => setCustomerSearch(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="max-h-96 overflow-y-auto">
            {customers?.map(customer => (
              <button
                key={customer.id}
                type="button"
                onClick={() => handleCustomerSelect(customer)}
                className="w-full text-left p-3 hover:bg-gray-50 rounded-lg"
              >
                <p className="font-medium">{customer.name}</p>
                <p className="text-sm text-gray-500">{customer.phone}</p>
              </button>
            ))}
            {customers?.length === 0 && (
              <p className="text-center text-gray-500 py-4">No customers found</p>
            )}
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default NewBookingPage;
