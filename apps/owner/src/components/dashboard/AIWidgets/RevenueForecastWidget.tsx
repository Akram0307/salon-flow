/**
 * RevenueForecastWidget Component
 * Displays AI-powered revenue predictions
 */

import { motion } from 'framer-motion';
import { useAIInsights } from '../../../hooks/ai/useAIInsights';

export const RevenueForecastWidget: React.FC = () => {
  const { revenueForecast, isLoadingForecast } = useAIInsights();

  if (isLoadingForecast) {
    return (
      <div className="bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-sm border border-surface-200 dark:border-surface-700 animate-pulse">
        <div className="h-4 bg-surface-200 dark:bg-surface-700 rounded w-1/3 mb-4"></div>
        <div className="h-32 bg-surface-200 dark:bg-surface-700 rounded"></div>
      </div>
    );
  }

  if (!revenueForecast) {
    return (
      <div className="bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-sm border border-surface-200 dark:border-surface-700">
        <h3 className="text-lg font-semibold text-surface-900 dark:text-white mb-4">Revenue Forecast</h3>
        <p className="text-surface-500 dark:text-surface-400">No forecast data available</p>
      </div>
    );
  }

  const trend = (revenueForecast as any).trend || 'stable';
  const confidence = (revenueForecast as any).confidence || 85;
  const factors = (revenueForecast as any).factors || [];
  const trendColor = trend === 'up' ? 'text-green-600 dark:text-green-400' : 
                     trend === 'down' ? 'text-red-600 dark:text-red-400' : 
                     'text-surface-600 dark:text-surface-400';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-sm border border-surface-200 dark:border-surface-700"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-surface-900 dark:text-white">Revenue Forecast</h3>
        <div className={`flex items-center gap-1 text-sm font-medium ${trendColor}`}>
          {trend === 'up' && (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          )}
          {trend === 'down' && (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
            </svg>
          )}
          <span>{confidence}% confidence</span>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-3xl font-bold text-surface-900 dark:text-white">
          ₹{((revenueForecast as any).predicted_revenue || 0).toLocaleString('en-IN')}
        </p>
        <p className="text-sm text-surface-500 dark:text-surface-400">
          Predicted for next 30 days
        </p>
      </div>

      <div className="space-y-2">
        <h4 className="text-sm font-medium text-surface-700 dark:text-surface-300">Key Factors</h4>
        {factors.map((factor: any, index: number) => (
          <div
            key={index}
            className="flex items-start gap-2 text-sm text-surface-600 dark:text-surface-400"
          >
            <svg className="w-4 h-4 text-accent-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span>{typeof factor === 'string' ? factor : factor.name || 'Unknown factor'}</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
};

export default RevenueForecastWidget;
