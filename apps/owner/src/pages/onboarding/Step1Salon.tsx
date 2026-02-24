/**
 * Salon Flow Owner PWA - Onboarding Step 1: Create Salon
 * Basic salon information collection
 */

import React, { useState, useCallback, useEffect } from 'react';
import { Input } from '@/components/atoms/Input';
import { useOnboardingStore } from '@/stores/onboardingStore';
import { useUIStore } from '@/stores/uiStore';
import { Building2, MapPin, Phone, FileText, Image as ImageIcon } from 'lucide-react';

interface AddressFieldProps {
  label: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
  icon?: React.ReactNode;
  required?: boolean;
}

const AddressField: React.FC<AddressFieldProps> = ({
  label,
  placeholder,
  value,
  onChange,
  icon,
  required = false,
}) => (
  <div className="space-y-1">
    <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">
      {label}
      {required && <span className="text-red-500 ml-1">*</span>}
    </label>
    <div className="relative">
      {icon && (
        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400">
          {icon}
        </div>
      )}
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className={`w-full px-4 py-2.5 rounded-lg border border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-800 text-surface-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all ${icon ? 'pl-10' : ''}`}
      />
    </div>
  </div>
);

export const Step1Salon: React.FC = () => {
  const { salonData, setSalonData } = useOnboardingStore();
  const { addToast } = useUIStore();
  const [logoPreview, setLogoPreview] = useState<string | null>(salonData.logo || null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleLogoUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 2 * 1024 * 1024) {
      addToast({ message: 'Logo must be less than 2MB', type: 'warning' });
      return;
    }

    if (!file.type.startsWith('image/')) {
      addToast({ message: 'Please upload an image file', type: 'warning' });
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      const result = reader.result as string;
      setLogoPreview(result);
      setSalonData({ logo: result });
    };
    reader.readAsDataURL(file);
  }, [setSalonData, addToast]);

  const validate = useCallback(() => {
    const newErrors: Record<string, string> = {};
    if (!salonData.name?.trim()) newErrors.name = 'Salon name is required';
    if (!salonData.address?.street?.trim()) newErrors.street = 'Street address is required';
    if (!salonData.address?.city?.trim()) newErrors.city = 'City is required';
    if (!salonData.address?.state?.trim()) newErrors.state = 'State is required';
    if (!salonData.address?.pincode?.trim()) newErrors.pincode = 'Pincode is required';
    if (!salonData.phone?.trim()) newErrors.phone = 'Phone number is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [salonData]);

  useEffect(() => {
    validate();
  }, [salonData, validate]);

  const isComplete = salonData.name && salonData.address?.street && salonData.phone;

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
          <Building2 className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-surface-900 dark:text-white mb-2">
          Create Your Salon
        </h1>
        <p className="text-surface-600 dark:text-surface-400">
          Let's start with the basics about your business
        </p>
      </div>

      <div className="space-y-6">
        <Input
          label="Salon Name *"
          placeholder="e.g., Jawed Habib Hair & Beauty Salon"
          value={salonData.name || ''}
          onChange={(e) => setSalonData({ name: e.target.value })}
          leftIcon={<Building2 className="w-5 h-5" />}
          error={errors.name}
          fullWidth
        />

        <div className="space-y-4">
          <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">
            Address
          </label>
          <div className="grid grid-cols-1 gap-4">
            <AddressField
              label="Street Address *"
              placeholder="123 Main Street, Building Name"
              value={salonData.address?.street || ''}
              onChange={(value) => setSalonData({
                address: { street: value } as any,
              })}
              icon={<MapPin className="w-5 h-5" />}
              required
            />
            <div className="grid grid-cols-2 gap-4">
              <AddressField
                label="City *"
                placeholder="e.g., Kurnool"
                value={salonData.address?.city || ''}
                onChange={(value) => setSalonData({
                  address: { ...salonData?.address, city: value } as any,
                })}
                required
              />
              <AddressField
                label="State *"
                placeholder="e.g., Andhra Pradesh"
                value={salonData.address?.state || ''}
                onChange={(value) => setSalonData({
                  address: { ...salonData?.address, state: value } as any,
                })}
                required
              />
            </div>
            <AddressField
              label="Pincode *"
              placeholder="e.g., 518001"
              value={salonData.address?.pincode || ''}
              onChange={(value) => setSalonData({
                address: { street: salonData?.address?.street || '', city: salonData?.address?.city || '', state: salonData?.address?.state || '', pincode: value } as any,
              })}
              required
            />
          </div>
        </div>

        <Input
          label="Phone Number *"
          placeholder="+91 98765 43210"
          value={salonData.phone || ''}
          onChange={(e) => setSalonData({ phone: e.target.value })}
          leftIcon={<Phone className="w-5 h-5" />}
          error={errors.phone}
          fullWidth
        />

        <Input
          label="GST Number (Optional)"
          placeholder="e.g., 29ABCDE1234F1Z5"
          value={salonData.gstNumber || ''}
          onChange={(e) => setSalonData({ gstNumber: e.target.value })}
          leftIcon={<FileText className="w-5 h-5" />}
          helperText="Required only if you want GST invoices"
          fullWidth
        />

        <div>
          <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
            Salon Logo (Optional)
          </label>
          <div className="flex items-center gap-4">
            <div className="relative w-24 h-24 rounded-xl border-2 border-dashed border-surface-300 dark:border-surface-600 flex items-center justify-center overflow-hidden bg-surface-50 dark:bg-surface-800/50">
              {logoPreview ? (
                <img
                  src={logoPreview}
                  alt="Logo preview"
                  className="w-full h-full object-cover"
                />
              ) : (
                <ImageIcon className="w-8 h-8 text-surface-400" />
              )}
              <input
                type="file"
                accept="image/*"
                onChange={handleLogoUpload}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
            </div>
            <div className="flex-1">
              <p className="text-sm text-surface-600 dark:text-surface-400">
                Upload your salon logo
              </p>
              <p className="text-xs text-surface-400">
                Recommended: Square image, max 2MB
              </p>
            </div>
          </div>
        </div>
      </div>

      {isComplete && (
        <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl">
          <p className="text-sm text-green-700 dark:text-green-300">
            ✓ All required fields completed
          </p>
        </div>
      )}
    </div>
  );
};

export default Step1Salon;
