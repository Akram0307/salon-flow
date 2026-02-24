/**
 * Salon Flow Owner PWA - Onboarding Step 2: Configure Layout
 * Salon space configuration with visual preview
 */

import React, { useState, useEffect } from 'react';
import { useOnboardingStore, type LayoutData } from '@/stores/onboardingStore';
import { cn } from '@/lib/utils';
import {
  Armchair,
  Users,
  DoorOpen,
  Sparkles,
  Bath,
  Minus,
  Plus,
  LayoutGrid,
  Info,
} from 'lucide-react';

// Counter Component
interface CounterProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  label: string;
  icon: React.ReactNode;
  description?: string;
}

const Counter: React.FC<CounterProps> = ({
  value,
  onChange,
  min = 0,
  max = 50,
  label,
  icon,
  description,
}) => {
  const increment = () => onChange(Math.min(value + 1, max));
  const decrement = () => onChange(Math.max(value - 1, min));

  return (
    <div className="flex items-center justify-between p-4 bg-surface-50 dark:bg-surface-800/50 rounded-xl border border-surface-200 dark:border-surface-700">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center text-primary-600 dark:text-primary-400">
          {icon}
        </div>
        <div>
          <p className="font-medium text-surface-900 dark:text-white">{label}</p>
          {description && (
            <p className="text-xs text-surface-500">{description}</p>
          )}
        </div>
      </div>
      <div className="flex items-center gap-3">
        <button
          onClick={decrement}
          disabled={value <= min}
          className="w-8 h-8 rounded-lg bg-white dark:bg-surface-700 border border-surface-300 dark:border-surface-600 flex items-center justify-center hover:bg-surface-100 dark:hover:bg-surface-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Minus className="w-4 h-4" />
        </button>
        <span className="w-8 text-center font-semibold text-lg text-surface-900 dark:text-white">
          {value}
        </span>
        <button
          onClick={increment}
          disabled={value >= max}
          className="w-8 h-8 rounded-lg bg-white dark:bg-surface-700 border border-surface-300 dark:border-surface-600 flex items-center justify-center hover:bg-surface-100 dark:hover:bg-surface-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

// Toggle Card Component
interface ToggleCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  isActive: boolean;
  onToggle: () => void;
  badge?: string;
}

const ToggleCard: React.FC<ToggleCardProps> = ({
  title,
  description,
  icon,
  isActive,
  onToggle,
  badge,
}) => (
  <button
    onClick={onToggle}
    className={cn(
      'w-full p-4 rounded-xl border-2 text-left transition-all duration-200',
      isActive
        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
        : 'border-surface-200 dark:border-surface-700 bg-white dark:bg-surface-800 hover:border-surface-300 dark:hover:border-surface-600'
    )}
  >
    <div className="flex items-start gap-3">
      <div
        className={cn(
          'w-10 h-10 rounded-lg flex items-center justify-center transition-colors',
          isActive
            ? 'bg-primary-500 text-white'
            : 'bg-surface-100 dark:bg-surface-700 text-surface-500'
        )}
      >
        {icon}
      </div>
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <p className="font-medium text-surface-900 dark:text-white">{title}</p>
          {badge && (
            <span className="px-2 py-0.5 text-xs bg-secondary-100 dark:bg-secondary-900/30 text-secondary-700 dark:text-secondary-400 rounded-full">
              {badge}
            </span>
          )}
        </div>
        <p className="text-sm text-surface-500 mt-1">{description}</p>
      </div>
      <div
        className={cn(
          'w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors',
          isActive
            ? 'border-primary-500 bg-primary-500'
            : 'border-surface-300 dark:border-surface-600'
        )}
      >
        {isActive && <div className="w-2.5 h-2.5 bg-white rounded-full" />}
      </div>
    </div>
  </button>
);

// Visual Layout Preview
const LayoutPreview: React.FC<{ layout: LayoutData }> = ({ layout }) => {
  const totalChairs = layout.mensChairs + layout.womensChairs;
  const totalRooms = layout.serviceRooms + (layout.bridalRoom ? 1 : 0) + layout.treatmentRooms + (layout.spaRoom ? 1 : 0);

  return (
    <div className="bg-surface-50 dark:bg-surface-800/50 rounded-xl p-6 border border-surface-200 dark:border-surface-700">
      <h4 className="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-4 flex items-center gap-2">
        <LayoutGrid className="w-4 h-4" />
        Layout Preview
      </h4>
      
      <div className="space-y-4">
        {/* Chairs Section */}
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <p className="text-xs text-surface-500 mb-2">Styling Chairs</p>
            <div className="flex flex-wrap gap-1">
              {Array.from({ length: Math.min(layout.mensChairs, 8) }).map((_, i) => (
                <div
                  key={`m-${i}`}
                  className="w-6 h-6 bg-blue-100 dark:bg-blue-900/30 rounded flex items-center justify-center"
                  title="Men's Chair"
                >
                  <span className="text-xs">M</span>
                </div>
              ))}
              {layout.mensChairs > 8 && (
                <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900/30 rounded flex items-center justify-center text-xs">
                  +{layout.mensChairs - 8}
                </div>
              )}
              {Array.from({ length: Math.min(layout.womensChairs, 8) }).map((_, i) => (
                <div
                  key={`w-${i}`}
                  className="w-6 h-6 bg-pink-100 dark:bg-pink-900/30 rounded flex items-center justify-center"
                  title="Women's Chair"
                >
                  <span className="text-xs">W</span>
                </div>
              ))}
              {layout.womensChairs > 8 && (
                <div className="w-6 h-6 bg-pink-100 dark:bg-pink-900/30 rounded flex items-center justify-center text-xs">
                  +{layout.womensChairs - 8}
                </div>
              )}
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-surface-900 dark:text-white">{totalChairs}</p>
            <p className="text-xs text-surface-500">Total Chairs</p>
          </div>
        </div>

        {/* Rooms Section */}
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <p className="text-xs text-surface-500 mb-2">Service Rooms</p>
            <div className="flex flex-wrap gap-1">
              {layout.bridalRoom && (
                <div className="px-2 h-6 bg-purple-100 dark:bg-purple-900/30 rounded flex items-center text-xs">
                  Bridal
                </div>
              )}
              {Array.from({ length: Math.min(layout.treatmentRooms, 4) }).map((_, i) => (
                <div
                  key={`t-${i}`}
                  className="px-2 h-6 bg-green-100 dark:bg-green-900/30 rounded flex items-center text-xs"
                >
                  Treatment
                </div>
              ))}
              {layout.treatmentRooms > 4 && (
                <div className="px-2 h-6 bg-green-100 dark:bg-green-900/30 rounded flex items-center text-xs">
                  +{layout.treatmentRooms - 4}
                </div>
              )}
              {layout.spaRoom && (
                <div className="px-2 h-6 bg-teal-100 dark:bg-teal-900/30 rounded flex items-center text-xs">
                  Spa
                </div>
              )}
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-surface-900 dark:text-white">{totalRooms}</p>
            <p className="text-xs text-surface-500">Total Rooms</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export const Step2Layout: React.FC = () => {
  const { layoutData, setLayoutData } = useOnboardingStore();
  const [localLayout, setLocalLayout] = useState<LayoutData>({
    mensChairs: layoutData.mensChairs ?? 6,
    womensChairs: layoutData.womensChairs ?? 4,
    serviceRooms: layoutData.serviceRooms ?? 4,
    bridalRoom: layoutData.bridalRoom ?? 1,
    treatmentRooms: layoutData.treatmentRooms ?? 2,
    spaRoom: layoutData.spaRoom ?? 0,
  });

  // Update store when local changes
  useEffect(() => {
    setLayoutData(localLayout);
  }, [localLayout, setLayoutData]);

  const updateField = <K extends keyof LayoutData>(field: K, value: LayoutData[K]) => {
    setLocalLayout(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-surface-900 dark:text-white mb-2">
          Configure Your Layout
        </h1>
        <p className="text-surface-600 dark:text-surface-400">
          Set up your salon's seating and room configuration
        </p>
      </div>

      {/* Info Banner */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 flex items-start gap-3">
        <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm text-blue-800 dark:text-blue-200">
            This helps us optimize booking slots and manage your resources efficiently.
            You can always update this later in settings.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Configuration Panel */}
        <div className="space-y-6">
          {/* Styling Chairs */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-surface-900 dark:text-white flex items-center gap-2">
              <Armchair className="w-5 h-5 text-primary-500" />
              Styling Chairs
            </h3>
            
            <Counter
              label="Men's Section"
              description="Chairs for men's haircuts & styling"
              icon={<span className="font-bold">M</span>}
              value={localLayout.mensChairs}
              onChange={(value) => updateField('mensChairs', value)}
              min={0}
              max={20}
            />
            
            <Counter
              label="Women's Section"
              description="Chairs for women's services"
              icon={<span className="font-bold">W</span>}
              value={localLayout.womensChairs}
              onChange={(value) => updateField('womensChairs', value)}
              min={0}
              max={20}
            />
          </div>

          {/* Service Rooms */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-surface-900 dark:text-white flex items-center gap-2">
              <DoorOpen className="w-5 h-5 text-secondary-500" />
              Service Rooms
            </h3>

            <ToggleCard
              title="Bridal Room"
              description="Private room for bridal makeup and styling"
              icon={<Sparkles className="w-5 h-5" />}
              isActive={Boolean(localLayout.bridalRoom)}
              onToggle={() => updateField('bridalRoom', localLayout.bridalRoom ? 0 : 1)}
              badge="Exclusive"
            />

            <div className="p-4 bg-surface-50 dark:bg-surface-800/50 rounded-xl border border-surface-200 dark:border-surface-700">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center text-green-600 dark:text-green-400">
                    <DoorOpen className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-medium text-surface-900 dark:text-white">Treatment Rooms</p>
                    <p className="text-xs text-surface-500">Shared rooms for facials, waxing, etc.</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => updateField('treatmentRooms', Math.max(0, localLayout.treatmentRooms - 1))}
                    disabled={localLayout.treatmentRooms <= 0}
                    className="w-8 h-8 rounded-lg bg-white dark:bg-surface-700 border border-surface-300 dark:border-surface-600 flex items-center justify-center hover:bg-surface-100 dark:hover:bg-surface-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <Minus className="w-4 h-4" />
                  </button>
                  <span className="w-8 text-center font-semibold text-lg text-surface-900 dark:text-white">
                    {localLayout.treatmentRooms}
                  </span>
                  <button
                    onClick={() => updateField('treatmentRooms', Math.min(10, localLayout.treatmentRooms + 1))}
                    disabled={localLayout.treatmentRooms >= 10}
                    className="w-8 h-8 rounded-lg bg-white dark:bg-surface-700 border border-surface-300 dark:border-surface-600 flex items-center justify-center hover:bg-surface-100 dark:hover:bg-surface-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <span className="inline-block px-2 py-0.5 text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full">
                Shared
              </span>
            </div>

            <ToggleCard
              title="Spa Room"
              description="Dedicated room for spa treatments and massages"
              icon={<Bath className="w-5 h-5" />}
              isActive={Boolean(localLayout.spaRoom)}
              onToggle={() => updateField('spaRoom', localLayout.spaRoom ? 0 : 1)}
              badge="Exclusive"
            />
          </div>
        </div>

        {/* Preview Panel */}
        <div className="space-y-6">
          <LayoutPreview layout={localLayout} />

          {/* Summary Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-primary-50 dark:bg-primary-900/20 rounded-xl p-4 border border-primary-200 dark:border-primary-800">
              <div className="flex items-center gap-2 mb-2">
                <Users className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                <span className="text-sm font-medium text-primary-700 dark:text-primary-300">Capacity</span>
              </div>
              <p className="text-2xl font-bold text-primary-900 dark:text-primary-100">
                {localLayout.mensChairs + localLayout.womensChairs}
              </p>
              <p className="text-xs text-primary-600 dark:text-primary-400">Concurrent clients</p>
            </div>

            <div className="bg-secondary-50 dark:bg-secondary-900/20 rounded-xl p-4 border border-secondary-200 dark:border-secondary-800">
              <div className="flex items-center gap-2 mb-2">
                <DoorOpen className="w-5 h-5 text-secondary-600 dark:text-secondary-400" />
                <span className="text-sm font-medium text-secondary-700 dark:text-secondary-300">Rooms</span>
              </div>
              <p className="text-2xl font-bold text-secondary-900 dark:text-secondary-100">
                {localLayout.serviceRooms + (localLayout.bridalRoom ? 1 : 0) + localLayout.treatmentRooms + (localLayout.spaRoom ? 1 : 0)}
              </p>
              <p className="text-xs text-secondary-600 dark:text-secondary-400">Service areas</p>
            </div>
          </div>

          {/* Tips */}
          <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-4">
            <h4 className="text-sm font-semibold text-amber-800 dark:text-amber-200 mb-2">
              💡 Pro Tip
            </h4>
            <p className="text-sm text-amber-700 dark:text-amber-300">
              Having separate men's and women's sections helps with privacy and allows you to 
              optimize scheduling based on service duration patterns.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Step2Layout;
