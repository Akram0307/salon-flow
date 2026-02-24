/**
 * Salon Flow Owner PWA - Onboarding Store
 * Manages multi-step onboarding wizard state
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { apiClient } from '@/services/api/client';

// Type definitions
export interface Address {
  street: string;
  city: string;
  state: string;
  pincode: string;
  country: string;
  area?: string;
}

export interface SalonData {
  name: string;
  address: Address;
  phone: string;
  email?: string;
  gstNumber?: string;
  logo?: string;
}

export interface LayoutData {
  mensChairs: number;
  womensChairs: number;
  serviceRooms: number;
  bridalRoom: number;
  treatmentRooms: number;
  spaRoom: number;
}

export interface ServiceTemplate {
  selected?: boolean;
  id: string;
  name: string;
  category: string;
  description?: string;
  basePrice: number;
  price: number;
  duration: number;
  gender: 'male' | 'female' | 'unisex';
}

export interface SelectedService extends ServiceTemplate {
  selected: boolean;
  customPrice?: number;
}

export interface Specialization {
  id: string;
  name: string;
}

export interface StaffData {
  id?: string;
  name: string;
  phone: string;
  email?: string;
  role: 'stylist' | 'therapist' | 'receptionist';
  specializations: Specialization[];
  commission: number;
  photo?: string;
}

export interface BreakTime {
  start: string;
  end: string;
}

export interface DayHours {
  isOpen: boolean;
  isClosed?: boolean;
  open: string;
  close: string;
  breaks: BreakTime[];
}

export interface BusinessHoursData {
  [key: string]: DayHours;
}

// Validation helpers
const isStepValid = (step: number, state: OnboardingState): boolean => {
  switch (step) {
    case 1:
      return !!state.salonData?.name?.trim() && 
             !!state.salonData?.address?.street?.trim() && 
             !!state.salonData?.phone?.trim();
    case 2:
      return (state.layoutData?.mensChairs ?? 0) >= 0 && 
             (state.layoutData?.womensChairs ?? 0) >= 0;
    case 3:
      return state.selectedServices.some((s: SelectedService) => s.selected);
    case 4:
      return state.staffMembers.length > 0;
    case 5:
      return Object.keys(state.businessHours || {}).length > 0;
    default:
      return false;
  }
};

interface OnboardingState {
  // Navigation
  currentStep: number;
  totalSteps: number;
  completedSteps: number[];
  isCompleted: boolean;
  isSubmitting: boolean;
  submitError: string | null;

  // Form data
  salonData: Partial<SalonData>;
  layoutData: Partial<LayoutData>;
  selectedServices: SelectedService[];
  staffMembers: StaffData[];
  businessHours: Partial<BusinessHoursData>;
  
  // Service templates
  availableServiceTemplates: ServiceTemplate[];
  selectedCategories: string[];
  
  // Loading states
  isLoadingServices: boolean;
}

interface OnboardingActions {
  // Navigation
  setCurrentStep: (step: number) => void;
  nextStep: () => void;
  previousStep: () => void;
  markStepComplete: (step: number) => void;
  canProceed: (step: number) => boolean;
  isStepValid: (step: number) => boolean;
  
  // Data setters
  setSalonData: (data: Partial<SalonData>) => void;
  setLayoutData: (data: Partial<LayoutData>) => void;
  setSelectedServices: (services: SelectedService[]) => void;
  setStaffMembers: (staff: StaffData[]) => void;
  setBusinessHours: (hours: Partial<BusinessHoursData>) => void;
  
  // Service management
  setAvailableTemplates: (templates: ServiceTemplate[]) => void;
  toggleService: (serviceId: string) => void;
  updateServicePrice: (serviceId: string, price: number) => void;
  updateServiceDuration: (serviceId: string, duration: number) => void;
  
  // Staff management
  addStaffMember: (staff: StaffData) => void;
  updateStaffMember: (index: number, staff: Partial<StaffData>) => void;
  removeStaffMember: (index: number) => void;
  
  // Business hours
  updateDayHours: (day: string, hours: Partial<DayHours>) => void;
  
  // API actions
  fetchServiceTemplates: () => Promise<void>;
  completeOnboarding: () => Promise<boolean>;
  saveProgress: () => void;
  setSubmitting: (submitting: boolean) => void;
  setSubmitError: (error: string | null) => void;
  setLoadingServices: (loading: boolean) => void;
  reset: () => void;
}

const initialState: OnboardingState = {
  currentStep: 1,
  totalSteps: 5,
  completedSteps: [],
  isCompleted: false,
  isSubmitting: false,
  submitError: null,
  salonData: {},
  layoutData: {
    mensChairs: 6,
    womensChairs: 4,
    serviceRooms: 4,
    bridalRoom: 1,
    treatmentRooms: 2,
    spaRoom: 1,
  },
  selectedServices: [],
  staffMembers: [],
  businessHours: {},
  availableServiceTemplates: [],
  selectedCategories: [],
  isLoadingServices: false,
};

export const useOnboardingStore = create<OnboardingState & OnboardingActions>()(
  persist(
    (set, get) => ({
      ...initialState,

      // Navigation
      setCurrentStep: (step) => set({ currentStep: step }),
      
      nextStep: () => {
        const { currentStep, totalSteps, completedSteps } = get();
        if (currentStep < totalSteps) {
          set({ 
            currentStep: currentStep + 1,
            completedSteps: [...new Set([...completedSteps, currentStep])],
          });
        }
      },
      
      previousStep: () => {
        const { currentStep } = get();
        if (currentStep > 1) {
          set({ currentStep: currentStep - 1 });
        }
      },
      
      markStepComplete: (step) => set((state) => ({
        completedSteps: [...new Set([...state.completedSteps, step])],
      })),

      canProceed: (step) => {
        const state = get();
        return isStepValid(step, state);
      },

      isStepValid: (step) => {
        const state = get();
        return isStepValid(step, state);
      },

      // Data setters
      setSalonData: (data) => set((state) => ({ 
        salonData: { ...state.salonData, ...data } 
      })),
      
      setLayoutData: (data) => set((state) => ({ 
        layoutData: { ...state.layoutData, ...data } 
      })),
      
      setSelectedServices: (services) => set({ selectedServices: services }),
      
      setStaffMembers: (staff) => set({ staffMembers: staff }),
      
      setBusinessHours: (hours) => set((state) => ({ 
        businessHours: { ...state.businessHours, ...hours } 
      })),

      // Service management
      setAvailableTemplates: (templates) => set({ availableServiceTemplates: templates }),
      
      toggleService: (serviceId) => set((state) => ({
        selectedServices: state.selectedServices.map((s) =>
          s.id === serviceId ? { ...s, selected: !s.selected } : s
        ),
      })),
      
      updateServicePrice: (serviceId, price) => set((state) => ({
        selectedServices: state.selectedServices.map((s) =>
          s.id === serviceId ? { ...s, price } : s
        ),
      })),
      
      updateServiceDuration: (serviceId, duration) => set((state) => ({
        selectedServices: state.selectedServices.map((s) =>
          s.id === serviceId ? { ...s, duration } : s
        ),
      })),

      // Staff management
      addStaffMember: (staff) => set((state) => ({
        staffMembers: [...state.staffMembers, staff],
      })),
      
      updateStaffMember: (index, data) => set((state) => ({
        staffMembers: state.staffMembers.map((s, i) =>
          i === index ? { ...s, ...data } : s
        ),
      })),
      
      removeStaffMember: (index) => set((state) => ({
        staffMembers: state.staffMembers.filter((_, i) => i !== index),
      })),

      // Business hours
      updateDayHours: (day, hours) => set((state) => ({
        businessHours: {
          ...state.businessHours,
          [day]: { ...state.businessHours[day], ...hours } as any,
        } as any,
      })),

      // API actions
      fetchServiceTemplates: async () => {
        set({ isLoadingServices: true });
        try {
          const response = await apiClient.get('/onboarding/service-templates');
          const templates = response.data.templates || response.data || [];
          
          // Convert to selected services format
          const selectedServices: SelectedService[] = templates.map((t: ServiceTemplate) => ({
            ...t,
            selected: false,
            price: t.basePrice || t.price || 0,
            duration: t.duration || 30,
          }));
          
          set({ 
            availableServiceTemplates: templates,
            selectedServices,
            isLoadingServices: false 
          });
        } catch (error) {
          set({ 
            submitError: error instanceof Error ? error.message : 'Failed to fetch service templates',
            isLoadingServices: false 
          });
        }
      },

      completeOnboarding: async () => {
        const state = get();
        set({ isSubmitting: true, submitError: null });
        
        try {
          // Filter selected services
          const servicesToSubmit = state.selectedServices
            .filter((s) => s.selected)
            .map((s) => ({
              name: s.name,
              category: s.category,
              price: s.price,
              duration: s.duration,
              description: s.description,
            }));
          
          // Submit salon data
          const salonResponse = await apiClient.post('/tenants', {
            name: state.salonData.name,
            address: state.salonData.address,
            phone: state.salonData.phone,
            gstNumber: state.salonData.gstNumber,
            logo: state.salonData.logo,
            layout: state.layoutData,
          });
          
          const tenantId = salonResponse.data.id;
          
          // Submit services
          if (servicesToSubmit.length > 0) {
            await apiClient.post('/services/bulk', {
              tenantId,
              services: servicesToSubmit,
            });
          }
          
          // Submit staff
          if (state.staffMembers.length > 0) {
            await apiClient.post('/staff/bulk', {
              tenantId,
              staff: state.staffMembers,
            });
          }
          
          // Submit business hours
          await apiClient.post(`/tenants/${tenantId}/business-hours`, {
            hours: state.businessHours,
          });
          
          set({ 
            isCompleted: true, 
            isSubmitting: false,
            completedSteps: [1, 2, 3, 4, 5],
          });
          
          return true;
        } catch (error) {
          set({ 
            submitError: error instanceof Error ? error.message : 'Failed to complete onboarding',
            isSubmitting: false 
          });
          return false;
        }
      },

      saveProgress: () => {
        // Progress is automatically saved via persist middleware
      },

      setSubmitting: (submitting) => set({ isSubmitting: submitting }),
      
      setSubmitError: (error) => set({ submitError: error }),
      
      setLoadingServices: (loading) => set({ isLoadingServices: loading }),

      reset: () => set(initialState),
    }),
    {
      name: 'salon-flow-onboarding',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        currentStep: state.currentStep,
        completedSteps: state.completedSteps,
        salonData: state.salonData,
        layoutData: state.layoutData,
        selectedServices: state.selectedServices,
        staffMembers: state.staffMembers,
        businessHours: state.businessHours,
        selectedCategories: state.selectedCategories,
      }),
    }
  )
);

export default useOnboardingStore;
