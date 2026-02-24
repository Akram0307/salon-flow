/**
 * MorningPulseWidget Component
 * Displays daily business summary with AI insights
 */

import { motion } from 'framer-motion';
import { useAIInsights } from '../../../hooks/ai/useAIInsights';

export const MorningPulseWidget: React.FC = () => {
  const { morningPulse, isLoadingPulse, refetchPulse } = useAIInsights();

  if (isLoadingPulse) {
    return (
      <div className="bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-sm border border-surface-200 dark:border-surface-700 animate-pulse">
        <div className="h-4 bg-surface-200 dark:bg-surface-700 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-3 bg-surface-200 dark:bg-surface-700 rounded w-full"></div>
          <div className="h-3 bg-surface-200 dark:bg-surface-700 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (!morningPulse) {
    return (
      <div className="bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-sm border border-surface-200 dark:border-surface-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-surface-900 dark:text-white">Morning Pulse</h3>
          <button
            onClick={refetchPulse}
            className="p-2 text-surface-500 hover:text-primary-600 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
        <p className="text-surface-500 dark:text-surface-400">No morning pulse data available</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-sm border border-surface-200 dark:border-surface-700"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-surface-900 dark:text-white">Morning Pulse</h3>
          <p className="text-sm text-surface-500 dark:text-surface-400">
            {new Date().toLocaleDateString('en-IN', { weekday: 'long', month: 'short', day: 'numeric' })}
          </p>
        </div>
        <button
          onClick={refetchPulse}
          className="p-2 text-surface-500 hover:text-primary-600 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-primary-50 dark:bg-primary-900/20 rounded-xl p-3">
          <p className="text-xs text-surface-500 dark:text-surface-400">Today's Bookings</p>
          <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">
            {(morningPulse as any).today_bookings || 0}
          </p>
        </div>
        <div className="bg-accent-50 dark:bg-accent-900/20 rounded-xl p-3">
          <p className="text-xs text-surface-500 dark:text-surface-400">Expected Revenue</p>
          <p className="text-2xl font-bold text-accent-600 dark:text-accent-400">
            ₹{((morningPulse as any).expected_revenue || 0).toLocaleString('en-IN')}
          </p>
        </div>
      </div>

      <div className="space-y-2">
        <h4 className="text-sm font-medium text-surface-700 dark:text-surface-300">AI Insights</h4>
        {((morningPulse as any).ai_insights || []).map((insight: string, index: number) => (
          <div
            key={index}
            className="flex items-start gap-2 text-sm text-surface-600 dark:text-surface-400"
          >
            <svg className="w-4 h-4 text-primary-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span>{insight}</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
};

export default MorningPulseWidget;
