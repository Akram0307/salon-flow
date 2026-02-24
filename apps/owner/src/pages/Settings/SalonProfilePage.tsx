import React from 'react';
import { useForm } from 'react-hook-form';
import { Save, Building2, MapPin, Phone, Mail } from 'lucide-react';
import { useSalon, useUpdateSalon } from '@salon-flow/shared';
import { Button, Card, CardContent, CardHeader, CardTitle, Input } from '@salon-flow/ui';

interface SalonProfileFormData {
  name: string;
  address: string;
  city: string;
  state: string;
  pincode: string;
  phone: string;
  email: string;
  gstNumber: string;
}

const SalonProfilePage: React.FC = () => {
  const { salon, isLoading } = useSalon();
  const updateSalon = useUpdateSalon();

  const { register, handleSubmit, formState: { errors }, reset } = useForm<SalonProfileFormData>({
    defaultValues: {
      name: '',
      address: '',
      city: '',
      state: '',
      pincode: '',
      phone: '',
      email: '',
      gstNumber: '',
    },
  });

  React.useEffect(() => {
    if (salon) {
      reset({
        name: salon.name,
        address: salon.address,
        city: salon.city,
        state: salon.state,
        pincode: salon.pincode,
        phone: salon.phone,
        email: salon.email,
        gstNumber: salon.gstNumber || '',
      });
    }
  }, [salon, reset]);

  const onSubmit = async (data: SalonProfileFormData) => {
    await updateSalon.mutateAsync(data);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Salon Profile</h1>

      <Card>
        <CardHeader>
          <CardTitle>Basic Information</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Salon Name</label>
                <div className="relative">
                  <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    className="pl-10"
                    {...register('name', { required: 'Name is required' })}
                    error={errors.name?.message}
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
                <label className="block text-sm font-medium text-gray-700 mb-1">GST Number</label>
                <Input
                  {...register('gstNumber')}
                  placeholder="Optional"
                />
              </div>
            </div>

            <div className="border-t pt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Address</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Street Address</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                    <textarea
                      className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                      rows={3}
                      {...register('address', { required: 'Address is required' })}
                    />
                  </div>
                  {errors.address && <p className="text-sm text-red-500 mt-1">{errors.address.message}</p>}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                    <Input {...register('city', { required: 'City is required' })} error={errors.city?.message} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                    <Input {...register('state', { required: 'State is required' })} error={errors.state?.message} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Pincode</label>
                    <Input {...register('pincode', { required: 'Pincode is required' })} error={errors.pincode?.message} />
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-end">
              <Button type="submit" disabled={updateSalon.isPending}>
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default SalonProfilePage;
