import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { ArrowLeft, Save, User, Mail, Phone } from 'lucide-react';
import { useStaff, useCreateStaff, useUpdateStaff, StaffRole, StaffCreate } from '@salon-flow/shared';
import { Button, Card, CardContent, Input } from '@salon-flow/ui';

const roleOptions = [
  { value: 'owner', label: 'Owner' },
  { value: 'manager', label: 'Manager' },
  { value: 'receptionist', label: 'Receptionist' },
  { value: 'stylist', label: 'Stylist' },
  { value: 'senior_stylist', label: 'Senior Stylist' },
  { value: 'colorist', label: 'Colorist' },
  { value: 'therapist', label: 'Therapist' },
];

interface StaffFormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  role: StaffRole;
  specialization: string;
  commission: number;
  isActive: boolean;
}

const StaffFormPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: existingStaff, isLoading: isLoadingStaff } = useStaff(id || '');
  const createStaff = useCreateStaff();
  const updateStaff = useUpdateStaff();

  const isEditing = Boolean(id);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<StaffFormData>({
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      role: 'stylist',
      specialization: '',
      commission: 10,
      isActive: true,
    },
  });

  React.useEffect(() => {
    if (existingStaff) {
      reset({
        firstName: existingStaff.firstName,
        lastName: existingStaff.lastName,
        email: existingStaff.email,
        phone: existingStaff.phone,
        role: existingStaff.role,
        specialization: existingStaff.specialization?.join(', ') || '',
        commission: existingStaff.commission,
        isActive: existingStaff.isActive,
      });
    }
  }, [existingStaff, reset]);

  const onSubmit = async (data: StaffFormData) => {
    try {
      const staffData: StaffCreate = {
        firstName: data.firstName,
        lastName: data.lastName,
        email: data.email,
        phone: data.phone,
        role: data.role,
        specialization: data.specialization.split(',').map(s => s.trim()).filter(Boolean),
        commission: data.commission,
        isActive: data.isActive,
        schedule: [], // Default empty schedule
      };

      if (isEditing && id) {
        await updateStaff.mutateAsync({ id, data: staffData });
      } else {
        await createStaff.mutateAsync(staffData);
      }
      navigate('/staff');
    } catch (error) {
      console.error('Failed to save staff:', error);
    }
  };

  if (isLoadingStaff) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => navigate('/staff')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <h1 className="text-2xl font-bold text-gray-900">
          {isEditing ? 'Edit Staff Member' : 'Add Staff Member'}
        </h1>
      </div>

      <Card>
        <CardContent className="p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    className="pl-10"
                    {...register('firstName', { required: 'First name is required' })}
                    error={errors.firstName?.message}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                <Input
                  {...register('lastName', { required: 'Last name is required' })}
                  error={errors.lastName?.message}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    type="email"
                    className="pl-10"
                    {...register('email', { required: 'Email is required' })}
                    error={errors.email?.message}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    type="tel"
                    className="pl-10"
                    {...register('phone', { required: 'Phone is required' })}
                    error={errors.phone?.message}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <select
                  {...register('role')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  {roleOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Specialization</label>
                <Input
                  placeholder="e.g., Haircut, Coloring, Spa"
                  {...register('specialization')}
                />
                <p className="text-xs text-gray-500 mt-1">Comma-separated list</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Commission (%)</label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  {...register('commission', { valueAsNumber: true })}
                />
              </div>

              <div className="flex items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded"
                    {...register('isActive')}
                  />
                  <span className="ml-2 text-sm text-gray-700">Active</span>
                </label>
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <Button type="button" variant="outline" onClick={() => navigate('/staff')}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                <Save className="w-4 h-4 mr-2" />
                {isEditing ? 'Update' : 'Create'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default StaffFormPage;
