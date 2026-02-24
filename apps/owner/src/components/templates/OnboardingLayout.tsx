/**
 * Salon Flow Owner PWA - Onboarding Layout
 * Full-screen wizard layout with step navigation
 */

import React, { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useOnboardingStore } from '@/stores/onboardingStore';
import { Button } from '@/components/atoms/Button';
import { Check, ChevronLeft, ChevronRight, X, Loader2 } from 'lucide-react';

interface StepConfig {
  id: number;
  title: string;
  description: string;
}

const steps: StepConfig[] = [
  { id: 1, title: 'Salon', description: 'Basic information' },
  { id: 2, title: 'Layout', description: 'Configure space' },
  { id: 3, title: 'Services', description: 'Add services' },
  { id: 4, title: 'Staff', description: 'Team members' },
  { id: 5, title: 'Hours', description: 'Business hours' },
];

interface OnboardingLayoutProps {
  children: React.ReactNode;
}

export const OnboardingLayout: React.FC<OnboardingLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const { 
    currentStep, 
    setCurrentStep,
    nextStep, 
    previousStep,
    completedSteps,
    canProceed,
    isSubmitting,
  } = useOnboardingStore();

  const handleNext = useCallback(() => {
    if (canProceed(currentStep)) {
      if (currentStep < steps.length) {
        nextStep();
      } else {
        navigate('/onboarding/complete');
      }
    }
  }, [currentStep, canProceed, nextStep, navigate]);

  const handleBack = useCallback(() => {
    if (currentStep > 1) {
      previousStep();
    }
  }, [currentStep, previousStep]);

  const handleSkip = useCallback(() => {
    navigate('/dashboard');
  }, [navigate]);

  const handleStepClick = useCallback((stepId: number) => {
    // Allow clicking on completed steps or the next immediate step
    if (completedSteps.includes(stepId) || stepId === currentStep + 1) {
      setCurrentStep(stepId);
    }
  }, [completedSteps, currentStep, setCurrentStep]);

  const isStepAccessible = (stepId: number) => {
    return completedSteps.includes(stepId) || stepId <= currentStep;
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-surface-50 via-white to-primary-50 dark:from-surface-900 dark:via-surface-900 dark:to-primary-900/20">
      {/* Header with progress */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-surface-900/80 backdrop-blur-xl border-b border-surface-200 dark:border-surface-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-lg">S</span>
              </div>
              <div>
                <h1 className="text-lg font-semibold text-surface-900 dark:text-white">
                  Salon Setup
                </h1>
                <p className="text-sm text-surface-500">
                  Step {currentStep} of {steps.length}
                </p>
              </div>
            </div>
            <button
              onClick={handleSkip}
              className="flex items-center gap-2 text-sm text-surface-500 hover:text-surface-700 dark:text-surface-400 dark:hover:text-surface-200 transition-colors"
            >
              <X className="w-4 h-4" />
              Skip for now
            </button>
          </div>

          {/* Step indicators */}
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const isCompleted = completedSteps.includes(step.id);
              const isCurrent = currentStep === step.id;
              const isAccessible = isStepAccessible(step.id);

              return (
                <React.Fragment key={step.id}>
                  <button
                    onClick={() => handleStepClick(step.id)}
                    disabled={!isAccessible}
                    className={`flex flex-col items-center gap-2 transition-all ${
                      isAccessible ? 'cursor-pointer' : 'cursor-not-allowed opacity-50'
                    }`}
                  >
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-all ${
                        isCompleted
                          ? 'bg-green-500 text-white'
                          : isCurrent
                          ? 'bg-primary-500 text-white ring-4 ring-primary-500/20'
                          : 'bg-surface-200 text-surface-500 dark:bg-surface-700 dark:text-surface-400'
                      }`}
                    >
                      {isCompleted ? (
                        <Check className="w-5 h-5" />
                      ) : (
                        step.id
                      )}
                    </div>
                    <span
                      className={`text-xs font-medium hidden sm:block ${
                        isCurrent
                          ? 'text-primary-600 dark:text-primary-400'
                          : 'text-surface-500'
                      }`}
                    >
                      {step.title}
                    </span>
                  </button>
                  {index < steps.length - 1 && (
                    <div
                      className={`flex-1 h-0.5 mx-2 transition-all ${
                        isCompleted
                          ? 'bg-green-500'
                          : 'bg-surface-200 dark:bg-surface-700'
                      }`}
                    />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="pt-40 pb-32 px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl mx-auto">
          {children}
        </div>
      </main>

      {/* Footer navigation */}
      <footer className="fixed bottom-0 left-0 right-0 bg-white/80 dark:bg-surface-900/80 backdrop-blur-xl border-t border-surface-200 dark:border-surface-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={handleBack}
              disabled={currentStep === 1}
              leftIcon={<ChevronLeft className="w-5 h-5" />}
            >
              Back
            </Button>

            <div className="flex items-center gap-4">
              <span className="text-sm text-surface-500">
                {completedSteps.length} of {steps.length} completed
              </span>
              <Button
                onClick={handleNext}
                disabled={!canProceed(currentStep) || isSubmitting}
                rightIcon={
                  isSubmitting ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <ChevronRight className="w-5 h-5" />
                  )
                }
              >
                {currentStep === steps.length ? 'Complete Setup' : 'Continue'}
              </Button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default OnboardingLayout;
