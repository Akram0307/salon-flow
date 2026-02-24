import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Upload, Loader2, MapPin, Mail, Building, Clock } from 'lucide-react';
import { Button, Card, CardContent, CardHeader, CardTitle, Input } from '@salon-flow/ui';
import { useSalon, useUpdateSalon } from '@salon-flow/shared';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

const DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] as const;
type DayKey = typeof DAYS[number];

interface DayHours {
  isOpen: boolean;
  open: string;
  close: string;
}

interface WorkingHoursState {
  monday: DayHours; tuesday: DayHours; wednesday: DayHours; thursday: DayHours;
  friday: DayHours; saturday: DayHours; sunday: DayHours;
}

const DEFAULT_HOURS: WorkingHoursState = {
  monday: { isOpen: true, open: '09:00', close: '19:00' },
  tuesday: { isOpen: true, open: '09:00', close: '19:00' },
  wednesday: { isOpen: true, open: '09:00', close: '19:00' },
  thursday: { isOpen: true, open: '09:00', close: '19:00' },
  friday: { isOpen: true, open: '09:00', close: '19:00' },
  saturday: { isOpen: true, open: '09:00', close: '19:00' },
  sunday: { isOpen: false, open: '09:00', close: '19:00' },
};

const ProfilePage: React.FC = () => {
  const { salon, isLoading } = useSalon();
  const updateSalon = useUpdateSalon();
  const [uploading, setUploading] = useState(false);
  const [workingHours, setWorkingHours] = useState<WorkingHoursState>(DEFAULT_HOURS);

  const { register, handleSubmit, formState: { errors, isDirty }, reset } = useForm({
    defaultValues: {
      name: '', email: '', phone: '', address: '', city: '', state: '', pincode: '', gstNumber: '',
    },
  });

  React.useEffect(() => {
    if (salon) {
      reset({
        name: salon.name || '', email: salon.email || '', phone: salon.phone || '',
        address: salon.address || '', city: salon.city || '', state: salon.state || '',
        pincode: salon.pincode || '', gstNumber: salon.gstNumber || '',
      });
      if (salon.workingHours) {
        const wh = salon.workingHours;
        setWorkingHours({
          monday: { isOpen: !!wh.monday, open: wh.monday?.open || '09:00', close: wh.monday?.close || '19:00' },
          tuesday: { isOpen: !!wh.tuesday, open: wh.tuesday?.open || '09:00', close: wh.tuesday?.close || '19:00' },
          wednesday: { isOpen: !!wh.wednesday, open: wh.wednesday?.open || '09:00', close: wh.wednesday?.close || '19:00' },
          thursday: { isOpen: !!wh.thursday, open: wh.thursday?.open || '09:00', close: wh.thursday?.close || '19:00' },
          friday: { isOpen: !!wh.friday, open: wh.friday?.open || '09:00', close: wh.friday?.close || '19:00' },
          saturday: { isOpen: !!wh.saturday, open: wh.saturday?.open || '09:00', close: wh.saturday?.close || '19:00' },
          sunday: { isOpen: !!wh.sunday, open: wh.sunday?.open || '09:00', close: wh.sunday?.close || '19:00' },
        });
      }
    }
  }, [salon, reset]);

  const handleLogoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      toast.success('Logo uploaded successfully');
    } catch {
      toast.error('Failed to upload logo');
    } finally {
      setUploading(false);
    }
  };

  const toggleDay = (day: DayKey) => {
    setWorkingHours((prev) => ({ ...prev, [day]: { ...prev[day], isOpen: !prev[day].isOpen } }));
  };

  const updateHours = (day: DayKey, field: 'open' | 'close', value: string) => {
    setWorkingHours((prev) => ({ ...prev, [day]: { ...prev[day], [field]: value } }));
  };

  const onSubmit = async (formData: any) => {
    try {
      await updateSalon.mutateAsync({
        ...formData,
        workingHours: Object.fromEntries(
          DAYS.map((d) => [d, workingHours[d].isOpen ? { open: workingHours[d].open, close: workingHours[d].close } : null])
        ),
      });
      toast.success('Profile updated successfully');
    } catch {
      toast.error('Failed to update profile');
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-gray-200 animate-pulse rounded" />
        <div className="h-96 bg-gray-200 animate-pulse rounded-lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Salon Profile</h1>
        <Button onClick={handleSubmit(onSubmit)} disabled={!isDirty && false || updateSalon.isPending} className="min-h-[44px]">
          {updateSalon.isPending ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Saving...</> : 'Save Changes'}
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Basic Information</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Salon Name *</label>
              <Input {...register('name', { required: 'Salon name is required' })} />
              {errors.name && <p className="text-sm text-rose-500 mt-1">{errors.name.message}</p>}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div><label className="block text-sm font-medium mb-1"><Mail className="w-4 h-4 inline mr-1" />Email</label><Input {...register('email')} type="email" /></div>
              <div><label className="block text-sm font-medium mb-1">Phone *</label><Input {...register('phone', { required: 'Phone is required' })} /></div>
            </div>
            <div><label className="block text-sm font-medium mb-1"><MapPin className="w-4 h-4 inline mr-1" />GST Number</label><Input {...register('gstNumber')} placeholder="22AAAAA0000A1Z5" /></div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Salon Logo</CardTitle></CardHeader>
          <CardContent>
            <div className="flex flex-col items-center">
              <div className="w-32 h-32 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-4 overflow-hidden">
                {salon?.logo ? <img src={salon.logo} alt="Logo" className="w-full h-full object-cover" /> : <Upload className="w-8 h-8 text-gray-400" />}
              </div>
              <label className="cursor-pointer">
                <input type="file" accept="image/*" className="hidden" onChange={handleLogoUpload} disabled={uploading} />
                <Button variant="outline" disabled={uploading} className="min-h-[44px]">
                  {uploading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Uploading...</> : <><Upload className="w-4 h-4 mr-2" />Upload Logo</>}
                </Button>
              </label>
              <p className="text-xs text-gray-500 mt-2">Recommended: 512x512px, max 2MB</p>
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader><CardTitle><Building className="w-5 h-5 inline mr-2" />Address</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div><label className="block text-sm font-medium mb-1">Street Address</label><Input {...register('address')} /></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div><label className="block text-sm font-medium mb-1">City</label><Input {...register('city')} /></div>
              <div><label className="block text-sm font-medium mb-1">State</label><Input {...register('state')} /></div>
              <div><label className="block text-sm font-medium mb-1">Pincode</label><Input {...register('pincode')} /></div>
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader><CardTitle><Clock className="w-5 h-5 inline mr-2" />Working Hours</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {DAYS.map((day) => (
                <div key={day} className={cn('flex items-center gap-4 p-3 rounded-lg', workingHours[day].isOpen ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-900/50')}>
                  <button type="button" onClick={() => toggleDay(day)} className={cn('w-12 h-6 rounded-full transition-colors relative', workingHours[day].isOpen ? 'bg-indigo-600' : 'bg-gray-300')}>
                    <span className={cn('absolute top-1 w-4 h-4 bg-white rounded-full transition-transform', workingHours[day].isOpen ? 'left-7' : 'left-1')} />
                  </button>
                  <span className="w-24 font-medium text-gray-700 dark:text-gray-300 capitalize">{day}</span>
                  {workingHours[day].isOpen ? (
                    <div className="flex items-center gap-2 flex-1">
                      <input type="time" value={workingHours[day].open} onChange={(e) => updateHours(day, 'open', e.target.value)} className="px-2 py-1 border rounded dark:bg-gray-800" />
                      <span className="text-gray-500">to</span>
                      <input type="time" value={workingHours[day].close} onChange={(e) => updateHours(day, 'close', e.target.value)} className="px-2 py-1 border rounded dark:bg-gray-800" />
                    </div>
                  ) : <span className="text-gray-500 italic">Closed</span>}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ProfilePage;
