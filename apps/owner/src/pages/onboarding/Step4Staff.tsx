/**
 * Salon Flow Owner PWA - Onboarding Step 4: Add Staff
 * Staff member management with multi-entry support
 */

import React, { useState, useEffect } from 'react';
import { Input } from '@/components/atoms/Input';
import { Button } from '@/components/atoms/Button';
import { useOnboardingStore, type StaffData } from '@/stores/onboardingStore';
import { useUIStore } from '@/stores/uiStore';
import { cn } from '@/lib/utils';
import {
  Users,
  UserPlus,
  Trash2,
  Camera,
  Phone,
  Mail,
  Percent,
  Star,
  X,
  Check,
  User,
} from 'lucide-react';

// Role definitions
const ROLES = [
  { id: 'stylist', name: 'Stylist', description: 'Hair cutting, coloring, styling', icon: '✂️' },
  { id: 'therapist', name: 'Therapist', description: 'Facials, massages, treatments', icon: '💆' },
  { id: 'receptionist', name: 'Receptionist', description: 'Front desk, bookings, billing', icon: '📞' },
  { id: 'manager', name: 'Manager', description: 'Operations, staff management', icon: '👔' },
] as const;

// Specialization options
const SPECIALIZATIONS = [
  'Hair Cutting', 'Hair Coloring', 'Hair Styling', 'Bridal Makeup',
  'Facial', 'Waxing', 'Threading', 'Manicure', 'Pedicure',
  'Massage', 'Nail Art', 'Beard Styling', 'Hair Spa',
];

// Empty staff template
const createEmptyStaff = (): StaffData => ({
  name: '',
  phone: '',
  email: '',
  role: 'stylist',
  specializations: [],
  commission: 0,
  photo: '',
});

// Staff Card Component
interface StaffCardProps {
  staff: StaffData;
  index: number;
  onUpdate: (index: number, data: Partial<StaffData>) => void;
  onRemove: (index: number) => void;
  isExpanded: boolean;
  onToggle: () => void;
}

