/**
 * Salon Flow Owner PWA - Onboarding Complete
 * Success page with summary and auto-redirect
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/atoms/Button';
import { useOnboardingStore } from '@/stores/onboardingStore';
import { useUIStore } from '@/stores/uiStore';
import { apiClient } from '@/services/api/client';
import {
  CheckCircle,
  Building2,
  Users,
  Scissors,
  Clock,
  ArrowRight,
  Sparkles,
  Loader2,
} from 'lucide-react';

// Summary Item Component
interface SummaryItemProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  subValue?: string;
}

const SummaryItem: React.FC<SummaryItemProps> = ({ icon, label, value, subValue }) => (
  <div className="flex items-start gap-3 p-3 bg-surface-50 dark:bg-surface-800/50 rounded-lg">
    <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center text-primary-600 dark:text-primary-400 flex-shrink-0">
      {icon}
    </div>
    <div className="flex-1 min-w-0">
      <p className="text-sm text-surface-500">{label}</p>
      <p className="font-medium text-surface-900 dark:text-white truncate">{value}</p>
      {subValue && <p className="text-xs text-surface-400">{subValue}</p>}
    </div>
  </div>
);

export const Complete: React.FC = () => {
  const navigate = useNavigate();
  const { 
    salonData, 
    layoutData, 
    selectedServices, 
    staffMembers, 
    businessHours,
    completeOnboarding,
    isSubmitting,
    setSubmitting,
    setSubmitError,
    submitError,
  } = useOnboardingStore();
  const { addToast } = useUIStore();
  
  const [countdown, setCountdown] = useState(5);
  const [isSubmitted, setIsSubmitted] = useState(false);

  // Submit data to API
  useEffect(() => {
    const submitOnboarding = async () => {
      if (isSubmitted) return;
      
      setSubmitting(true);
      try {
        // Create tenant/salon
        const tenantResponse = await apiClient.post('/tenants', {
          name: salonData.name,
          address: salonData.address,
          phone: salonData.phone,
          email: salonData.email,
          gst_number: salonData.gstNumber,
          logo: salonData.logo,
          layout: layoutData,
          business_hours: businessHours,
        });

        const tenantId = tenantResponse.data.id;

        // Create services
        const servicesToCreate = selectedServices
          .filter(s => s.selected)
          .map(s => ({
            name: s.name,
            category: s.category,
            price: s.customPrice || s.price,
            duration: s.duration,
            tenant_id: tenantId,
          }));

        if (servicesToCreate.length > 0) {
          await apiClient.post('/services/bulk', { services: servicesToCreate });
        }

        // Create staff
        for (const staff of staffMembers) {
          await apiClient.post('/staff', {
            ...staff,
            tenant_id: tenantId,
          });
        }

        completeOnboarding();
        setIsSubmitted(true);
        addToast({ message: 'Salon setup completed successfully!', type: 'success' });
      } catch (error) {
        console.error('Onboarding submission error:', error);
        setSubmitError('Failed to complete setup. Please try again.');
        addToast({ message: 'Failed to complete setup', type: 'error' });
      } finally {
        setSubmitting(false);
      }
    };

    submitOnboarding();
  }, [isSubmitted]);

  // Auto-redirect countdown
  useEffect(() => {
    if (!isSubmitted || submitError) return;

    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          navigate('/dashboard');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isSubmitted, submitError, navigate]);

  const handleGoToDashboard = () => {
    navigate('/dashboard');
  };

  // Calculate summary stats
  const selectedServicesCount = selectedServices.filter(s => s.selected).length;
  const openDays = Object.values(businessHours).filter(h => !h?.isClosed).length;

  if (isSubmitting) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-surface-900 dark:via-surface-900 dark:to-surface-800 flex items-center justify-center">
        <div className="text-center">
          <div className="w-20 h-20 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
            <Loader2 className="w-10 h-10 text-primary-600 animate-spin" />
          </div>
          <h2 className="text-2xl font-bold text-surface-900 dark:text-white mb-2">
            Setting up your salon...
          </h2>
          <p className="text-surface-600 dark:text-surface-400">
            This may take a few moments
          </p>
        </div>
      </div>
    );
  }

  if (submitError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-red-50 dark:from-red-900/20 dark:via-surface-900 dark:to-red-900/20 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white dark:bg-surface-800 rounded-2xl shadow-xl p-8 text-center">
          <div className="w-20 h-20 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-4xl">⚠️</span>
          </div>
          <h2 className="text-2xl font-bold text-surface-900 dark:text-white mb-2">
            Setup Failed
          </h2>
          <p className="text-surface-600 dark:text-surface-400 mb-6">
            {submitError}
          </p>
          <Button onClick={() => window.location.reload()} fullWidth>
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-surface-900 dark:via-surface-900 dark:to-surface-800 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Success Animation */}
        <div className="text-center mb-8">
          <div className="relative inline-block">
            <div className="w-24 h-24 bg-success-100 dark:bg-success-900/30 rounded-full flex items-center justify-center mx-auto mb-6 animate-bounce">
              <CheckCircle className="w-12 h-12 text-success-600 dark:text-success-400" />
            </div>
            <div className="absolute -top-2 -right-2 w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center animate-pulse">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
          </div>
          
          <h1 className="text-3xl sm:text-4xl font-bold text-surface-900 dark:text-white mb-2">
            You're All Set!
          </h1>
          <p className="text-surface-600 dark:text-surface-400">
            Your salon is ready to start taking bookings
          </p>
        </div>

        {/* Summary Card */}
        <div className="bg-white dark:bg-surface-800 rounded-2xl shadow-xl border border-surface-200 dark:border-surface-700 overflow-hidden mb-6">
          <div className="p-6 border-b border-surface-200 dark:border-surface-700">
            <h2 className="text-lg font-semibold text-surface-900 dark:text-white flex items-center gap-2">
              <Building2 className="w-5 h-5 text-primary-500" />
              Salon Summary
            </h2>
          </div>
          
          <div className="p-6 space-y-4">
            <SummaryItem
              icon={<Building2 className="w-5 h-5" />}
              label="Salon Name"
              value={salonData.name || 'Not set'}
              subValue={salonData.address ? `${salonData.address.city}, ${salonData.address.state}` : undefined}
            />
            
            <SummaryItem
              icon={<Users className="w-5 h-5" />}
              label="Team Size"
              value={`${staffMembers.length} staff member${staffMembers.length !== 1 ? 's' : ''}`}
              subValue={staffMembers.map(s => s.name).join(', ')}
            />
            
            <SummaryItem
              icon={<Scissors className="w-5 h-5" />}
              label="Services Offered"
              value={`${selectedServicesCount} services`}
              subValue="Ready for booking"
            />
            
            <SummaryItem
              icon={<Clock className="w-5 h-5" />}
              label="Business Hours"
              value={`${openDays} days per week`}
              subValue="Configured and active"
            />
          </div>
        </div>

        {/* Quick Tips */}
        <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-4 mb-6">
          <h3 className="text-sm font-semibold text-amber-800 dark:text-amber-200 mb-2">
            💡 Quick Tips to Get Started
          </h3>
          <ul className="text-sm text-amber-700 dark:text-amber-300 space-y-1 list-disc list-inside">
            <li>Share your booking link with customers</li>
            <li>Set up WhatsApp notifications in settings</li>
            <li>Explore the AI assistant for marketing ideas</li>
            <li>Add more services or staff anytime from settings</li>
          </ul>
        </div>

        {/* CTA */}
        <div className="text-center space-y-4">
          <Button
            onClick={handleGoToDashboard}
            size="lg"
            rightIcon={<ArrowRight className="w-5 h-5" />}
            className="w-full sm:w-auto px-8"
          >
            Go to Dashboard
          </Button>
          
          <p className="text-sm text-surface-500">
            Redirecting automatically in {countdown} seconds...
          </p>
        </div>
      </div>
    </div>
  );
};

export default Complete;
