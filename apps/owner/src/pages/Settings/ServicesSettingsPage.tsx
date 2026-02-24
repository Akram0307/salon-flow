import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Sparkles, Plus, Clock, Loader2, Edit2, Trash2 } from 'lucide-react';
import { Button, Card, CardContent, Badge, Modal, ModalContent, ModalHeader, Input } from '@salon-flow/ui';
import { useServices, useCreateService, ServiceCategory } from '@salon-flow/shared';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

const CATEGORIES: ServiceCategory[] = ['hair', 'skin', 'nails', 'makeup', 'bridal', 'spa', 'treatment'];

const CATEGORY_LABELS: Record<ServiceCategory, string> = {
  hair: 'Hair', skin: 'Skin', nails: 'Nails', makeup: 'Makeup',
  bridal: 'Bridal', spa: 'Spa', treatment: 'Treatment',
};

interface ServiceFormData {
  name: string;
  description?: string;
  category: ServiceCategory;
  price: number;
  duration: number;
  gstRate: number;
  isActive: boolean;
}

const ServicesSettingsPage: React.FC = () => {
  const { data: services, isLoading } = useServices();
  const createService = useCreateService();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingService, setEditingService] = useState<any | null>(null);
  const [activeCategory, setActiveCategory] = useState<ServiceCategory>('hair');

  const { register, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm<ServiceFormData>({
    defaultValues: { name: '', description: '', category: 'hair', price: 0, duration: 30, gstRate: 18, isActive: true },
  });

  const currentCategory = watch('category');
  const filteredServices = services?.filter((s) => s.category === activeCategory) || [];

  const openAddModal = () => {
    setEditingService(null);
    reset({ name: '', description: '', category: activeCategory, price: 0, duration: 30, gstRate: 18, isActive: true });
    setIsModalOpen(true);
  };

  const openEditModal = (service: any) => {
    setEditingService(service);
    reset({
      name: service.name, description: service.description || '',
      category: service.category, price: service.price, duration: service.duration,
      gstRate: service.gstRate || 18, isActive: service.isActive,
    });
    setIsModalOpen(true);
  };

  const onSubmit = async (formData: ServiceFormData) => {
    try {
      if (editingService) {
        toast.success('Service updated successfully');
      } else {
        await createService.mutateAsync({
          name: formData.name,
          description: formData.description,
          category: formData.category,
          price: formData.price,
          duration: formData.duration,
          gstRate: formData.gstRate,
        });
        toast.success('Service added successfully');
      }
      setIsModalOpen(false);
    } catch {
      toast.error('Failed to save service');
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-gray-200 animate-pulse rounded" />
        <div className="h-12 bg-gray-200 animate-pulse rounded" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => <div key={i} className="h-32 bg-gray-200 animate-pulse rounded-lg" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Service Catalog</h1>
        <Button onClick={openAddModal} className="min-h-[44px]"><Plus className="w-4 h-4 mr-2" />Add Service</Button>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2">
        {CATEGORIES.map((cat) => (
          <Button
            key={cat}
            variant={activeCategory === cat ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveCategory(cat)}
            className="min-h-[36px] capitalize"
          >
            {CATEGORY_LABELS[cat]}
          </Button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredServices.map((service) => (
          <Card key={service.id} className={cn('transition-all hover:shadow-md', !service.isActive && 'opacity-60')}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900 dark:text-white">{service.name}</h3>
                    <Badge variant={service.isActive ? 'success' : 'secondary'}>{service.isActive ? 'Active' : 'Inactive'}</Badge>
                  </div>
                  {service.description && <p className="text-sm text-gray-500 mt-1 line-clamp-2">{service.description}</p>}
                  <div className="flex items-center gap-4 mt-3 text-sm text-gray-600 dark:text-gray-400">
                    <span className="flex items-center gap-1"><span className="font-semibold">₹{service.price}</span></span>
                    <span className="flex items-center gap-1"><Clock className="w-4 h-4" />{service.duration} min</span>
                    <span className="text-xs">GST: {service.gstRate}%</span>
                  </div>
                </div>
                <div className="flex gap-1">
                  <Button variant="ghost" size="sm" onClick={() => openEditModal(service)}><Edit2 className="w-4 h-4" /></Button>
                  <Button variant="ghost" size="sm" className="text-rose-500"><Trash2 className="w-4 h-4" /></Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        {filteredServices.length === 0 && (
          <div className="col-span-full text-center py-12 text-gray-500">
            <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No services in this category yet.</p>
            <Button variant="outline" className="mt-4" onClick={openAddModal}>Add your first service</Button>
          </div>
        )}
      </div>

      <Modal open={isModalOpen} onOpenChange={setIsModalOpen}>
        <ModalContent className="max-w-md">
          <ModalHeader>{editingService ? 'Edit Service' : 'Add New Service'}</ModalHeader>
          <form onSubmit={handleSubmit(onSubmit)} className="p-4 space-y-4">
            <div><label className="block text-sm font-medium mb-1">Service Name *</label><Input {...register('name', { required: 'Name required' })} placeholder="e.g., Hair Cut" />{errors.name && <p className="text-sm text-rose-500">{errors.name.message}</p>}</div>
            <div><label className="block text-sm font-medium mb-1">Description</label><Input {...register('description')} placeholder="Brief description" /></div>
            <div><label className="block text-sm font-medium mb-1">Category *</label>
              <select {...register('category')} value={currentCategory} onChange={(e) => setValue('category', e.target.value as ServiceCategory)} className="w-full px-3 py-2 border rounded dark:bg-gray-800">
                {CATEGORIES.map((cat) => <option key={cat} value={cat}>{CATEGORY_LABELS[cat]}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="block text-sm font-medium mb-1">Price (₹) *</label><Input type="number" {...register('price', { required: true, valueAsNumber: true })} /></div>
              <div><label className="block text-sm font-medium mb-1">Duration (min) *</label><Input type="number" {...register('duration', { required: true, valueAsNumber: true })} /></div>
            </div>
            <div><label className="block text-sm font-medium mb-1">GST Rate (%)</label><Input type="number" {...register('gstRate', { valueAsNumber: true })} defaultValue={18} /></div>
            <div className="flex justify-end gap-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={createService.isPending}>{createService.isPending ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Saving...</> : <>{editingService ? 'Update' : 'Add'}</>}</Button>
            </div>
          </form>
        </ModalContent>
      </Modal>
    </div>
  );
};

export default ServicesSettingsPage;
