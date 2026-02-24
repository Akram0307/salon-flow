/**
 * Salon Flow Owner PWA - Onboarding Step 5: Set Business Hours
 * Business hours configuration with day-by-day control
 */

import React, { useState } from 'react';
import { Button } from '@/components/atoms/Button';
import { useOnboardingStore, type BusinessHoursData, type DayHours } from '@/stores/onboardingStore';
import { cn } from '@/lib/utils';
import {
  Clock,
  Calendar,
  Copy,
  Check,
  Sun,
  Moon,
  Coffee,
  Store,
  AlertCircle,
} from 'lucide-react';

// Days configuration
const DAYS = [
  { id: 'monday', name: 'Monday', short: 'Mon' },
  { id: 'tuesday', name: 'Tuesday', short: 'Tue' },
  { id: 'wednesday', name: 'Wednesday', short: 'Wed' },
  { id: 'thursday', name: 'Thursday', short: 'Thu' },
  { id: 'friday', name: 'Friday', short: 'Fri' },
  { id: 'saturday', name: 'Saturday', short: 'Sat' },
  { id: 'sunday', name: 'Sunday', short: 'Sun' },
] as const;

type DayId = typeof DAYS[number]['id'];

// Time slot options
const TIME_SLOTS = Array.from({ length: 24 * 2 }, (_, i) => {
  const hour = Math.floor(i / 2);
  const minute = (i % 2) * 30;
  return `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
});

// Day Card Component
interface DayCardProps {
  day: typeof DAYS[number];
  hours: DayHours;
  onUpdate: (hours: Partial<DayHours>) => void;
  isToday: boolean;
}

const DayCard: React.FC<DayCardProps> = ({ day, hours, onUpdate, isToday }) => {
  const [showBreaks, setShowBreaks] = useState(false);

  const addBreak = () => {
    const newBreaks = [...hours.breaks, { start: '13:00', end: '14:00' }];
    onUpdate({ breaks: newBreaks });
  };

  const removeBreak = (index: number) => {
    const newBreaks = hours.breaks.filter((_, i) => i !== index);
    onUpdate({ breaks: newBreaks });
  };

  const updateBreak = (index: number, field: 'start' | 'end', value: string) => {
    const newBreaks = hours.breaks.map((b, i) =>
      i === index ? { ...b, [field]: value } : b
    );
    onUpdate({ breaks: newBreaks });
  };

  return (
    <div className={cn(
      'rounded-xl border-2 overflow-hidden transition-all',
      isToday ? 'border-primary-500 ring-2 ring-primary-500/20' : 'border-surface-200 dark:border-surface-700',
      hours.isClosed && 'opacity-60'
    )}>
      {/* Header */}
      <div className="p-4 bg-surface-50 dark:bg-surface-800/50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={cn(
            'w-10 h-10 rounded-lg flex items-center justify-center font-semibold',
            isToday
              ? 'bg-primary-500 text-white'
              : 'bg-surface-200 dark:bg-surface-700 text-surface-700 dark:text-surface-300'
          )}>
            {day.short}
          </div>
          <div>
            <p className="font-medium text-surface-900 dark:text-white">{day.name}</p>
            {isToday && <p className="text-xs text-primary-600">Today</p>}
          </div>
        </div>

        {/* Closed Toggle */}
        <label className="flex items-center gap-2 cursor-pointer">
          <span className="text-sm text-surface-600 dark:text-surface-400">
            {hours.isClosed ? 'Closed' : 'Open'}
          </span>
          <button
            onClick={() => onUpdate({ isClosed: !hours.isClosed })}
            className={cn(
              'w-12 h-6 rounded-full transition-colors relative',
              hours.isClosed ? 'bg-surface-300 dark:bg-surface-600' : 'bg-success-500'
            )}
          >
            <div className={cn(
              'w-5 h-5 rounded-full bg-white absolute top-0.5 transition-all',
              hours.isClosed ? 'left-0.5' : 'left-6'
            )} />
          </button>
        </label>
      </div>

      {/* Time Controls */}
      {!hours.isClosed && (
        <div className="p-4 space-y-4">
          {/* Open/Close Times */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1">
                <span className="flex items-center gap-1">
                  <Sun className="w-4 h-4 text-amber-500" />
                  Opens
                </span>
              </label>
              <select
                value={hours.open}
                onChange={(e) => onUpdate({ open: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-800 text-surface-900 dark:text-white"
              >
                {TIME_SLOTS.map(time => (
                  <option key={time} value={time}>
                    {time}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1">
                <span className="flex items-center gap-1">
                  <Moon className="w-4 h-4 text-indigo-500" />
                  Closes
                </span>
              </label>
              <select
                value={hours.close}
                onChange={(e) => onUpdate({ close: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-800 text-surface-900 dark:text-white"
              >
                {TIME_SLOTS.map(time => (
                  <option key={time} value={time}>
                    {time}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Break Times */}
          <div>
            <button
              onClick={() => setShowBreaks(!showBreaks)}
              className="flex items-center gap-2 text-sm text-surface-600 dark:text-surface-400 hover:text-primary-600"
            >
              <Coffee className="w-4 h-4" />
              {hours.breaks.length > 0
                ? `${hours.breaks.length} break${hours.breaks.length > 1 ? 's' : ''} set`
                : 'Add breaks'}
              <span className="text-xs">{showBreaks ? '▲' : '▼'}</span>
            </button>

            {showBreaks && (
              <div className="mt-3 space-y-2">
                {hours.breaks.map((breakTime, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <span className="text-sm text-surface-500">Break {index + 1}:</span>
                    <select
                      value={breakTime.start}
                      onChange={(e) => updateBreak(index, 'start', e.target.value)}
                      className="px-2 py-1 rounded border border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-800 text-sm"
                    >
                      {TIME_SLOTS.map(time => (
                        <option key={time} value={time}>{time}</option>
                      ))}
                    </select>
                    <span className="text-surface-400">to</span>
                    <select
                      value={breakTime.end}
                      onChange={(e) => updateBreak(index, 'end', e.target.value)}
                      className="px-2 py-1 rounded border border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-800 text-sm"
                    >
                      {TIME_SLOTS.map(time => (
                        <option key={time} value={time}>{time}</option>
                      ))}
                    </select>
                    <button
                      onClick={() => removeBreak(index)}
                      className="text-red-500 hover:text-red-600"
                    >
                      ×
                    </button>
                  </div>
                ))}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={addBreak}
                  leftIcon={<span className="text-lg">+</span>}
                >
                  Add Break
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Weekly Summary Component
const WeeklySummary: React.FC<{ hours: Partial<BusinessHoursData> }> = ({ hours }) => {
  const openDays = DAYS.filter(day => !hours[day.id]?.isClosed).length;
  const closedDays = 7 - openDays;
  const totalHours = DAYS.reduce((sum, day) => {
    if (hours[day.id]?.isClosed) return sum;
    const open = hours[day.id]?.open || '09:00';
    const close = hours[day.id]?.close || '21:00';
    const [openH, openM] = open.split(':').map(Number);
    const [closeH, closeM] = close.split(':').map(Number);
    return sum + (closeH - openH) + (closeM - openM) / 60;
  }, 0);

  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="bg-success-50 dark:bg-success-900/20 rounded-xl p-4 border border-success-200 dark:border-success-800">
        <div className="flex items-center gap-2 mb-1">
          <Store className="w-5 h-5 text-success-600" />
          <span className="text-sm font-medium text-success-700 dark:text-success-300">Open Days</span>
        </div>
        <p className="text-2xl font-bold text-success-900 dark:text-success-100">{openDays}</p>
        <p className="text-xs text-success-600">per week</p>
      </div>

      <div className="bg-surface-50 dark:bg-surface-800 rounded-xl p-4 border border-surface-200 dark:border-surface-700">
        <div className="flex items-center gap-2 mb-1">
          <Clock className="w-5 h-5 text-surface-600" />
          <span className="text-sm font-medium text-surface-700 dark:text-surface-300">Weekly Hours</span>
        </div>
        <p className="text-2xl font-bold text-surface-900 dark:text-white">{Math.round(totalHours)}h</p>
        <p className="text-xs text-surface-500">total availability</p>
      </div>

      <div className="bg-amber-50 dark:bg-amber-900/20 rounded-xl p-4 border border-amber-200 dark:border-amber-800">
        <div className="flex items-center gap-2 mb-1">
          <Calendar className="w-5 h-5 text-amber-600" />
          <span className="text-sm font-medium text-amber-700 dark:text-amber-300">Closed Days</span>
        </div>
        <p className="text-2xl font-bold text-amber-900 dark:text-amber-100">{closedDays}</p>
        <p className="text-xs text-amber-600">per week</p>
      </div>
    </div>
  );
};

export const Step5Hours: React.FC = () => {
  const { businessHours, setBusinessHours, updateDayHours } = useOnboardingStore();
  const [copiedFrom, setCopiedFrom] = useState<DayId | null>(null);

  const today = new Date().getDay();
  const todayId = DAYS[today === 0 ? 6 : today - 1].id;

  const handleCopyToAll = (fromDay: DayId) => {
    const sourceHours = businessHours[fromDay];
    if (!sourceHours) return;

    const newHours: Partial<BusinessHoursData> = {};
    DAYS.forEach(day => {
      newHours[day.id] = { ...sourceHours };
    });
    setBusinessHours(newHours);
    setCopiedFrom(fromDay);
    setTimeout(() => setCopiedFrom(null), 2000);
  };

  const getDayHours = (dayId: DayId): DayHours => {
    return businessHours[dayId] || {
      open: '09:00',
      close: '21:00',
      isOpen: true,
      isClosed: false,
      breaks: [],
    } as any;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-surface-900 dark:text-white mb-2">
          Set Business Hours
        </h1>
        <p className="text-surface-600 dark:text-surface-400">
          Configure when your salon is open for bookings
        </p>
      </div>

      {/* Weekly Summary */}
      <WeeklySummary hours={businessHours} />

      {/* Copy Actions */}
      <div className="flex items-center gap-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
        <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0" />
        <p className="text-sm text-blue-800 dark:text-blue-200 flex-1">
          Set hours for one day, then copy to all other days
        </p>
        <div className="flex gap-2">
          {DAYS.slice(0, 3).map(day => (
            <button
              key={day.id}
              onClick={() => handleCopyToAll(day.id)}
              className="px-3 py-1.5 text-sm bg-white dark:bg-surface-800 border border-blue-300 dark:border-blue-700 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors flex items-center gap-1"
            >
              <Copy className="w-3.5 h-3.5" />
              Copy {day.short}
              {copiedFrom === day.id && <Check className="w-3.5 h-3.5 text-success-500" />}
            </button>
          ))}
        </div>
      </div>

      {/* Days Grid */}
      <div className="space-y-4">
        {DAYS.map(day => (
          <DayCard
            key={day.id}
            day={day}
            hours={getDayHours(day.id)}
            onUpdate={(hours) => updateDayHours(day.id, hours)}
            isToday={day.id === todayId}
          />
        ))}
      </div>

      {/* Tips */}
      <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-4">
        <h4 className="text-sm font-semibold text-green-800 dark:text-green-200 mb-2">
          💡 Tips for Setting Hours
        </h4>
        <ul className="text-sm text-green-700 dark:text-green-300 space-y-1 list-disc list-inside">
          <li>Consider peak hours (evenings, weekends) when setting availability</li>
          <li>Add break times for lunch and staff rest periods</li>
          <li>Keep Sunday hours shorter if that's typical for your area</li>
          <li>You can always adjust these later from settings</li>
        </ul>
      </div>
    </div>
  );
};

export default Step5Hours;
