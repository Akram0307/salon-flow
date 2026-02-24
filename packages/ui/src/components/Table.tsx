import React from 'react';
import { cn } from '../lib/utils';

// ============================================
// Table Types
// ============================================
export interface TableColumn<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  className?: string;
}

export interface TableProps<T> {
  data: T[];
  columns: TableColumn<T>[];
  onRowClick?: (item: T) => void;
  keyExtractor: (item: T) => string | number;
  className?: string;
  emptyMessage?: string;
  loading?: boolean;
}

// ============================================
// Table Components
// ============================================
export const TableHeader: React.FC<React.HTMLAttributes<HTMLTableSectionElement>> = ({
  className,
  children,
  ...props
}) => (
  <thead className={cn('bg-gray-50', className)} {...props}>
    {children}
  </thead>
);

export const TableBody: React.FC<React.HTMLAttributes<HTMLTableSectionElement>> = ({
  className,
  children,
  ...props
}) => (
  <tbody className={cn('bg-white divide-y divide-gray-200', className)} {...props}>
    {children}
  </tbody>
);

export const TableFooter: React.FC<React.HTMLAttributes<HTMLTableSectionElement>> = ({
  className,
  children,
  ...props
}) => (
  <tfoot className={cn('bg-gray-50 border-t', className)} {...props}>
    {children}
  </tfoot>
);

export const TableHead: React.FC<React.ThHTMLAttributes<HTMLTableCellElement>> = ({
  className,
  children,
  ...props
}) => (
  <th
    className={cn(
      'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      className
    )}
    {...props}
  >
    {children}
  </th>
);

export const TableRow: React.FC<React.HTMLAttributes<HTMLTableRowElement> & { onClick?: () => void }> = ({
  className,
  children,
  onClick,
  ...props
}) => (
  <tr
    className={cn(
      'hover:bg-gray-50 transition-colors',
      onClick && 'cursor-pointer',
      className
    )}
    onClick={onClick}
    {...props}
  >
    {children}
  </tr>
);

export const TableCell: React.FC<React.TdHTMLAttributes<HTMLTableCellElement>> = ({
  className,
  children,
  ...props
}) => (
  <td
    className={cn('px-6 py-4 whitespace-nowrap text-sm text-gray-900', className)}
    {...props}
  >
    {children}
  </td>
);

export const TableCaption: React.FC<React.HTMLAttributes<HTMLTableCaptionElement>> = ({
  className,
  children,
  ...props
}) => (
  <caption className={cn('text-sm text-gray-500 py-2', className)} {...props}>
    {children}
  </caption>
);

// ============================================
// Main Table Component
// ============================================
export function Table<T extends Record<string, any>>({
  data,
  columns,
  onRowClick,
  keyExtractor,
  className,
  emptyMessage = 'No data available',
  loading = false,
}: TableProps<T>): React.ReactElement {
  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-10 bg-gray-200 rounded mb-2"></div>
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 bg-gray-100 rounded mb-1"></div>
        ))}
      </div>
    );
  }

  if (data.length === 0) {
    return <EmptyState message={emptyMessage} />;
  }

  return (
    <div className={cn('overflow-x-auto', className)}>
      <table className="min-w-full divide-y divide-gray-200">
        <TableHeader>
          <TableRow>
            {columns.map((column) => (
              <TableHead key={column.key} className={column.className}>
                {column.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((item) => (
            <TableRow
              key={keyExtractor(item)}
              onClick={() => onRowClick?.(item)}
            >
              {columns.map((column) => (
                <TableCell key={column.key}>
                  {column.render ? column.render(item) : item[column.key]}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </table>
    </div>
  );
}

// ============================================
// Table Pagination
// ============================================
export interface TablePaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export const TablePagination: React.FC<TablePaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  className,
}) => (
  <div className={cn('flex items-center justify-between px-4 py-3 bg-white border-t', className)}>
    <div className="text-sm text-gray-500">
      Page {currentPage} of {totalPages}
    </div>
    <div className="flex gap-2">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage <= 1}
        className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
      >
        Previous
      </button>
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages}
        className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
      >
        Next
      </button>
    </div>
  </div>
);

// ============================================
// Empty State
// ============================================
export interface EmptyStateProps {
  message?: string;
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  message = 'No data available',
  title,
  description,
  icon,
  action,
  className,
}) => (
  <div className={cn('text-center py-8 text-gray-500', className)}>
    {icon && <div className="mb-2 flex justify-center">{icon}</div>}
    {title && <h3 className="text-lg font-medium text-gray-900 mb-1">{title}</h3>}
    {description && <p className="text-sm text-gray-500 mb-4">{description}</p>}
    {!title && !description && <p>{message}</p>}
    {action && <div className="mt-4">{action}</div>}
  </div>
);

export default Table;
