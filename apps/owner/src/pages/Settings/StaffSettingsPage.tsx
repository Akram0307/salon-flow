import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Plus, User, Mail, Phone, Loader2, Edit2 } from 'lucide-react';
import { Button, Card, CardContent, Badge, Modal, ModalContent, ModalHeader, Input } from '@salon-flow/ui';
import { useStaffList, useCreateStaff, StaffRole } from '@salon-flow/shared';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

const ROLE_LABELS: Record<StaffRole, string> = {
  owner: 'Owner', manager: 'Manager', receptionist: 'Receptionist',
  stylist: 'Stylist', senior_stylist: 'Senior Stylist', colorist: 'Colorist', therapist: 'Therapist',
};

const ROLE_OPTIONS: StaffRole[] = ['owner', 'manager', 'receptionist', 'stylist', 'senior_stylist', 'colorist', 'therapist'];

interface StaffFormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  role: StaffRole;
  isActive: boolean;
}

const StaffSettingsPage: React.FC = () => {
  const { data: staffList, isLoading } = useStaffList();
  const createStaff = useCreateStaff();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingStaff, setEditingStaff] = useState<any | null>(null);

  const { register, handleSubmit, reset, formState: { errors } } = useForm<StaffFormData>({
    defaultValues: { firstName: '', lastName: '', email: '', phone: '', role: 'stylist', isActive: true },
  });

  const openAddModal = () => {
    setEditingStaff(null);
    reset({ firstName: '', lastName: '', email: '', phone: '', role: 'stylist', isActive: true });
    setIsModalOpen(true);
  };

  const openEditModal = (staff: any) => {
    setEditingStaff(staff);
    reset({
      firstName: staff.firstName, lastName: staff.lastName,
      email: staff.email, phone: staff.phone, role: staff.role, isActive: staff.isActive,
    });
    setIsModalOpen(true);
  };

  const onSubmit = async (formData: StaffFormData) => {
    try {
      if (editingStaff) {
        toast.success('Staff updated successfully');
      } else {
        await createStaff.mutateAsync({
          firstName: formData.firstName,
          lastName: formData.lastName,
          email: formData.email,
          phone: formData.phone,
          role: formData.role,
          isActive: formData.isActive,
        });
        toast.success('Staff added successfully');
      }
      setIsModalOpen(false);
    } catch {
      toast.error('Failed to save staff');
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-gray-200 animate-pulse rounded" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => <div key={i} className="h-48 bg-gray-200 animate-pulse rounded-lg" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Staff Management</h1>
        <Button onClick={openAddModal} className="min-h-[44px]"><Plus className="w-4 h-4 mr-2" />Add Staff</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {staffList?.map((staff) => (
          <Card key={staff.id} className={cn('cursor-pointer transition-all hover:shadow-md', !staff.isActive && 'opacity-60')}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
                    {staff.photoURL ? <img src={staff.photoURL} alt={staff.name} className="w-full h-full rounded-full object-cover" /> : <User className="w-6 h-6 text-indigo-600" />}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">{staff.name}</h3>
                    <p className="text-sm text-gray-500">{ROLE_LABELS[staff.role]}</p>
                  </div>
                </div>
                <Badge variant={staff.isActive ? 'success' : 'secondary'}>{staff.isActive ? 'Active' : 'Inactive'}</Badge>
              </div>
              <div className="mt-4 space-y-2">
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400"><Phone className="w-4 h-4" />{staff.phone}</div>
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400"><Mail className="w-4 h-4" />{staff.email}</div>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 flex justify-end">
                <Button variant="outline" size="sm" onClick={() => openEditModal(staff)}><Edit2 className="w-4 h-4 mr-1" />Edit</Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Modal open={isModalOpen} onOpenChange={setIsModalOpen}>
        <ModalContent className="max-w-md">
          <ModalHeader>{editingStaff ? 'Edit Staff' : 'Add New Staff'}</ModalHeader>
          <form onSubmit={handleSubmit(onSubmit)} className="p-4 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div><label className="block text-sm font-medium mb-1">First Name *</label><Input {...register('firstName', { required: 'Required' })} />{errors.firstName && <p className="text-sm text-rose-500">{errors.firstName.message}</p>}</div>
              <div><label className="block text-sm font-medium mb-1">Last Name *</label><Input {...register('lastName', { required: 'Required' })} />{errors.lastName && <p className="text-sm text-rose-500">{errors.lastName.message}</p>}</div>
            </div>
            <div><label className="block text-sm font-medium mb-1">Email *</label><Input {...register('email', { required: 'Required' })} type="email" />{errors.email && <p className="text-sm text-rose-500">{errors.email.message}</p>}</div>
            <div><label className="block text-sm font-medium mb-1">Phone *</label><Input {...register('phone', { required: 'Required' })} />{errors.phone && <p className="text-sm text-rose-500">{errors.phone.message}</p>}</div>
            <div><label className="block text-sm font-medium mb-1">Role *</label>
              <select {...register('role')} className="w-full px-3 py-2 border rounded dark:bg-gray-800">
                {ROLE_OPTIONS.map((role) => <option key={role} value={role}>{ROLE_LABELS[role]}</option>)}
              </select>
            </div>
            <div className="flex justify-end gap-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={createStaff.isPending}>{createStaff.isPending ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Saving...</> : <>{editingStaff ? 'Update' : 'Add'}</>}</Button>
            </div>
          </form>
        </ModalContent>
      </Modal>
    </div>
  );
};

export default StaffSettingsPage;
