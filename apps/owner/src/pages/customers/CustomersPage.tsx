import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCustomers, useDeleteCustomer } from '@salon-flow/shared';
import { 
  Card, 
  Button, 
  Input,
  Avatar,
  Table,
  EmptyState,
  Modal,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalTitle,
} from '@salon-flow/ui';
import { formatCurrency, formatDate, formatPhone } from '@salon-flow/shared';
import { 
  Plus, 
  Search,
  Download,
  Phone,
  Calendar,
  Gift,
  Star,
  Eye,
  Edit,
  Users,
} from 'lucide-react';

const CustomersPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [membershipFilter, setMembershipFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'visits' | 'spent'>('name');
  const [selectedCustomer, setSelectedCustomer] = useState<any>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const { data: customers, isLoading, error } = useCustomers({
    search: searchQuery || undefined,
  });

  const deleteCustomer = useDeleteCustomer();

  const handleDelete = async () => {
    if (!selectedCustomer) return;
    
    try {
      await deleteCustomer.mutateAsync(selectedCustomer.id);
      setShowDeleteModal(false);
      setSelectedCustomer(null);
    } catch (error) {
      console.error('Failed to delete customer:', error);
    }
  };

  const getMembershipBadge = (membership: string) => {
    const variants: Record<string, { color: string; label: string }> = {
      gold: { color: 'bg-yellow-100 text-yellow-800', label: 'Gold' },
      silver: { color: 'bg-gray-100 text-gray-800', label: 'Silver' },
      bronze: { color: 'bg-orange-100 text-orange-800', label: 'Bronze' },
      none: { color: 'bg-gray-50 text-gray-600', label: 'Regular' },
    };
    const variant = variants[membership] || variants.none;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${variant.color}`}>
        {variant.label}
      </span>
    );
  };

  const columns = [
    {
      key: 'customer',
      header: 'Customer',
      render: (customer: any) => (
        <div className="flex items-center gap-3">
          <Avatar name={customer.name} size="md" />
          <div>
            <p className="font-medium text-gray-900">{customer.name}</p>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Phone className="h-3 w-3" />
              <span>{formatPhone(customer.phone)}</span>
            </div>
          </div>
        </div>
      ),
    },
    {
      key: 'membership',
      header: 'Membership',
      render: (customer: any) => getMembershipBadge(customer.membershipTier),
    },
    {
      key: 'visits',
      header: 'Visits',
      render: (customer: any) => (
        <div className="flex items-center gap-1">
          <Calendar className="h-4 w-4 text-gray-400" />
          <span className="font-medium">{customer.total_visits || 0}</span>
        </div>
      ),
    },
    {
      key: 'spent',
      header: 'Total Spent',
      render: (customer: any) => (
        <span className="font-medium text-gray-900">
          {formatCurrency(customer.total_spent || 0)}
        </span>
      ),
    },
    {
      key: 'loyalty',
      header: 'Loyalty Points',
      render: (customer: any) => (
        <div className="flex items-center gap-1">
          <Star className="h-4 w-4 text-yellow-500" />
          <span className="font-medium">{customer.loyalty_points || 0}</span>
        </div>
      ),
    },
    {
      key: 'lastVisit',
      header: 'Last Visit',
      render: (customer: any) => (
        <span className="text-gray-500">
          {customer.lastVisit ? formatDate(customer.lastVisit) : 'Never'}
        </span>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (customer: any) => (
        <div className="flex items-center justify-end gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/customers/${customer.id}`);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/customers/${customer.id}/edit`);
            }}
          >
            <Edit className="h-4 w-4" />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Customers</h1>
          <p className="text-gray-500 mt-1">Manage your customer database</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" leftIcon={<Download className="h-4 w-4" />}>
            Export
          </Button>
          <Button onClick={() => navigate('/customers/new')} leftIcon={<Plus className="h-4 w-4" />}>
            Add Customer
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center">
              <Users className="h-5 w-5 text-primary-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{customers?.length || 0}</p>
              <p className="text-sm text-gray-500">Total</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-yellow-100 flex items-center justify-center">
              <Star className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {customers?.filter(c => c.membershipTier === 'gold').length || 0}
              </p>
              <p className="text-sm text-gray-500">Gold Members</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
              <Calendar className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {customers?.filter(c => {
                  if (!c.lastVisit) return false;
                  const lastVisit = new Date(c.lastVisit);
                  const thirtyDaysAgo = new Date();
                  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
                  return lastVisit >= thirtyDaysAgo;
                }).length || 0}
              </p>
              <p className="text-sm text-gray-500">Active (30d)</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <Gift className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {customers?.filter(c => c.birthdayMonth === new Date().getMonth() + 1).length || 0}
              </p>
              <p className="text-sm text-gray-500">Birthdays</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card padding="sm">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Search by name, phone, or email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              leftIcon={<Search className="h-4 w-4" />}
            />
          </div>
          <div className="flex gap-3">
            <select
              value={membershipFilter}
              onChange={(e) => setMembershipFilter(e.target.value)}
              className="px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Members</option>
              <option value="gold">Gold</option>
              <option value="silver">Silver</option>
              <option value="bronze">Bronze</option>
              <option value="none">Regular</option>
            </select>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="name">Sort by Name</option>
              <option value="visits">Sort by Visits</option>
              <option value="spent">Sort by Spent</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Table */}
      <Card padding="none">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading customers...</div>
        ) : error ? (
          <div className="p-8 text-center text-red-500">Failed to load customers</div>
        ) : !customers?.length ? (
          <EmptyState
            icon={<Users className="h-12 w-12" />}
            title="No customers found"
            description="Try adjusting your search or add a new customer"
            action={<Button onClick={() => navigate('/customers/new')}>Add Customer</Button>}
          />
        ) : (
          <Table
            data={customers}
            columns={columns}
            onRowClick={(customer) => navigate(`/customers/${customer.id}`)}
            keyExtractor={(customer) => customer.id}
          />
        )}
      </Card>

      {/* Delete Modal */}
      <Modal open={showDeleteModal} onOpenChange={setShowDeleteModal}>
        <ModalContent>
          <ModalHeader>
            <ModalTitle>Delete Customer</ModalTitle>
          </ModalHeader>
          <div className="py-4">
            <p className="text-gray-600">
              Are you sure you want to delete {selectedCustomer?.name}? This action cannot be undone.
            </p>
          </div>
          <ModalFooter>
            <Button variant="outline" onClick={() => setShowDeleteModal(false)}>Cancel</Button>
            <Button variant="destructive" onClick={handleDelete} isLoading={deleteCustomer.isPending}>
              Delete
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </div>
  );
};

export default CustomersPage;
