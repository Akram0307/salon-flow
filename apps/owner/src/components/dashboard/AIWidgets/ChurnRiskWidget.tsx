/**
 * ChurnRiskWidget Component
 * Displays at-risk customers with AI predictions
 */

import { motion } from 'framer-motion';
import { useAIInsights } from '../../../hooks/ai/useAIInsights';
import { cn } from '../../../lib/utils';

export const ChurnRiskWidget: React.FC = () => {
  const { churnRiskAlerts, isLoadingChurn } = useAIInsights();

  if (isLoadingChurn) {
    return (
      <div className="bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-sm border border-surface-200 dark:border-surface-700 animate-pulse">
        <div className="h-4 bg-surface-200 dark:bg-surface-700 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-12 bg-surface-200 dark:bg-surface-700 rounded"></div>
          <div className="h-12 bg-surface-200 dark:bg-surface-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (!churnRiskAlerts || churnRiskAlerts.length === 0) {
    return (
      <div className="bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-sm border border-surface-200 dark:border-surface-700">
        <h3 className="text-lg font-semibold text-surface-900 dark:text-white mb-4">Churn Risk</h3>
        <div className="text-center py-6">
          <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
            <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-surface-600 dark:text-surface-400 text-sm">No at-risk customers detected</p>
        </div>
      </div>
    );
  }

  const highRiskCount = churnRiskAlerts.filter((a: any) => a.risk_level === 'high').length;
  const avgRiskScore = churnRiskAlerts.reduce((sum: number, a: any) => sum + a.risk_score, 0) / churnRiskAlerts.length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-sm border border-surface-200 dark:border-surface-700"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-surface-900 dark:text-white">Churn Risk</h3>
        <div className="flex items-center gap-2">
          <span className={cn(
            'px-2 py-1 rounded-full text-xs font-medium',
            highRiskCount > 0 
              ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
              : 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
          )}>
            {highRiskCount} High Risk
          </span>
        </div>
      </div>

      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-surface-500 dark:text-surface-400">Average Risk Score</span>
          <span className={cn(
            'text-lg font-bold',
            avgRiskScore > 70 ? 'text-red-600 dark:text-red-400' :
            avgRiskScore > 40 ? 'text-yellow-600 dark:text-yellow-400' :
            'text-green-600 dark:text-green-400'
          )}>
            {avgRiskScore.toFixed(0)}%
          </span>
        </div>
        <div className="h-2 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden">
          <div
            className={cn(
              'h-full rounded-full transition-all duration-500',
              avgRiskScore > 70 ? 'bg-red-500' :
              avgRiskScore > 40 ? 'bg-yellow-500' :
              'bg-green-500'
            )}
            style={{ width: `${avgRiskScore}%` }}
          />
        </div>
      </div>

      <div className="space-y-3">
        <h4 className="text-sm font-medium text-surface-700 dark:text-surface-300">At-Risk Customers</h4>
        {churnRiskAlerts.slice(0, 3).map((alert: any) => (
          <div
            key={alert.customer_id}
            className="flex items-center justify-between p-3 bg-surface-50 dark:bg-surface-700/50 rounded-xl"
          >
            <div className="flex items-center gap-3">
              <div className={cn(
                'w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium',
                alert.risk_level === 'high'
                  ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                  : alert.risk_level === 'medium'
                  ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400'
                  : 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
              )}>
                {alert.customer_name?.charAt(0) || '?'}
              </div>
              <div>
                <p className="text-sm font-medium text-surface-900 dark:text-white">{alert.customer_name}</p>
                <p className="text-xs text-surface-500 dark:text-surface-400">
                  Last visit: {alert.days_since_last_visit} days ago
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className={cn(
                'text-sm font-bold',
                alert.risk_score > 70 ? 'text-red-600 dark:text-red-400' :
                alert.risk_score > 40 ? 'text-yellow-600 dark:text-yellow-400' :
                'text-green-600 dark:text-green-400'
              )}>
                {alert.risk_score}%
              </p>
              <p className="text-xs text-surface-500 dark:text-surface-400 capitalize">{alert.risk_level}</p>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
};

export default ChurnRiskWidget;
