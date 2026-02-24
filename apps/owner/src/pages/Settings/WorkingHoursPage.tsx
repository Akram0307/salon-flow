import React from 'react';
import { useForm } from 'react-hook-form';
import { Save } from 'lucide-react';
import { useSalon, useUpdateSalon, WorkingHours, SalonHours } from '@salon-flow/shared';
import { Button, Card, CardContent, CardHeader, CardTitle, Input } from '@salon-flow/ui';

const days = [
  { key: 'monday', label: 'Monday' },
  { key: 'tuesday', label: 'Tuesday' },
  { key: 'wednesday', label: 'Wednesday' },
  { key: 'thursday', label: 'Thursday' },
  { key: 'friday', label: 'Friday' },
  { key: 'saturday', label: 'Saturday' },
  { key: 'sunday', label: 'Sunday' },
];

interface WorkingHoursFormData {
  monday: { open: string; close: string; closed: boolean };
  tuesday: { open: string; close: string; closed: boolean };
  wednesday: { open: string; close: string; closed: boolean };
  thursday: { open: string; close: string; closed: boolean };
  friday: { open: string; close: string; closed: boolean };
  saturday: { open: string; close: string; closed: boolean };
  sunday: { open: string; close: string; closed: boolean };
}

const WorkingHoursPage: React.FC = () => {
  const { salon, isLoading } = useSalon();
  const updateSalon = useUpdateSalon();

  const defaultValues: WorkingHoursFormData = {
    monday: { open: '09:00', close: '21:00', closed: false },
    tuesday: { open: '09:00', close: '21:00', closed: false },
    wednesday: { open: '09:00', close: '21:00', closed: false },
    thursday: { open: '09:00', close: '21:00', closed: false },
    friday: { open: '09:00', close: '21:00', closed: false },
    saturday: { open: '09:00', close: '21:00', closed: false },
    sunday: { open: '10:00', close: '18:00', closed: false },
  };

  const { register, handleSubmit, watch, setValue } = useForm<WorkingHoursFormData>({
    defaultValues,
  });

  React.useEffect(() => {
    if (salon?.workingHours) {
      days.forEach(day => {
        const hours = salon.workingHours![day.key as keyof WorkingHours];
        setValue(day.key as keyof WorkingHoursFormData, {
          open: hours?.open || '09:00',
          close: hours?.close || '21:00',
          closed: !hours,
        });
      });
    }
  }, [salon, setValue]);

  const onSubmit = async (data: WorkingHoursFormData) => {
    const workingHours: WorkingHours = {} as WorkingHours;
    days.forEach(day => {
      const dayData = data[day.key as keyof WorkingHoursFormData];
      (workingHours as unknown as Record<string, SalonHours | null>)[day.key] = dayData.closed
        ? null
        : { open: dayData.open, close: dayData.close };
    });

    await updateSalon.mutateAsync({ workingHours });
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
      <h1 className="text-2xl font-bold text-gray-900">Working Hours</h1>

      <Card>
        <CardHeader>
          <CardTitle>Set Salon Hours</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {days.map(day => {
              const dayData = watch(day.key as keyof WorkingHoursFormData);
              return (
                <div key={day.key} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="w-32">
                    <span className="font-medium">{day.label}</span>
                  </div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      className="w-4 h-4 text-primary-600 border-gray-300 rounded"
                      checked={dayData?.closed}
                      onChange={(e) => setValue(`${day.key}.closed` as any, e.target.checked)}
                    />
                    <span className="ml-2 text-sm text-gray-600">Closed</span>
                  </label>
                  {!dayData?.closed && (
                    <>
                      <div className="flex items-center gap-2">
                        <label className="text-sm text-gray-600">Open:</label>
                        <Input
                          type="time"
                          className="w-32"
                          {...register(`${day.key}.open` as any)}
                        />
                      </div>
                      <div className="flex items-center gap-2">
                        <label className="text-sm text-gray-600">Close:</label>
                        <Input
                          type="time"
                          className="w-32"
                          {...register(`${day.key}.close` as any)}
                        />
                      </div>
                    </>
                  )}
                </div>
              );
            })}

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

export default WorkingHoursPage;
