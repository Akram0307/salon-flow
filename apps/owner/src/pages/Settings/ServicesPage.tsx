import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Plus, Search, Edit, Trash2, Clock, DollarSign } from 'lucide-react';
import { useServices, useCreateService, useUpdateService, useDeleteService, Service, ServiceCategory } from '@salon-flow/shared';
import { Button, Card, CardContent, Input, Modal, ModalContent, ModalHeader, ModalFooter, Badge } from '@salon-flow/ui';

const categoryOptions: { value: ServiceCategory; label: string }[] = [
  { value: 'hair', label: 'Hair' },
  { value: 'skin', label: 'Skin' },
  { value: 'nails', label: 'Nails' },
  { value: 'makeup', label: 'Makeup' },
  { value: 'bridal', label: 'Bridal' },
  { value: 'spa', label: 'Spa' },
  { value: 'treatment', label: 'Treatment' },
];

interface ServiceFormData {
  name: string;
  description: string;
  category: ServiceCategory;
  duration: number;
  price: number;
  gstRate: number;
}

const ServicesPage: React.FC = () => {
    const { data: services, isLoading } = useServices();
  const createService = useCreateService();
  const updateService = useUpdateService();
  const deleteService = useDeleteService();

  const [searchQuery, setSearchQuery] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingService, setEditingService] = useState<Service | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ServiceFormData>({
    defaultValues: {
      name: '',
      description: '',
      category: 'hair',
      duration: 30,
      price: 0,
      gstRate: 5,
    },
  });

  const filteredServices = (services || []).filter((s: Service) =>
    s.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const openModal = (service?: Service) => {
    if (service) {
      setEditingService(service);
      reset({
        name: service.name,
        description: service.description || '',
        category: service.category,
        duration: service.duration,
        price: service.price,
        gstRate: service.gstRate,
      });
    } else {
      setEditingService(null);
      reset({
        name: '',
        description: '',
        category: 'hair',
        duration: 30,
        price: 0,
        gstRate: 5,
      });
    }
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingService(null);
  };

  const onSubmit = async (data: ServiceFormData) => {
    try {
      if (editingService) {
        await updateService.mutateAsync({
          id: editingService.id,
          data: {
            name: data.name,
            description: data.description,
            category: data.category,
            duration: data.duration,
            price: data.price,
            gstRate: data.gstRate,
          },
        });
      } else {
        await createService.mutateAsync({
          name: data.name,
          description: data.description,
          category: data.category,
          duration: data.duration,
          price: data.price,
          gstRate: data.gstRate,
        });
      }
      closeModal();
    } catch (error) {
      console.error('Failed to save service:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this service?')) {
      await deleteService.mutateAsync(id);
    }
  };

  const getCategoryBadgeVariant = (category: ServiceCategory) => {
    const variants: Record<ServiceCategory, 'default' | 'secondary' | 'success' | 'warning' | 'outline'> = {
      hair: 'default',
      skin: 'success',
      nails: 'secondary',
      makeup: 'warning',
      bridal: 'outline',
      spa: 'success',
      treatment: 'secondary',
    };
    return variants[category] || 'outline';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Services</h1>
        <Button onClick={() => openModal()}>
          <Plus className="w-4 h-4 mr-2" />
          Add Service
        </Button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <Input
          placeholder="Search services..."
          className="pl-10"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredServices.map((service: Service) => (
          <Card key={service.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{service.name}</h3>
                  <Badge variant={getCategoryBadgeVariant(service.category)} className="mt-1">
                    {service.category}
                  </Badge>
                </div>
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => openModal(service)}
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(service.id)}
                  >
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </Button>
                </div>
              </div>
              {service.description && (
                <p className="text-sm text-gray-500 mt-2">{service.description}</p>
              )}
              <div className="flex items-center gap-4 mt-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>{service.duration} min</span>
                </div>
                <div className="flex items-center gap-1">
                  <DollarSign className="w-4 h-4" />
                  <span>Rs.{service.price}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredServices.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No services found</p>
        </div>
      )}

      {/* Add/Edit Modal */}
      <Modal open={isModalOpen} onOpenChange={setIsModalOpen}>
        <ModalContent>
          <ModalHeader>
            {editingService ? 'Edit Service' : 'Add Service'}
          </ModalHeader>
          <div className="p-4">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <Input
                  {...register('name', { required: 'Name is required' })}
                  error={errors.name?.message}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <Input
                  {...register('description')}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  {...register('category')}
                >
                  {categoryOptions.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Duration (min)</label>
                  <Input
                    type="number"
                    {...register('duration', { valueAsNumber: true })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Price (Rs.)</label>
                  <Input
                    type="number"
                    {...register('price', { valueAsNumber: true })}
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">GST Rate (%)</label>
                <Input
                  type="number"
                  {...register('gstRate', { valueAsNumber: true })}
                />
              </div>
            </form>
          </div>
          <ModalFooter>
            <Button variant="outline" onClick={closeModal}>Cancel</Button>
            <Button onClick={handleSubmit(onSubmit)}>
              {editingService ? 'Update' : 'Create'}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </div>
  );
};

export default ServicesPage;
