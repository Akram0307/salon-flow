import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useCustomer, useCreateCustomer, useUpdateCustomer } from '@salon-flow/shared';
import { 
  Card, 
  Button, 
  Input, 
} from '@salon-flow/ui';
import { 
  ArrowLeft,
  User,
  Phone,
  Mail,
  Gift,
  Save,
  Loader2,
} from 'lucide-react';

const customerSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  phone: z.string().min(10, 'Valid phone number is required'),
  email: z.string().email('Valid email is required').optional().or(z.literal('')),
  address: z.string().optional(),
  birthday: z.string().optional(),
  anniversary: z.string().optional(),
  gender: z.enum(['male', 'female', 'other', 'prefer_not_to_say']).optional(),
  notes: z.string().optional(),
  membershipTier: z.enum(['none', 'bronze', 'silver', 'gold']).optional(),
});

type CustomerFormData = z.infer<typeof customerSchema>;

const CustomerFormPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  const { data: existingCustomer, isLoading: isLoadingCustomer } = useCustomer(id!);
  const createCustomer = useCreateCustomer();
  const updateCustomer = useUpdateCustomer();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<CustomerFormData>({
    resolver: zodResolver(customerSchema),
    defaultValues: {
      name: '',
      phone: '',
      email: '',
      address: '',
      birthday: '',
      anniversary: '',
      gender: 'prefer_not_to_say',
      notes: '',
      membershipTier: 'none',
    },
  });

  // Load existing customer data for editing
  useEffect(() => {
    if (existingCustomer) {
      reset({
        name: existingCustomer.name || '',
        phone: existingCustomer.phone || '',
        email: existingCustomer.email || '',
        address: existingCustomer.address || '',
        birthday: existingCustomer.birthday || '',
        anniversary: existingCustomer.anniversary || '',
        gender: existingCustomer.gender || 'prefer_not_to_say',
        notes: existingCustomer.notes || '',
        membershipTier: (existingCustomer.membershipTier === 'platinum' ? 'gold' : existingCustomer.membershipTier) || 'none',
      });
    }
  }, [existingCustomer, reset]);

  const onSubmit = async (data: CustomerFormData) => {
    // Cast to any to handle type mismatches
    const submitData: any = {
      firstName: data.name.split(' ')[0] || '',
      lastName: data.name.split(' ').slice(1).join(' ') || '',
      phone: data.phone,
      email: data.email,
      address: data.address,
      birthday: data.birthday,
      anniversary: data.anniversary,
      gender: data.gender === 'prefer_not_to_say' ? 'other' : data.gender,
      notes: data.notes,
      membershipTier: data.membershipTier || 'none',
    };
    try {
      if (isEditing) {
        await updateCustomer.mutateAsync({ id: id!, data: submitData });
      } else {
        await createCustomer.mutateAsync(submitData);
      }
      navigate('/customers');
    } catch (error) {
      console.error('Failed to save customer:', error);
    }
  };

  if (isLoadingCustomer) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {isEditing ? 'Edit Customer' : 'Add New Customer'}
          </h1>
          <p className="text-gray-500 mt-1">
            {isEditing ? 'Update customer information' : 'Create a new customer profile'}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Form */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Information */}
            <Card padding="lg">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
              
              <div className="grid md:grid-cols-2 gap-4">
                <Input
                  {...register('name')}
                  label="Full Name"
                  placeholder="Enter customer name"
                  error={errors.name?.message}
                  leftIcon={<User className="h-4 w-4" />}
                  required
                />

                <Input
                  {...register('phone')}
                  type="tel"
                  label="Phone Number"
                  placeholder="+91 9876543210"
                  error={errors.phone?.message}
                  leftIcon={<Phone className="h-4 w-4" />}
                  required
                />

                <Input
                  {...register('email')}
                  type="email"
                  label="Email Address"
                  placeholder="customer@example.com"
                  error={errors.email?.message}
                  leftIcon={<Mail className="h-4 w-4" />}
                />

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
                  <select
                    {...register('gender')}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="prefer_not_to_say">Prefer not to say</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
            </Card>

            {/* Address & Personal */}
            <Card padding="lg">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Address & Personal Details</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                  <textarea
                    {...register('address')}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Enter full address"
                  />
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <Input
                    {...register('birthday')}
                    type="date"
                    label="Birthday"
                    error={errors.birthday?.message}
                    leftIcon={<Gift className="h-4 w-4" />}
                  />

                  <Input
                    {...register('anniversary')}
                    type="date"
                    label="Anniversary"
                    error={errors.anniversary?.message}
                  />
                </div>
              </div>
            </Card>

            {/* Membership & Notes */}
            <Card padding="lg">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Membership & Notes</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Membership Tier</label>
                  <select
                    {...register('membershipTier')}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="none">Regular (No Membership)</option>
                    <option value="bronze">Bronze</option>
                    <option value="silver">Silver</option>
                    <option value="gold">Gold</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                  <textarea
                    {...register('notes')}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Add any notes about this customer (preferences, allergies, etc.)"
                  />
                </div>
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Actions */}
            <Card padding="lg">
              <h3 className="text-sm font-medium text-gray-500 mb-4">Actions</h3>
              <div className="space-y-3">
                <Button
                  type="submit"
                  fullWidth
                  isLoading={isSubmitting || createCustomer.isPending || updateCustomer.isPending}
                  leftIcon={<Save className="h-4 w-4" />}
                >
                  {isEditing ? 'Update Customer' : 'Create Customer'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  fullWidth
                  onClick={() => navigate(-1)}
                >
                  Cancel
                </Button>
              </div>
            </Card>

            {/* Tips */}
            <Card padding="lg">
              <h3 className="text-sm font-medium text-gray-500 mb-4">Tips</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <span className="text-primary-500 mt-0.5">•</span>
                  <span>Phone number is required for booking confirmations</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-500 mt-0.5">•</span>
                  <span>Birthday info helps send special offers</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-500 mt-0.5">•</span>
                  <span>Notes help personalize service</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-500 mt-0.5">•</span>
                  <span>Membership tiers unlock loyalty benefits</span>
                </li>
              </ul>
            </Card>
          </div>
        </div>
      </form>
    </div>
  );
};

export default CustomerFormPage;
