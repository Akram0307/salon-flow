/**
 * Salon Flow Owner PWA - ServiceCard Molecule
 * Service selection card with icon/image, name, duration, price, category
 */

import React from 'react';
import { Clock, Check, IndianRupee, Sparkles } from 'lucide-react';
import { cn, formatCurrency } from '@/lib/utils';
import { Card } from '@/components/atoms';

// ============================================
// Types
// ============================================
export interface Service {
  id: string;
  name: string;
  duration: number; // in minutes
  price: number;
  category: string;
  icon?: string;
  description?: string;
  imageUrl?: string;
}

export interface ServiceCardProps {
  service: Service;
  selected?: boolean;
  onSelect?: (service: Service) => void;
  className?: string;
  compact?: boolean;
}

// ============================================
// ServiceCard Component
// ============================================
export const ServiceCard: React.FC<ServiceCardProps> = ({
  service,
  selected = false,
  onSelect,
  className,
  compact = false,
}) => {
  const formatDuration = (mins: number) => {
    if (mins < 60) return `${mins}m`;
    const hours = Math.floor(mins / 60);
    const remaining = mins % 60;
    return remaining > 0 ? `${hours}h ${remaining}m` : `${hours}h`;
  };

  return (
    <Card
      hoverable={!!onSelect}
      clickable={!!onSelect}
      onClick={() => onSelect?.(service)}
      className={cn(
        'relative flex items-center gap-3',
        selected && [
          'ring-2 ring-primary-500 dark:ring-primary-400',
          'bg-primary-50 dark:bg-primary-900/10',
        ],
        className
      )}
    >
      {/* Selection Indicator */}
      {selected && (
        <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-primary-500 flex items-center justify-center">
          <Check className="w-3 h-3 text-white" />
        </div>
      )}

      {/* Icon/Image */}
      <div
        className={cn(
          'flex-shrink-0 rounded-xl flex items-center justify-center',
          'bg-gradient-to-br from-primary-100 to-primary-50',
          'dark:from-primary-900/30 dark:to-primary-800/20',
          'text-primary-600 dark:text-primary-400',
          compact ? 'w-12 h-12' : 'w-14 h-14'
        )}
      >
        {service.imageUrl ? (
          <img
            src={service.imageUrl}
            alt={service.name}
            className="w-full h-full object-cover rounded-xl"
          />
        ) : service.icon ? (
          <span className="text-2xl">{service.icon}</span>
        ) : (
          <Sparkles className={cn(compact ? 'w-6 h-6' : 'w-7 h-7')} />
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        {/* Category */}
        <p className="text-xs text-surface-400 dark:text-surface-500 uppercase tracking-wide">
          {service.category}
        </p>

        {/* Name */}
        <h4 className="font-semibold text-surface-900 dark:text-white truncate mt-0.5">
          {service.name}
        </h4>

        {/* Duration & Price */}
        <div className="flex items-center gap-3 mt-1">
          <div className="flex items-center gap-1 text-sm text-surface-500 dark:text-surface-400">
            <Clock className="w-3.5 h-3.5" />
            <span>{formatDuration(service.duration)}</span>
          </div>
          <div className="flex items-center gap-0.5 text-sm font-medium text-surface-700 dark:text-surface-300">
            <IndianRupee className="w-3.5 h-3.5" />
            <span>{formatCurrency(service.price, { showSymbol: false })}</span>
          </div>
        </div>

        {/* Description */}
        {service.description && !compact && (
          <p className="text-xs text-surface-400 dark:text-surface-500 mt-1 line-clamp-1">
            {service.description}
          </p>
        )}
      </div>
    </Card>
  );
};

export default ServiceCard;
