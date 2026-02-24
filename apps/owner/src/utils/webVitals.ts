import { onCLS, onFCP, onLCP, onTTFB, onINP, type Metric } from 'web-vitals';

// Web Vitals thresholds based on Google's Core Web Vitals
const THRESHOLDS = {
  LCP: { good: 2500, poor: 4000 },      // Largest Contentful Paint (ms)
  INP: { good: 200, poor: 500 },        // Interaction to Next Paint (ms) - replaces FID
  CLS: { good: 0.1, poor: 0.25 },       // Cumulative Layout Shift
  FCP: { good: 1800, poor: 3000 },      // First Contentful Paint (ms)
  TTFB: { good: 800, poor: 1800 },      // Time to First Byte (ms)
};

type WebVitalRating = 'good' | 'needs-improvement' | 'poor';

function getRating(name: string, value: number): WebVitalRating {
  const threshold = THRESHOLDS[name as keyof typeof THRESHOLDS];
  if (!threshold) return 'good';
  
  if (value <= threshold.good) return 'good';
  if (value <= threshold.poor) return 'needs-improvement';
  return 'poor';
}

// Send metrics to analytics endpoint
function sendToAnalytics(metric: Metric) {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
    delta: metric.delta,
    id: metric.id,
    navigationType: metric.navigationType,
    timestamp: new Date().toISOString(),
    url: window.location.href,
    userAgent: navigator.userAgent,
  });

  // Use sendBeacon for reliable delivery
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/api/analytics/web-vitals', body);
  } else {
    fetch('/api/analytics/web-vitals', {
      body,
      method: 'POST',
      keepalive: true,
      headers: { 'Content-Type': 'application/json' },
    }).catch(() => {
      // Silently fail - don't block user experience
    });
  }
}

// Log to console in development
function logToConsole(metric: Metric) {
  if (import.meta.env.DEV) {
    const rating = getRating(metric.name, metric.value);
    const emoji = rating === 'good' ? '✅' : rating === 'needs-improvement' ? '⚠️' : '❌';
    console.log(
      `%c${emoji} ${metric.name}:`,
      `color: ${rating === 'good' ? 'green' : rating === 'needs-improvement' ? 'orange' : 'red'}; font-weight: bold;`,
      `${Math.round(metric.value * 100) / 100}${metric.name === 'CLS' ? '' : 'ms'}`,
      `(${rating})`
    );
  }
}

// Report all Web Vitals
export function reportWebVitals() {
  try {
    onCLS((metric) => {
      logToConsole(metric);
      sendToAnalytics(metric);
    });
    
    onINP((metric) => {
      logToConsole(metric);
      sendToAnalytics(metric);
    });
    
    onFCP((metric) => {
      logToConsole(metric);
      sendToAnalytics(metric);
    });
    
    onLCP((metric) => {
      logToConsole(metric);
      sendToAnalytics(metric);
    });
    
    onTTFB((metric) => {
      logToConsole(metric);
      sendToAnalytics(metric);
    });
  } catch (error) {
    console.error('Failed to initialize Web Vitals:', error);
  }
}

// Get current Web Vitals summary
export function getWebVitalsSummary(): Promise<Record<string, number>> {
  return new Promise((resolve) => {
    const metrics: Record<string, number> = {};
    let count = 0;
    const total = 5;
    
    const checkComplete = () => {
      count++;
      if (count >= total) {
        resolve(metrics);
      }
    };
    
    onCLS((m: Metric) => { metrics.CLS = m.value; checkComplete(); }, { reportAllChanges: true });
    onINP((m: Metric) => { metrics.INP = m.value; checkComplete(); }, { reportAllChanges: true });
    onFCP((m: Metric) => { metrics.FCP = m.value; checkComplete(); });
    onLCP((m: Metric) => { metrics.LCP = m.value; checkComplete(); }, { reportAllChanges: true });
    onTTFB((m: Metric) => { metrics.TTFB = m.value; checkComplete(); });
    
    // Timeout after 10 seconds
    setTimeout(() => resolve(metrics), 10000);
  });
}

export { THRESHOLDS };
export type { Metric, WebVitalRating };
