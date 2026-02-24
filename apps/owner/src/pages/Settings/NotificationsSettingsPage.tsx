import React, { useState } from 'react';
import { Bell, Mail, MessageSquare, Smartphone, Clock, Loader2 } from 'lucide-react';
import { Button, Card, CardContent, CardHeader, CardTitle } from '@salon-flow/ui';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface ChannelConfig {
  enabled: boolean;
  new_booking: boolean;
  cancellation: boolean;
  reminder: boolean;
  marketing?: boolean;
  daily_summary?: boolean;
  weekly_report?: boolean;
}

const NotificationsSettingsPage: React.FC = () => {
  const [isSaving, setIsSaving] = useState(false);
  const [quietHours, setQuietHours] = useState({ start: '22:00', end: '08:00' });
  const [email, setEmail] = useState<ChannelConfig>({
    enabled: true, new_booking: true, cancellation: true, reminder: true, marketing: false, daily_summary: true, weekly_report: true,
  });
  const [whatsapp, setWhatsapp] = useState<ChannelConfig>({
    enabled: true, new_booking: true, cancellation: true, reminder: true, marketing: false,
  });
  const [sms, setSms] = useState<ChannelConfig>({
    enabled: false, new_booking: true, cancellation: false, reminder: false,
  });
  const [push, setPush] = useState<ChannelConfig>({
    enabled: true, new_booking: true, cancellation: true, reminder: true,
  });

  const toggleChannel = (setter: React.Dispatch<React.SetStateAction<ChannelConfig>>, key: keyof ChannelConfig) => {
    setter((prev: ChannelConfig) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      toast.success('Notification preferences saved');
    } catch {
      toast.error('Failed to save preferences');
    } finally {
      setIsSaving(false);
    }
  };

  const renderToggle = (label: string, checked: boolean, onChange: () => void) => (
    <div className="flex items-center justify-between py-2">
      <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
      <button
        type="button"
        onClick={onChange}
        className={cn('relative inline-flex h-5 w-9 items-center rounded-full transition-colors', checked ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600')}
      >
        <span className={cn('inline-block h-3 w-3 transform rounded-full bg-white transition-transform', checked ? 'translate-x-5' : 'translate-x-1')} />
      </button>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Notification Preferences</h1>
        <Button onClick={handleSave} disabled={isSaving} className="min-h-[44px]">
          {isSaving ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Saving...</> : 'Save Changes'}
        </Button>
      </div>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Mail className="w-5 h-5 text-indigo-600" />Email Notifications</CardTitle></CardHeader>
        <CardContent className="space-y-1">
          {renderToggle('Enable Email Notifications', email.enabled, () => toggleChannel(setEmail, 'enabled'))}
          {email.enabled && (
            <div className="pl-4 space-y-1 border-l-2 border-indigo-200 ml-2 mt-2">
              {renderToggle('New Bookings', email.new_booking, () => toggleChannel(setEmail, 'new_booking'))}
              {renderToggle('Cancellations', email.cancellation, () => toggleChannel(setEmail, 'cancellation'))}
              {renderToggle('Reminders', email.reminder, () => toggleChannel(setEmail, 'reminder'))}
              {renderToggle('Marketing & Promotions', email.marketing || false, () => toggleChannel(setEmail, 'marketing'))}
              {renderToggle('Daily Summary', email.daily_summary || false, () => toggleChannel(setEmail, 'daily_summary'))}
              {renderToggle('Weekly Reports', email.weekly_report || false, () => toggleChannel(setEmail, 'weekly_report'))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><MessageSquare className="w-5 h-5 text-emerald-600" />WhatsApp Notifications</CardTitle></CardHeader>
        <CardContent className="space-y-1">
          {renderToggle('Enable WhatsApp', whatsapp.enabled, () => toggleChannel(setWhatsapp, 'enabled'))}
          {whatsapp.enabled && (
            <div className="pl-4 space-y-1 border-l-2 border-emerald-200 ml-2 mt-2">
              {renderToggle('Booking Confirmations', whatsapp.new_booking, () => toggleChannel(setWhatsapp, 'new_booking'))}
              {renderToggle('Reminders', whatsapp.reminder, () => toggleChannel(setWhatsapp, 'reminder'))}
              {renderToggle('Promotions', whatsapp.marketing || false, () => toggleChannel(setWhatsapp, 'marketing'))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Smartphone className="w-5 h-5 text-amber-600" />SMS Notifications</CardTitle></CardHeader>
        <CardContent className="space-y-1">
          {renderToggle('Enable SMS (Critical Alerts Only)', sms.enabled, () => toggleChannel(setSms, 'enabled'))}
          {sms.enabled && (
            <div className="pl-4 space-y-1 border-l-2 border-amber-200 ml-2 mt-2">
              {renderToggle('Critical Alerts', sms.new_booking, () => toggleChannel(setSms, 'new_booking'))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Bell className="w-5 h-5 text-rose-600" />Push Notifications</CardTitle></CardHeader>
        <CardContent className="space-y-1">
          {renderToggle('Enable Push Notifications', push.enabled, () => toggleChannel(setPush, 'enabled'))}
          {push.enabled && (
            <div className="pl-4 space-y-1 border-l-2 border-rose-200 ml-2 mt-2">
              {renderToggle('Real-time Alerts', push.new_booking, () => toggleChannel(setPush, 'new_booking'))}
              {renderToggle('Cancellations', push.cancellation, () => toggleChannel(setPush, 'cancellation'))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Clock className="w-5 h-5 text-purple-600" />Quiet Hours</CardTitle></CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500 mb-4">No notifications will be sent during quiet hours</p>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="block text-sm font-medium mb-1">Start Time</label><input type="time" value={quietHours.start} onChange={(e) => setQuietHours((p) => ({ ...p, start: e.target.value }))} className="w-full px-3 py-2 border rounded dark:bg-gray-800" /></div>
            <div><label className="block text-sm font-medium mb-1">End Time</label><input type="time" value={quietHours.end} onChange={(e) => setQuietHours((p) => ({ ...p, end: e.target.value }))} className="w-full px-3 py-2 border rounded dark:bg-gray-800" /></div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default NotificationsSettingsPage;
