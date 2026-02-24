/**
 * AI Types - TypeScript interfaces for AI service contracts
 * Updated for Task 2.6: Deep AI Integration
 */

// ============================================
// Chat Types
// ============================================
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    loading?: boolean;
    error?: boolean;
    cached?: boolean;
    tokens?: number;
  };
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
  context?: string;
}

// ============================================
// Morning Pulse Types
// ============================================
export interface MorningPulse {
  greeting: string;
  summary: {
    bookings_today: number;
    high_value_bookings: number;
    gaps_detected: number;
    potential_revenue: number;
  };
  recommendations: MorningPulseRecommendation[];
  alerts: MorningPulseAlert[];
  weather?: {
    condition: string;
    temp: number;
    impact?: string;
  };
}

export interface MorningPulseRecommendation {
  id: string;
  title: string;
  message: string;
  priority: 'high' | 'medium' | 'low';
  action?: {
    label: string;
    endpoint: string;
    payload?: Record<string, unknown>;
  };
}

export interface MorningPulseAlert {
  id: string;
  title: string;
  message: string;
  severity: 'critical' | 'warning' | 'info';
}

// ============================================
// AI Insights Types
// ============================================
export interface AIInsight {
  id: string;
  type: 'revenue' | 'operations' | 'marketing' | 'staff' | 'customer';
  title: string;
  message: string;
  priority: 'high' | 'medium' | 'low';
  read: boolean;
  createdAt: string;
  action?: {
    label: string;
    endpoint: string;
    payload?: Record<string, unknown>;
  };
  metadata?: Record<string, unknown>;
}

// ============================================
// Revenue Forecast Types
// ============================================
export interface RevenueForecast {
  current_period: {
    revenue: number;
    bookings: number;
  };
  predicted_period: {
    revenue: number;
    bookings: number;
  };
  trend: 'up' | 'down' | 'stable';
  confidence: number;
  factors: ForecastFactor[];
  daily_breakdown?: DailyForecast[];
}

export interface ForecastFactor {
  name: string;
  impact: 'positive' | 'negative' | 'neutral';
  weight: number;
  description?: string;
}

export interface DailyForecast {
  date: string;
  predicted_revenue: number;
  confidence: number;
}

// ============================================
// Staff Performance Types
// ============================================
export interface StaffPerformance {
  staff_id: string;
  name: string;
  avatar?: string;
  metrics: {
    utilization_rate: number;
    customer_rating: number;
    revenue_generated: number;
    bookings_completed: number;
    avg_service_time: number;
  };
  predictions: {
    next_week_bookings: number;
    performance_trend: 'improving' | 'stable' | 'declining';
    risk_factors?: string[];
  };
}

// ============================================
// Churn Risk Types
// ============================================
export interface ChurnRiskAlert {
  id: string;
  customer_id: string;
  customer_name: string;
  risk_score: number;
  risk_level: 'high' | 'medium' | 'low';
  last_visit: string;
  days_since_visit: number;
  suggested_action: string;
  potential_value: number;
  factors?: string[];
}

// ============================================
// Slot Optimization Types
// ============================================
export interface SlotOptimization {
  date: string;
  time_slot: string;
  current_utilization: number;
  recommended_action: 'promote' | 'discount' | 'block' | 'staff_adjust';
  reason: string;
  potential_revenue?: number;
}

export interface GapDetection {
  date: string;
  gaps: TimeGap[];
  recommendations: GapRecommendation[];
}

export interface TimeGap {
  start: string;
  end: string;
  duration_minutes: number;
  can_fill: boolean;
}

export interface GapRecommendation {
  gap_index: number;
  suggested_service?: string;
  suggested_staff?: string;
  potential_revenue: number;
}

// ============================================
// At-Risk Customer Types
// ============================================
export interface AtRiskCustomer {
  id: string;
  name: string;
  phone: string;
  last_visit: string;
  total_visits: number;
  lifetime_value: number;
  risk_score: number;
  risk_factors: string[];
  recommended_action: string;
}

// ============================================
// Campaign Types
// ============================================
export interface CampaignSuggestion {
  id: string;
  type: 'promotional' | 'birthday' | 'rebooking' | 'winback' | 'festival';
  title: string;
  message: string;
  target_segment: string;
  estimated_reach: number;
  estimated_conversion: number;
  suggested_discount?: string;
  channels: ('whatsapp' | 'sms' | 'email')[];
  timing: string;
}

// ============================================
// Dynamic Pricing Types
// ============================================
export interface DynamicPricingSuggestion {
  service_id: string;
  service_name: string;
  current_price: number;
  suggested_price: number;
  price_change_percent: number;
  reason: string;
  demand_level: 'high' | 'medium' | 'low';
  confidence: number;
}

// ============================================
// Smart Action Types
// ============================================
export interface SmartAction {
  id: string;
  type: 'campaign' | 'follow_up' | 'pricing' | 'inventory' | 'staffing';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  createdAt: string;
  completedAt?: string;
  params?: Record<string, unknown>;
  result?: unknown;
}

// ============================================
// Smart Reply Types
// ============================================
export interface SmartReplyContext {
  customer_name: string;
  last_message?: string;
  booking_status?: string;
  customer_type?: 'new' | 'regular' | 'vip';
}

// ============================================
// AI Service Response Types
// ============================================
export interface AIServiceResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  cached?: boolean;
  timestamp: string;
}

export interface AIStreamChunk {
  content: string;
  done: boolean;
  metadata?: {
    tokens?: number;
    model?: string;
  };
}

// ============================================
// AI Preferences Types
// ============================================
export interface AIPreferences {
  voiceInputEnabled: boolean;
  autoSuggestEnabled: boolean;
  soundEnabled: boolean;
  markdownEnabled: boolean;
  theme: 'light' | 'dark' | 'auto';
  language: 'en' | 'hi' | 'te';
  cacheEnabled: boolean;
  cacheDuration: number;
}

// ============================================
// AI Quota Types
// ============================================
export interface AIQuota {
  dailyLimit: number;
  usedToday: number;
  resetTime: string;
}
