/**
 * Salon Flow Owner PWA - Onboarding Step 3: Import Services
 * Service selection from templates with customization
 */

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/atoms/Button';
import { useOnboardingStore, type ServiceTemplate } from '@/stores/onboardingStore';
import { useUIStore } from '@/stores/uiStore';
import { apiClient } from '@/services/api/client';
import { cn } from '@/lib/utils';
import {
  Scissors,
  Search,
  Check,
  Plus,
  Trash2,
  Clock,
  IndianRupee,
  Sparkles,
  Loader2,
  Package,
} from 'lucide-react';

// Service Categories
const CATEGORIES = [
  { id: 'all', name: 'All Services', icon: Package },
  { id: 'hair', name: 'Hair', icon: Scissors },
  { id: 'skin', name: 'Skin & Face', icon: Sparkles },
  { id: 'nails', name: 'Nails', icon: Package },
  { id: 'spa', name: 'Spa & Massage', icon: Package },
  { id: 'bridal', name: 'Bridal', icon: Sparkles },
  { id: 'other', name: 'Other', icon: Package },
];

// Mock service templates (will be replaced with API call)
const MOCK_SERVICE_TEMPLATES: ServiceTemplate[] = [
  // Hair Services
  { id: 'h1', name: 'Haircut - Men', category: 'hair', gender: 'male', price: 150, basePrice: 150, duration: 30, selected: false },
  { id: 'h2', name: 'Haircut - Women', category: 'hair', gender: 'female', price: 250, basePrice: 250, duration: 45, selected: false },
  { id: 'h3', name: 'Hair Wash & Blow Dry', category: 'hair', gender: 'unisex', price: 300, basePrice: 300, duration: 45, selected: false },
  { id: 'h4', name: 'Hair Coloring - Root Touch Up', category: 'hair', gender: 'unisex', price: 800, basePrice: 800, duration: 60, selected: false },
  { id: 'h5', name: 'Hair Coloring - Full', category: 'hair', gender: 'unisex', price: 1500, basePrice: 1500, duration: 120, selected: false },
  { id: 'h6', name: 'Hair Spa Treatment', category: 'hair', gender: 'unisex', price: 600, basePrice: 600, duration: 60, selected: false },
  { id: 'h7', name: 'Hair Straightening', category: 'hair', gender: 'unisex', price: 2000, basePrice: 2000, duration: 180, selected: false },
  { id: 'h8', name: 'Hair Smoothening', category: 'hair', gender: 'unisex', price: 2500, basePrice: 2500, duration: 180, selected: false },
  { id: 'h9', name: 'Beard Trim', category: 'hair', gender: 'male', price: 100, basePrice: 100, duration: 15, selected: false },
  { id: 'h10', name: 'Beard Styling', category: 'hair', gender: 'male', price: 150, basePrice: 150, duration: 20, selected: false },
  // Skin Services
  { id: 's1', name: 'Basic Facial', category: 'skin', gender: 'female', price: 500, basePrice: 500, duration: 45, selected: false },
  { id: 's2', name: 'Gold Facial', category: 'skin', gender: 'female', price: 1200, basePrice: 1200, duration: 60, selected: false },
  { id: 's3', name: 'Diamond Facial', category: 'skin', gender: 'female', price: 1500, basePrice: 1500, duration: 75, selected: false },
  { id: 's4', name: 'Cleanup', category: 'skin', gender: 'unisex', price: 350, basePrice: 350, duration: 30, selected: false },
  { id: 's5', name: 'Bleach - Face', category: 'skin', gender: 'unisex', price: 200, basePrice: 200, duration: 20, selected: false },
  { id: 's6', name: 'Bleach - Full Body', category: 'skin', gender: 'unisex', price: 800, basePrice: 800, duration: 60, selected: false },
  { id: 's7', name: 'Threading - Eyebrows', category: 'skin', gender: 'unisex', price: 50, basePrice: 50, duration: 10, selected: false },
  { id: 's8', name: 'Threading - Upper Lip', category: 'skin', gender: 'unisex', price: 30, basePrice: 30, duration: 5, selected: false },
  { id: 's9', name: 'Threading - Full Face', category: 'skin', gender: 'unisex', price: 150, basePrice: 150, duration: 20, selected: false },
  // Nail Services
  { id: 'n1', name: 'Manicure', category: 'nails', gender: 'unisex', price: 300, basePrice: 300, duration: 30, selected: false },
  { id: 'n2', name: 'Pedicure', category: 'nails', gender: 'unisex', price: 400, basePrice: 400, duration: 45, selected: false },
  { id: 'n3', name: 'Nail Polish', category: 'nails', gender: 'unisex', price: 100, basePrice: 100, duration: 15, selected: false },
  { id: 'n4', name: 'Nail Art', category: 'nails', gender: 'unisex', price: 250, basePrice: 250, duration: 30, selected: false },
  // Spa Services
  { id: 'sp1', name: 'Head Massage', category: 'spa', gender: 'unisex', price: 300, basePrice: 300, duration: 30, selected: false },
  { id: 'sp2', name: 'Full Body Massage', category: 'spa', gender: 'unisex', price: 1200, basePrice: 1200, duration: 60, selected: false },
  { id: 'sp3', name: 'Back Massage', category: 'spa', gender: 'unisex', price: 500, basePrice: 500, duration: 30, selected: false },
  // Bridal Services
  { id: 'b1', name: 'Bridal Makeup', category: 'bridal', gender: 'unisex', price: 8000, basePrice: 8000, duration: 180, selected: false },
  { id: 'b2', name: 'Bridal Package - Basic', category: 'bridal', gender: 'unisex', price: 15000, basePrice: 15000, duration: 300, selected: false },
  { id: 'b3', name: 'Bridal Package - Premium', category: 'bridal', gender: 'unisex', price: 25000, basePrice: 25000, duration: 360, selected: false },
  { id: 'b4', name: 'Mehendi', category: 'bridal', gender: 'unisex', price: 500, basePrice: 500, duration: 60, selected: false },
  { id: 'b5', name: 'Saree Draping', category: 'bridal', gender: 'unisex', price: 300, basePrice: 300, duration: 30, selected: false },
];

