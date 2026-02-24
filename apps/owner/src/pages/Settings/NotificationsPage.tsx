import React from 'react';
import { useForm } from 'react-hook-form';
import { Save, Bell, Mail, MessageSquare, Smartphone } from 'lucide-react';
import { useSalon, useUpdateSalon, NotificationSettings } from '@salon-flow/shared';
import { Button, Card, CardContent, CardHeader, CardTitle, Input } from '@salon-flow/ui';

const NotificationsPage: React.FC = () => {
  const { salon, isLoading } = useSalon();
  const updateSalon = useUpdateSalon();

  const { register, handleSubmit, reset } = useForm<NotificationSettings>({
    defaultValues: {
      email_notifications: {
        enabled: true,
        new_booking: true,
        cancellation: true,
        reminder: true,
        marketing: false,
        daily_summary: false,
        weekly_report: true,
        monthly_report: true,
      },
      sms_notifications: {
        enabled: true,
        new_booking: true,
        cancellation: true,
        reminder: true,
        marketing: false,
      },
      whatsapp_notifications: {
        enabled: true,
        new_booking: true,
        cancellation: true,
        reminder: true,
        marketing: false,
      },
      push_notifications: {
        enabled: true,
        new_booking: true,
        cancellation: true,
        reminder: true,
      },
      quiet_hours: {
        enabled: false,
        start_time: '22:00',
        end_time: '08:00',
      },
    },
  });

  React.useEffect(() => {
    if (salon?.notificationSettings) {
      reset(salon.notificationSettings);
    }
  }, [salon, reset]);

  const onSubmit = async (data: NotificationSettings) => {
    await updateSalon.mutateAsync({ notificationSettings: data });
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
      <h1 className="text-2xl font-bold text-gray-900">Notification Settings</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Email Notifications */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Mail className="w-5 h-5 text-primary-600" />
              <CardTitle>Email Notifications</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                className="w-4 h-4 text-primary-600 border-gray-300 rounded"
                {...register('email_notifications.enabled')}
              />
              <span className="ml-2">Enable email notifications</span>
            </label>
            <div className="grid grid-cols-2 gap-4 ml-6">
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4" {...register('email_notifications.new_booking')} />
                <span className="ml-2 text-sm">New bookings</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4" {...register('email_notifications.cancellation')} />
                <span className="ml-2 text-sm">Cancellations</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4" {...register('email_notifications.reminder')} />
                <span className="ml-2 text-sm">Reminders</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4" {...register('email_notifications.marketing')} />
                <span className="ml-2 text-sm">Marketing</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4" {...register('email_notifications.daily_summary')} />
                <span className="ml-2 text-sm">Daily summary</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4" {...register('email_notifications.weekly_report')} />
                <span className="ml-2 text-sm">Weekly report</span>
              </label>
            </div>
          </CardContent>
        </Card>

        {/* SMS Notifications */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-primary-600" />
              <CardTitle>SMS Notifications</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                className="w-4 h-4 text-primary-600 border-gray-300 rounded"
                {...register('sms_notifications.enabled')}
              />
              <span className="ml-2">Enable SMS notifications</span>
            </label>
            <div className="grid grid-cols-2 gap-4 ml-6">
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4" {...register('sms_notifications.new_booking')} />
                <span className="ml-2 text-sm">New bookings</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4" {...register('sms_notifications.cancellation')} />
                <span className="ml-2 text-sm">Cancellations</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4" {...register('sms_notifications.reminder')} />
                <span className="ml-2 text-sm">Reminders</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4" {...register('sms_notifications.marketing')} />
                <span className="ml-2 text-sm">Marketing</span>
              </label>
            </div>
          </CardContent>
        </Card>

        {/* WhatsApp Notifications */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Smartphone className="w-5 h-5 text-primary-600" />
              <CardTitle>WhatsApp Notifications</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                className="w-4 h-4 text-primary-600 border-gray-300 rounded"
                {...register('whatsapp_notifications.enabled')}
              />
              <span className="ml-2">Enable WhatsApp notifications</span>
            </label>
            <div className="grid grid-cols-2 gap-4 ml-6">
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4" {...register('whatsapp_notifications.new_booking')} />
                <span className="ml-2 text-sm">New bookings</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4" {...register('whatsapp_notifications.cancellation')} />
                <span className="ml-2 text-sm">Cancellations</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4" {...register('whatsapp_notifications.reminder')} />
                <span className="ml-2 text-sm">Reminders</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4" {...register('whatsapp_notifications.marketing')} />
                <span className="ml-2 text-sm">Marketing</span>
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Quiet Hours */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Bell className="w-5 h-5 text-primary-600" />
              <CardTitle>Quiet Hours</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                className="w-4 h-4 text-primary-600 border-gray-300 rounded"
                {...register('quiet_hours.enabled')}
              />
              <span className="ml-2">Enable quiet hours</span>
            </label>
            <div className="flex items-center gap-4 ml-6">
              <div>
                <label className="text-sm text-gray-600">Start time</label>
                <Input type="time" className="w-32" {...register('quiet_hours.start_time')} />
              </div>
              <div>
                <label className="text-sm text-gray-600">End time</label>
                <Input type="time" className="w-32" {...register('quiet_hours.end_time')} />
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button type="submit" disabled={updateSalon.isPending}>
            <Save className="w-4 h-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </form>
    </div>
  );
};

export default NotificationsPage;
