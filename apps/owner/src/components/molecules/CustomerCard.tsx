/**
 * Salon Flow Owner PWA - CustomerCard Molecule
 * Customer list item with photo/avatar, name, phone, last visit, total spent
 */

import React from 'react';
import { Phone, Calendar, Wallet, ChevronRight } from 'lucide-react';
import { cn, formatDate, formatCurrency } from '@/lib/utils';
import { Avatar, Card } from '@/components/atoms';

// ============================================
// Types
// ============================================
export interface Customer {
  id: string;
  name: string;
  phone: string;
  avatar?: string;
  lastVisit?: Date | string;
  totalSpent: number;
  visitCount?: number;
  membershipStatus?: 'active' | 'expired' | 'none';
}

export interface CustomerCardProps {
  customer: Customer;
  onPress?: (customer: Customer) => void;
  className?: string;
  compact?: boolean;
}

// ============================================
// CustomerCard Component
// ============================================
export const CustomerCard: React.FC<CustomerCardProps> = ({
  customer,
  onPress,
  className,
  compact = false,
}) => {
  const formattedLastVisit = customer.lastVisit
    ? formatDate(customer.lastVisit, { format: 'relative' })
    : 'No visits';

  const formattedTotal = formatCurrency(customer.totalSpent, { compact: true });

  return (
    <Card
      hoverable={!!onPress}
      clickable={!!onPress}
      onClick={() => onPress?.(customer)}
      className={cn(
        'flex items-center gap-3',
        customer.membershipStatus === 'active' && 'border-l-4 border-l-primary-500',
        className
      )}
    >
      {/* Avatar */}
      <Avatar
        src={customer.avatar}
        alt={customer.name}
        fallback={customer.name}
        size={compact ? 'md' : 'lg'}
      />

      {/* Info */}
      <div className="flex-1 min-w-0">
        {/* Name */}
        <div className="flex items-center gap-2">
          <h4 className="font-semibold text-surface-900 dark:text-white truncate">
            {customer.name}
          </h4>
          {customer.membershipStatus === 'active' && (
            <span className="flex-shrink-0 w-2 h-2 rounded-full bg-primary-500" title="Active Member" />
          )}
        </div>

        {/* Phone */}
        <div className="flex items-center gap-1.5 text-sm text-surface-500 dark:text-surface-400 mt-0.5">
          <Phone className="w-3.5 h-3.5" />
          <span>{customer.phone}</span>
        </div>

        {/* Meta Info */}
        <div className="flex items-center gap-3 mt-2 text-xs text-surface-400 dark:text-surface-500">
          <div className="flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5" />
            <span>Last: {formattedLastVisit}</span>
          </div>
          <div className="flex items-center gap-1">
            <Wallet className="w-3.5 h-3.5" />
            <span>{formattedTotal}</span>
          </div>
          {customer.visitCount && (
            <span>{customer.visitCount} visits</span>
          )}
        </div>
      </div>

      {/* Chevron */}
      {onPress && (
        <ChevronRight className="w-5 h-5 text-surface-300 dark:text-surface-600 flex-shrink-0" />
      )}
    </Card>
  );
};

export default CustomerCard;