// Custom Service Form
interface CustomServiceFormProps {
  onAdd: (service: ServiceTemplate) => void;
  onCancel: () => void;
}

const CustomServiceForm: React.FC<CustomServiceFormProps> = ({ onAdd, onCancel }) => {
  const [name, setName] = useState('');
  const [category, setCategory] = useState('hair');
  const [price, setPrice] = useState('');
  const [duration, setDuration] = useState('30');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onAdd({
      id: `custom-${Date.now()}`,
      name,
      category,
      price: parseInt(price) || 0,
      basePrice: parseInt(price) || 0,
      duration: parseInt(duration) || 30,
      gender: 'unisex',
      selected: true,
    } as any);
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 bg-primary-50 dark:bg-primary-900/20 rounded-xl border border-primary-200 dark:border-primary-800 space-y-4">
      <h4 className="font-medium text-primary-900 dark:text-primary-100">Add Custom Service</h4>
      <div className="grid grid-cols-2 gap-3">
        <input
          type="text"
          placeholder="Service name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="col-span-2 px-3 py-2 rounded-lg border border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-800 text-sm"
          required
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="px-3 py-2 rounded-lg border border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-800 text-sm"
        >
          {CATEGORIES.filter(c => c.id !== 'all').map(c => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
        <input
          type="number"
          placeholder="Price (₹)"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          className="px-3 py-2 rounded-lg border border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-800 text-sm"
          required
          min="0"
        />
        <input
          type="number"
          placeholder="Duration (min)"
          value={duration}
          onChange={(e) => setDuration(e.target.value)}
          className="px-3 py-2 rounded-lg border border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-800 text-sm"
          required
          min="5"
          step="5"
        />
      </div>
      <div className="flex gap-2">
        <Button type="submit" size="sm" className="flex-1">Add Service</Button>
        <Button type="button" variant="ghost" size="sm" onClick={onCancel}>Cancel</Button>
      </div>
    </form>
  );
};

export const Step3Services: React.FC = () => {
  const { 
    selectedServices, 
    setSelectedServices, 
    toggleService, 
    updateServicePrice,
    availableServiceTemplates,
    setAvailableTemplates,
    isLoadingServices,
    setLoadingServices,
  } = useOnboardingStore();
  const { addToast } = useUIStore();
  
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showCustomForm, setShowCustomForm] = useState(false);
  const [editingPrice, setEditingPrice] = useState<string | null>(null);

  // Load service templates
  useEffect(() => {
    const loadTemplates = async () => {
      setLoadingServices(true);
      try {
        // Try to fetch from API first
        const response = await apiClient.get('/onboarding/service-templates');
        if (response.data && response.data.length > 0) {
          setAvailableTemplates(response.data);
        } else {
          // Fallback to mock data
          setAvailableTemplates(MOCK_SERVICE_TEMPLATES);
        }
      } catch (error) {
        // Use mock data on error
        setAvailableTemplates(MOCK_SERVICE_TEMPLATES);
      } finally {
        setLoadingServices(false);
      }
    };

    if (availableServiceTemplates.length === 0) {
      loadTemplates();
    }
  }, [availableServiceTemplates.length, setAvailableTemplates, setLoadingServices]);

  // Merge API templates with selected state
  const services = availableServiceTemplates.map(template => {
    const selected = selectedServices.find(s => s.id === template.id);
    return selected || { ...template, selected: false };
  });

  // Filter services
  const filteredServices = services.filter(service => {
    const matchesCategory = activeCategory === 'all' || service.category === activeCategory;
    const matchesSearch = service.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const selectedCount = selectedServices.filter(s => s.selected).length;
  const totalValue = selectedServices
    .filter(s => s.selected)
    .reduce((sum, s) => sum + (s.customPrice || s.price), 0);

  const handleSelectAll = () => {
    const allSelected = filteredServices.every(s => s.selected);
    const updatedServices = services.map(s => {
      if (filteredServices.find(fs => fs.id === s.id)) {
        return { ...s, selected: !allSelected };
      }
      return s;
    });
    setSelectedServices(updatedServices);
  };

  const handleAddCustom = (service: ServiceTemplate) => {
    setSelectedServices([...selectedServices, service as any]);
    setShowCustomForm(false);
    addToast({ message: 'Custom service added', type: 'success' });
  };

  const handleRemoveCustom = (id: string) => {
    setSelectedServices(selectedServices.filter(s => s.id !== id));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-surface-900 dark:text-white mb-2">
          Select Your Services
        </h1>
        <p className="text-surface-600 dark:text-surface-400">
          Choose from our templates or add your own custom services
        </p>
      </div>

      {/* Stats Bar */}
      <div className="flex items-center justify-between p-4 bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 rounded-xl border border-primary-200 dark:border-primary-800">
        <div className="flex items-center gap-6">
          <div>
            <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">{selectedCount}</p>
            <p className="text-xs text-surface-500">Services Selected</p>
          </div>
          <div className="w-px h-10 bg-surface-300 dark:bg-surface-600" />
          <div>
            <p className="text-2xl font-bold text-secondary-600 dark:text-secondary-400">₹{totalValue.toLocaleString()}</p>
            <p className="text-xs text-surface-500">Total Menu Value</p>
          </div>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleSelectAll}
          leftIcon={<Check className="w-4 h-4" />}
        >
          {filteredServices.every(s => s.selected) ? 'Deselect All' : 'Select All'}
        </Button>
      </div>

      {/* Search & Categories */}
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400" />
          <input
            type="text"
            placeholder="Search services..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-800 text-surface-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        {/* Category Pills */}
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map(category => {
            const Icon = category.icon;
            const count = services.filter(s => s.category === category.id && s.selected).length;
            return (
              <button
                key={category.id}
                onClick={() => setActiveCategory(category.id)}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all',
                  activeCategory === category.id
                    ? 'bg-primary-600 text-white'
                    : 'bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300 hover:bg-surface-200 dark:hover:bg-surface-700'
                )}
              >
                <Icon className="w-4 h-4" />
                {category.name}
                {count > 0 && (
                  <span className={cn(
                    'px-1.5 py-0.5 text-xs rounded-full',
                    activeCategory === category.id
                      ? 'bg-white/20'
                      : 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400'
                  )}>
                    {count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Services List */}
      {isLoadingServices ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
          {filteredServices.map(service => (
            <div
              key={service.id}
              className={cn(
                'flex items-center gap-4 p-4 rounded-xl border-2 transition-all cursor-pointer',
                service.selected
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-surface-200 dark:border-surface-700 bg-white dark:bg-surface-800 hover:border-surface-300 dark:hover:border-surface-600'
              )}
              onClick={() => toggleService(service.id)}
            >
              <div
                className={cn(
                  'w-6 h-6 rounded-lg border-2 flex items-center justify-center transition-colors',
                  service.selected
                    ? 'bg-primary-500 border-primary-500'
                    : 'border-surface-300 dark:border-surface-600'
                )}
              >
                {service.selected && <Check className="w-4 h-4 text-white" />}
              </div>

              <div className="flex-1">
                <p className="font-medium text-surface-900 dark:text-white">{service.name}</p>
                <div className="flex items-center gap-3 text-sm text-surface-500">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" />
                    {service.duration} min
                  </span>
                  <span className="capitalize">{service.category}</span>
                </div>
              </div>

              <div className="text-right">
                {editingPrice === service.id ? (
                  <input
                    type="number"
                    autoFocus
                    defaultValue={service.customPrice || service.price}
                    onClick={(e) => e.stopPropagation()}
                    onBlur={(e) => {
                      updateServicePrice(service.id, parseInt(e.target.value) || service.price);
                      setEditingPrice(null);
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        updateServicePrice(service.id, parseInt((e.target as HTMLInputElement).value) || service.price);
                        setEditingPrice(null);
                      }
                    }}
                    className="w-20 px-2 py-1 text-right rounded border border-primary-500 text-sm"
                  />
                ) : (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setEditingPrice(service.id);
                    }}
                    className="flex items-center gap-1 text-lg font-semibold text-surface-900 dark:text-white hover:text-primary-600"
                  >
                    <IndianRupee className="w-4 h-4" />
                    {service.customPrice || service.price}
                  </button>
                )}
                <p className="text-xs text-surface-400">Click to edit</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Custom Service Button */}
      {!showCustomForm ? (
        <Button
          variant="outline"
          onClick={() => setShowCustomForm(true)}
          leftIcon={<Plus className="w-4 h-4" />}
          fullWidth
        >
          Add Custom Service
        </Button>
      ) : (
        <CustomServiceForm
          onAdd={handleAddCustom}
          onCancel={() => setShowCustomForm(false)}
        />
      )}

      {/* Selected Services Summary */}
      {selectedCount > 0 && (
        <div className="p-4 bg-surface-50 dark:bg-surface-800/50 rounded-xl border border-surface-200 dark:border-surface-700">
          <h4 className="font-medium text-surface-900 dark:text-white mb-3">Selected Services</h4>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {selectedServices
              .filter(s => s.selected)
              .map(service => (
                <div key={service.id} className="flex items-center justify-between text-sm">
                  <span className="text-surface-700 dark:text-surface-300">{service.name}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-surface-500">₹{service.customPrice || service.price}</span>
                    {service.id.startsWith('custom-') && (
                      <button
                        onClick={() => handleRemoveCustom(service.id)}
                        className="text-red-500 hover:text-red-600"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Step3Services;
