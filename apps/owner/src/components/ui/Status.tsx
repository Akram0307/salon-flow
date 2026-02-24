import React from 'react';
import { cn } from '../../lib/utils';

type StatusType = 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'canceled' | 'cancelled' | 'no_show' | 'error' | 'neutral' | 'success' | 'warning' | 'info';

interface StatusProps {
  status: StatusType;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const statusConfig: Record<StatusType, { label: string; color: string; bgColor: string }> = {
  pending: { label: 'Pending', color: 'text-yellow-700', bgColor: 'bg-yellow-100' },
  confirmed: { label: 'Confirmed', color: 'text-green-700', bgColor: 'bg-green-100' },
  in_progress: { label: 'In Progress', color: 'text-blue-700', bgColor: 'bg-blue-100' },
  completed: { label: 'Completed', color: 'text-green-700', bgColor: 'bg-green-100' },
  canceled: { label: 'Canceled', color: 'text-red-700', bgColor: 'bg-red-100' },
  cancelled: { label: 'Cancelled', color: 'text-red-700', bgColor: 'bg-red-100' },
  no_show: { label: 'No Show', color: 'text-gray-700', bgColor: 'bg-gray-100' },
  error: { label: 'Error', color: 'text-red-700', bgColor: 'bg-red-100' },
  neutral: { label: 'Neutral', color: 'text-gray-700', bgColor: 'bg-gray-100' },
  success: { label: 'Success', color: 'text-green-700', bgColor: 'bg-green-100' },
  warning: { label: 'Warning', color: 'text-yellow-700', bgColor: 'bg-yellow-100' },
  info: { label: 'Info', color: 'text-blue-700', bgColor: 'bg-blue-100' },
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base',
};

const Status: React.FC<StatusProps> = ({ status, size = 'md', className }) => {
  const config = statusConfig[status] || statusConfig.neutral;

  return (
    <span
      className={cn(
        'inline-flex items-center font-medium rounded-full',
        config.bgColor,
        config.color,
        sizeClasses[size],
        className
      )}
    >
      {config.label}
    </span>
  );
};

export default Status;
