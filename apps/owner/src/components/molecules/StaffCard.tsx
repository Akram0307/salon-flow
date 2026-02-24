/**
 * Salon Flow Owner PWA - StaffCard Molecule
 * Staff member card with avatar, name, role, specialization, status, rating
 */

import React from 'react';
import { Star, MapPin, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Avatar, Card } from '@/components/atoms';

// ============================================
// Types
// ============================================
export type StaffStatus = 'active' | 'inactive' | 'on_leave';

export interface Staff {
  id: string;
  name: string;
  role: string;
  avatar?: string;
  specialization?: string[];
  status: StaffStatus;
  rating?: number;
  reviewCount?: number;
  location?: string;
  email?: string;
  phone?: string;
}

export interface StaffCardProps {
  staff: Staff;
  onPress?: (staff: Staff) => void;
  className?: string;
  compact?: boolean;
}

// ============================================
// StaffCard Component
// ============================================
export const StaffCard: React.FC<StaffCardProps> = ({
  staff,
  onPress,
  className,
  compact = false,
}) => {
  const statusConfig: Record<StaffStatus, { status: string; label: string }> = {
    active: { status: 'success', label: 'Active' },
    inactive: { status: 'error', label: 'Inactive' },
    on_leave: { status: 'warning', label: 'On Leave' },
  };

  const config = statusConfig[staff.status];

  return (
    <Card
      hoverable={!!onPress}
      clickable={!!onPress}
      onClick={() => onPress?.(staff)}
      className={cn(className)}
    >
      <div className="flex items-start gap-3">
        {/* Avatar */}
        <div className="relative">
          <Avatar
            src={staff.avatar}
            alt={staff.name}
            fallback={staff.name}
            size={compact ? 'md' : 'lg'}
          />
          {/* Status Indicator */}
          <span
            className={cn(
              'absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full border-2 border-white dark:border-surface-800',
              staff.status === 'active' && 'bg-success-500',
              staff.status === 'inactive' && 'bg-error-500',
              staff.status === 'on_leave' && 'bg-warning-500'
            )}
            title={config.label}
          />
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          {/* Name */}
          <div className="flex items-center justify-between">
            <h4 className="font-semibold text-surface-900 dark:text-white truncate">
              {staff.name}
            </h4>
            {onPress && (
              <ChevronRight className="w-5 h-5 text-surface-300 dark:text-surface-600 flex-shrink-0" />
            )}
          </div>

          {/* Role */}
          <p className="text-sm text-surface-500 dark:text-surface-400 capitalize">
            {staff.role}
          </p>

          {/* Specialization */}
          {staff.specialization && staff.specialization.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {staff.specialization.slice(0, 3).map((spec, idx) => (
                <span
                  key={idx}
                  className="text-xs px-2 py-0.5 rounded-full bg-surface-100 dark:bg-surface-700 text-surface-600 dark:text-surface-400"
                >
                  {spec}
                </span>
              ))}
              {staff.specialization.length > 3 && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-surface-100 dark:bg-surface-700 text-surface-500">
                  +{staff.specialization.length - 3}
                </span>
              )}
            </div>
          )}

          {/* Rating & Location */}
          <div className="flex items-center gap-3 mt-2">
            {staff.rating && (
              <div className="flex items-center gap-1 text-sm">
                <Star className="w-4 h-4 text-warning-400 fill-warning-400" />
                <span className="font-medium text-surface-700 dark:text-surface-300">
                  {staff.rating.toFixed(1)}
                </span>
                {staff.reviewCount && (
                  <span className="text-surface-400">
                    ({staff.reviewCount})
                  </span>
                )}
              </div>
            )}
            {staff.location && (
              <div className="flex items-center gap-1 text-sm text-surface-500 dark:text-surface-400">
                <MapPin className="w-3.5 h-3.5" />
                <span className="truncate">{staff.location}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default StaffCard;
