/**
 * Salon Flow Owner PWA - SearchBar Molecule
 * Search input with icon, clear button, and optional filters
 * Mobile-optimized with large touch targets (min 44px)
 */

import React, { forwardRef } from 'react';
import { Search, X, SlidersHorizontal } from 'lucide-react';
import { cn } from '@/lib/utils';

// ============================================
// Types
// ============================================
export interface FilterOption {
  value: string;
  label: string;
}

export interface SearchBarProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange' | 'size'> {
  value: string;
  onChange: (value: string) => void;
  onClear?: () => void;
  placeholder?: string;
  filters?: FilterOption[];
  activeFilter?: string;
  onFilterChange?: (filter: string) => void;
  showFilters?: boolean;
  loading?: boolean;
}

// ============================================
// SearchBar Component
// ============================================
export const SearchBar = forwardRef<HTMLInputElement, SearchBarProps>(
  (
    {
      value,
      onChange,
      onClear,
      placeholder = 'Search...',
      filters,
      activeFilter,
      onFilterChange,
      showFilters = false,
      loading = false,
      className,
      ...props
    },
    ref
  ) => {
    const hasValue = value.length > 0;
    const hasFilters = filters && filters.length > 0;

    return (
      <div className={cn('w-full space-y-2', className)}>
        {/* Search Input Container */}
        <div className="relative flex items-center">
          {/* Search Icon */}
          <div className="absolute left-3 pointer-events-none">
            <Search className="w-5 h-5 text-surface-400 dark:text-surface-500" />
          </div>

          {/* Input */}
          <input
            ref={ref}
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            className={cn(
              // Base styles
              'w-full rounded-xl',
              'bg-surface-100 dark:bg-surface-800/50',
              'border-0',
              'text-surface-900 dark:text-surface-100',
              'placeholder:text-surface-400 dark:placeholder:text-surface-500',
              'focus:outline-none focus:ring-2 focus:ring-primary-500/30',
              'transition-all duration-200',
              // Size with left padding for icon and right for clear button
              'pl-10 pr-10 py-3 text-base',
              // Mobile touch target
              'min-h-[48px]'
            )}
            {...props}
          />

          {/* Loading Spinner or Clear Button */}
          <div className="absolute right-3">
            {loading ? (
              <div className="w-5 h-5 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
            ) : hasValue ? (
              <button
                type="button"
                onClick={onClear}
                className={cn(
                  'p-1 rounded-full',
                  'hover:bg-surface-200 dark:hover:bg-surface-700',
                  'text-surface-400 dark:text-surface-500',
                  'hover:text-surface-600 dark:hover:text-surface-300',
                  'transition-colors duration-200',
                  // Touch target
                  'min-w-[28px] min-h-[28px] flex items-center justify-center'
                )}
                aria-label="Clear search"
              >
                <X className="w-4 h-4" />
              </button>
            ) : null}
          </div>
        </div>

        {/* Filters */}
        {showFilters && hasFilters && (
          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-hide">
            {/* Filter Icon */}
            <div className="flex-shrink-0 p-2 text-surface-400 dark:text-surface-500">
              <SlidersHorizontal className="w-4 h-4" />
            </div>

            {/* Filter Pills */}
            {filters.map((filter) => {
              const isActive = activeFilter === filter.value;
              return (
                <button
                  key={filter.value}
                  type="button"
                  onClick={() => onFilterChange?.(filter.value)}
                  className={cn(
                    'flex-shrink-0 px-3 py-1.5 rounded-full text-sm font-medium',
                    'transition-all duration-200',
                    'min-h-[36px] flex items-center',
                    isActive
                      ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                      : 'bg-surface-100 dark:bg-surface-800 text-surface-600 dark:text-surface-400 hover:bg-surface-200 dark:hover:bg-surface-700'
                  )}
                >
                  {filter.label}
                </button>
              );
            })}
          </div>
        )}
      </div>
    );
  }
);

SearchBar.displayName = 'SearchBar';

export default SearchBar;