const StaffCard: React.FC<StaffCardProps> = ({
  staff,
  index,
  onUpdate,
  onRemove,
  isExpanded,
  onToggle,
}) => {
  const [localSpecializations, setLocalSpecializations] = useState(staff.specializations);

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 2 * 1024 * 1024) {
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        onUpdate(index, { photo: reader.result as string });
      };
      reader.readAsDataURL(file);
    }
  };

  const toggleSpecialization = (spec: any) => {
    const newSpecs = (localSpecializations as any[]).includes(spec)
      ? (localSpecializations as any[]).filter((s: any) => s !== spec)
      : [...(localSpecializations as any[]), spec];
    setLocalSpecializations(newSpecs as any);
    onUpdate(index, { specializations: newSpecs as any });
  };

  const isComplete = staff.name && staff.phone && staff.role;

  return (
    <div className={cn(
      'border-2 rounded-xl overflow-hidden transition-all',
      isExpanded ? 'border-primary-500' : 'border-surface-200 dark:border-surface-700',
      !isComplete && 'border-amber-300 dark:border-amber-700'
    )}>
      {/* Header - Always visible */}
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center gap-4 bg-white dark:bg-surface-800"
      >
        {/* Avatar */}
        <div className="relative">
          {staff.photo ? (
            <img
              src={staff.photo}
              alt={staff.name}
              className="w-12 h-12 rounded-full object-cover"
            />
          ) : (
            <div className="w-12 h-12 rounded-full bg-surface-200 dark:bg-surface-700 flex items-center justify-center">
              <User className="w-6 h-6 text-surface-400" />
            </div>
          )}
          {isComplete && (
            <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-success-500 rounded-full flex items-center justify-center">
              <Check className="w-3 h-3 text-white" />
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 text-left">
          <p className="font-medium text-surface-900 dark:text-white">
            {staff.name || `Staff Member ${index + 1}`}
          </p>
          <p className="text-sm text-surface-500">
            {staff.role ? ROLES.find(r => r.id === staff.role)?.name : 'Role not set'}
            {staff.specializations.length > 0 && ` • ${staff.specializations.length} specializations`}
          </p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onRemove(index);
            }}
            className="p-2 text-surface-400 hover:text-red-500 transition-colors"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="p-4 border-t border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800/50 space-y-4">
          {/* Photo Upload */}
          <div className="flex items-center gap-4">
            <div className="relative">
              {staff.photo ? (
                <div className="relative">
                  <img
                    src={staff.photo}
                    alt="Staff"
                    className="w-20 h-20 rounded-xl object-cover"
                  />
                  <button
                    onClick={() => onUpdate(index, { photo: '' })}
                    className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ) : (
                <label className="w-20 h-20 rounded-xl border-2 border-dashed border-surface-300 dark:border-surface-600 flex flex-col items-center justify-center cursor-pointer hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all">
                  <Camera className="w-6 h-6 text-surface-400" />
                  <span className="text-xs text-surface-500 mt-1">Photo</span>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handlePhotoUpload}
                    className="hidden"
                  />
                </label>
              )}
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-surface-700 dark:text-surface-300">Profile Photo</p>
              <p className="text-xs text-surface-500">Optional • Max 2MB</p>
            </div>
          </div>

          {/* Name & Phone */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Full Name *"
              placeholder="e.g., Priya Sharma"
              value={staff.name}
              onChange={(e) => onUpdate(index, { name: e.target.value })}
              leftIcon={<User className="w-5 h-5" />}
              fullWidth
            />
            <Input
              label="Phone Number *"
              placeholder="e.g., +91 98765 43210"
              value={staff.phone}
              onChange={(e) => onUpdate(index, { phone: e.target.value })}
              leftIcon={<Phone className="w-5 h-5" />}
              fullWidth
            />
          </div>

          {/* Email */}
          <Input
            label="Email Address"
            placeholder="e.g., staff@salon.com"
            value={staff.email}
            onChange={(e) => onUpdate(index, { email: e.target.value })}
            leftIcon={<Mail className="w-5 h-5" />}
            fullWidth
          />

          {/* Role Selection */}
          <div>
            <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
              Role *
            </label>
            <div className="grid grid-cols-2 gap-3">
              {ROLES.map(role => (
                <button
                  key={role.id}
                  onClick={() => onUpdate(index, { role: role.id as StaffData['role'] })}
                  className={cn(
                    'p-3 rounded-xl border-2 text-left transition-all',
                    staff.role === role.id
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-surface-200 dark:border-surface-700 hover:border-surface-300'
                  )}
                >
                  <div className="flex items-start gap-2">
                    <span className="text-2xl">{role.icon}</span>
                    <div>
                      <p className="font-medium text-surface-900 dark:text-white text-sm">{role.name}</p>
                      <p className="text-xs text-surface-500">{role.description}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Specializations */}
          {(staff.role === 'stylist' || staff.role === 'therapist') && (
            <div>
              <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
                <span className="flex items-center gap-2">
                  <Star className="w-4 h-4" />
                  Specializations
                </span>
              </label>
              <div className="flex flex-wrap gap-2">
                {SPECIALIZATIONS.map(spec => (
                  <button
                    key={spec}
                    onClick={() => toggleSpecialization(spec)}
                    className={cn(
                      'px-3 py-1.5 rounded-full text-sm transition-all',
                      (localSpecializations as any[]).includes(spec as any)
                        ? 'bg-primary-500 text-white'
                        : 'bg-surface-200 dark:bg-surface-700 text-surface-700 dark:text-surface-300 hover:bg-surface-300'
                    )}
                  >
                    {spec}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Commission */}
          <div>
            <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
              <span className="flex items-center gap-2">
                <Percent className="w-4 h-4" />
                Commission Percentage
              </span>
            </label>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="0"
                max="50"
                value={staff.commission}
                onChange={(e) => onUpdate(index, { commission: parseInt(e.target.value) })}
                className="flex-1 h-2 bg-surface-200 dark:bg-surface-700 rounded-lg appearance-none cursor-pointer accent-primary-500"
              />
              <div className="w-20">
                <Input
                  type="number"
                  value={staff.commission}
                  onChange={(e) => onUpdate(index, { commission: Math.min(50, Math.max(0, parseInt(e.target.value) || 0)) })}
                  
                  fullWidth
                />
              </div>
            </div>
            <p className="text-xs text-surface-500 mt-1">
              Percentage of service revenue shared with staff member
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export const Step4Staff: React.FC = () => {
  const { staffMembers, setStaffMembers, addStaffMember, removeStaffMember, updateStaffMember } = useOnboardingStore();
  const { addToast } = useUIStore();
  const [expandedIndex, setExpandedIndex] = useState<number>(0);

  // Initialize with one empty staff if none exists
  useEffect(() => {
    if (staffMembers.length === 0) {
      setStaffMembers([createEmptyStaff()]);
    }
  }, [staffMembers.length, setStaffMembers]);

  const handleAddStaff = () => {
    addStaffMember(createEmptyStaff());
    setExpandedIndex(staffMembers.length);
    addToast({ message: 'New staff member added', type: 'success' });
  };

  const handleRemoveStaff = (index: number) => {
    if (staffMembers.length === 1) {
      addToast({ message: 'You need at least one staff member', type: 'warning' });
      return;
    }
    removeStaffMember(index);
    setExpandedIndex(Math.max(0, index - 1));
  };

  const completedCount = staffMembers.filter(s => s.name && s.phone && s.role).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-surface-900 dark:text-white mb-2">
          Add Your Team
        </h1>
        <p className="text-surface-600 dark:text-surface-400">
          Add your staff members and their details
        </p>
      </div>

      {/* Progress */}
      <div className="flex items-center justify-between p-4 bg-surface-50 dark:bg-surface-800/50 rounded-xl border border-surface-200 dark:border-surface-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
            <Users className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <p className="font-medium text-surface-900 dark:text-white">
              {completedCount} of {staffMembers.length} completed
            </p>
            <p className="text-sm text-surface-500">
              {staffMembers.length - completedCount} pending
            </p>
          </div>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleAddStaff}
          leftIcon={<UserPlus className="w-4 h-4" />}
        >
          Add Staff
        </Button>
      </div>

      {/* Staff List */}
      <div className="space-y-4">
        {staffMembers.map((staff, index) => (
          <StaffCard
            key={index}
            staff={staff}
            index={index}
            onUpdate={updateStaffMember}
            onRemove={handleRemoveStaff}
            isExpanded={expandedIndex === index}
            onToggle={() => setExpandedIndex(expandedIndex === index ? -1 : index)}
          />
        ))}
      </div>

      {/* Tips */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
        <h4 className="text-sm font-semibold text-blue-800 dark:text-blue-200 mb-2">
          💡 Tips for Adding Staff
        </h4>
        <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1 list-disc list-inside">
          <li>Add at least one stylist or therapist to start taking bookings</li>
          <li>Include a receptionist if you have front desk operations</li>
          <li>Set commission percentages based on your salon's policy</li>
          <li>You can always add more staff later from the dashboard</li>
        </ul>
      </div>
    </div>
  );
};

export default Step4Staff;
