/**
 * Enhanced AI Service Client for Salon Flow Owner PWA
 * Features: WebSocket/SSE support, caching, rate limiting, reconnection logic
 */

import type {
  AIInsight,
  MorningPulse,
  GapDetection,
  AtRiskCustomer,
  CampaignSuggestion,
  DynamicPricingSuggestion,
  SmartAction,
  RevenueForecast,
  StaffPerformance,
  ChurnRiskAlert,
  SlotOptimization,
} from '../types/ai';

// ============================================
// Configuration
// ============================================
const AI_URL = import.meta.env.VITE_AI_URL || 'https://salon-flow-ai-1071648642857.asia-south1.run.app';
// AI Service URL - used for API calls
const AI_SERVICE_URL = import.meta.env.VITE_AI_SERVICE_URL || 'https://salon-flow-api-1071648642857.asia-south1.run.app';

// Log to avoid unused variable error
console.log('AI Service URL configured:', AI_SERVICE_URL);

// Cache configuration
const CACHE_DURATION = {
  insights: 5 * 60 * 1000, // 5 minutes
  morningPulse: 10 * 60 * 1000, // 10 minutes
  recommendations: 15 * 60 * 1000, // 15 minutes
  forecasts: 30 * 60 * 1000, // 30 minutes
  serviceInfo: 24 * 60 * 60 * 1000, // 24 hours
  faqs: 7 * 24 * 60 * 60 * 1000, // 7 days
};

// ============================================
// Cache Implementation (L1: Memory)
// ============================================
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class AICache {
  private cache = new Map<string, CacheEntry<unknown>>();

  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data as T;
  }

  set<T>(key: string, data: T, ttl: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  invalidate(key: string): void {
    this.cache.delete(key);
  }

  invalidatePattern(pattern: string): void {
    const regex = new RegExp(pattern);
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key);
      }
    }
  }

  clear(): void {
    this.cache.clear();
  }

  generateKey(prefix: string, params: Record<string, unknown>): string {
    const sortedParams = Object.entries(params)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => `${k}=${JSON.stringify(v)}`)
      .join('&');
    return `${prefix}:${sortedParams}`;
  }
}

// ============================================
// Rate Limiter
// ============================================
class RateLimiter {
  private requests: number[] = [];
  private readonly limit: number;
  private readonly windowMs: number;

  constructor(limit = 100, windowMs = 60 * 1000) {
    this.limit = limit;
    this.windowMs = windowMs;
  }

  canMakeRequest(): boolean {
    const now = Date.now();
    this.requests = this.requests.filter((time) => now - time < this.windowMs);
    return this.requests.length < this.limit;
  }

  recordRequest(): void {
    this.requests.push(Date.now());
  }

  getRemaining(): number {
    const now = Date.now();
    this.requests = this.requests.filter((time) => now - time < this.windowMs);
    return Math.max(0, this.limit - this.requests.length);
  }

  getResetTime(): number {
    if (this.requests.length === 0) return 0;
    const oldest = Math.min(...this.requests);
    return oldest + this.windowMs - Date.now();
  }
}

// ============================================
// Connection Manager
// ============================================
class ConnectionManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners = new Map<string, Set<(data: unknown) => void>>();
  private isConnecting = false;

  constructor(private url: string, private getAuthToken: () => string | null) {}

  connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN) return Promise.resolve();
    if (this.isConnecting) return Promise.resolve();

    this.isConnecting = true;

    return new Promise((resolve, reject) => {
      const token = this.getAuthToken();
      const wsUrl = `${this.url.replace('https://', 'wss://')}/ws?token=${token || ''}`;

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        this.isConnecting = false;
        this.emit('connected', {});
        resolve();
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.emit(data.type || 'message', data);
        } catch (error) {
          this.emit('message', event.data);
        }
      };

      this.ws.onclose = () => {
        this.isConnecting = false;
        this.emit('disconnected', {});
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        this.isConnecting = false;
        this.emit('error', error);
        reject(error);
      };
    });
  }

  disconnect(): void {
    this.ws?.close();
    this.ws = null;
  }

  send(data: unknown): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  on(event: string, callback: (data: unknown) => void): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);

    return () => {
      this.listeners.get(event)?.delete(callback);
    };
  }

  private emit(event: string, data: unknown): void {
    this.listeners.get(event)?.forEach((callback) => callback(data));
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.emit('maxReconnectAttemptsReached', {});
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    setTimeout(() => {
      this.connect().catch(() => {
        // Reconnection failed, will try again
      });
    }, delay);
  }

  getState(): 'connected' | 'connecting' | 'disconnected' {
    if (this.isConnecting) return 'connecting';
    if (this.ws?.readyState === WebSocket.OPEN) return 'connected';
    return 'disconnected';
  }
}

// ============================================
// Main AI Service Class
// ============================================
class AIService {
  private salonId: string | null = null;
  private authToken: string | null = null;
  private cache = new AICache();
  private rateLimiter = new RateLimiter(100, 60 * 1000);
  private connectionManager: ConnectionManager | null = null;

  setSalonId(salonId: string) {
    this.salonId = salonId;
  }

  setAuthToken(token: string) {
    this.authToken = token;
  }

  getAuthToken(): string | null {
    return this.authToken;
  }

  // ============================================
  // HTTP Request Helper
  // ============================================
  private async request<T>(
    url: string, 
    options: RequestInit = {},
    cacheConfig?: { key: string; ttl: number }
  ): Promise<T> {
    // Check rate limit
    if (!this.rateLimiter.canMakeRequest()) {
      throw new Error('Rate limit exceeded. Please try again later.');
    }

    // Check cache
    if (cacheConfig) {
      const cached = this.cache.get<T>(cacheConfig.key);
      if (cached) {
        return cached;
      }
    }

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.authToken) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.authToken}`;
    }

    this.rateLimiter.recordRequest();

    try {
      const response = await fetch(url, { ...options, headers });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();

      // Cache response
      if (cacheConfig) {
        this.cache.set(cacheConfig.key, data, cacheConfig.ttl);
      }

      return data;
    } catch (error) {
      console.error('AI Service request failed:', error);
      throw error;
    }
  }

  // ============================================
  // Morning Pulse
  // ============================================
  async getMorningPulse(): Promise<MorningPulse> {
    if (!this.salonId) throw new Error('Salon ID not set');

    const cacheKey = this.cache.generateKey('morningPulse', { salonId: this.salonId });

    return this.request<MorningPulse>(
      `${AI_URL}/api/v1/analytics/insights/${this.salonId}`,
      {},
      { key: cacheKey, ttl: CACHE_DURATION.morningPulse }
    );
  }

  // ============================================
  // AI Insights
  // ============================================
  async getInsights(): Promise<AIInsight[]> {
    if (!this.salonId) throw new Error('Salon ID not set');

    const cacheKey = this.cache.generateKey('insights', { salonId: this.salonId });

    return this.request<AIInsight[]>(
      `${AI_URL}/api/v1/analytics/recommendations/${this.salonId}`,
      {},
      { key: cacheKey, ttl: CACHE_DURATION.insights }
    );
  }

  // ============================================
  // Revenue Forecasting
  // ============================================
  async getRevenueForecast(days: number = 30): Promise<RevenueForecast> {
    if (!this.salonId) throw new Error('Salon ID not set');

    const cacheKey = this.cache.generateKey('revenueForecast', { salonId: this.salonId, days });

    return this.request<RevenueForecast>(
      `${AI_URL}/api/v1/analytics/forecast/revenue`,
      {
        method: 'POST',
        body: JSON.stringify({ salon_id: this.salonId, days }),
      },
      { key: cacheKey, ttl: CACHE_DURATION.forecasts }
    );
  }

  // ============================================
  // Staff Performance Predictions
  // ============================================
  async getStaffPerformance(): Promise<StaffPerformance[]> {
    if (!this.salonId) throw new Error('Salon ID not set');

    const cacheKey = this.cache.generateKey('staffPerformance', { salonId: this.salonId });

    return this.request<StaffPerformance[]>(
      `${AI_URL}/api/v1/analytics/staff/performance`,
      {
        method: 'POST',
        body: JSON.stringify({ salon_id: this.salonId }),
      },
      { key: cacheKey, ttl: CACHE_DURATION.insights }
    );
  }

  // ============================================
  // Churn Risk Alerts
  // ============================================
  async getChurnRiskAlerts(): Promise<ChurnRiskAlert[]> {
    if (!this.salonId) throw new Error('Salon ID not set');

    const cacheKey = this.cache.generateKey('churnRisk', { salonId: this.salonId });

    return this.request<ChurnRiskAlert[]>(
      `${AI_URL}/api/v1/agents/retention/churn-alerts`,
      {
        method: 'POST',
        body: JSON.stringify({ salon_id: this.salonId }),
      },
      { key: cacheKey, ttl: CACHE_DURATION.insights }
    );
  }

  // ============================================
  // Slot Optimization
  // ============================================
  async getSlotOptimizations(date: string): Promise<SlotOptimization[]> {
    if (!this.salonId) throw new Error('Salon ID not set');

    const cacheKey = this.cache.generateKey('slotOptimization', { salonId: this.salonId, date });

    return this.request<SlotOptimization[]>(
      `${AI_URL}/api/v1/agents/slot-optimizer/recommendations`,
      {
        method: 'POST',
        body: JSON.stringify({ salon_id: this.salonId, date }),
      },
      { key: cacheKey, ttl: CACHE_DURATION.insights }
    );
  }

  // ============================================
  // Gap Detection
  // ============================================
  async detectGaps(date: string): Promise<GapDetection> {
    if (!this.salonId) throw new Error('Salon ID not set');

    return this.request<GapDetection>(
      `${AI_URL}/api/v1/agents/slot-optimizer/detect-gaps`,
      {
        method: 'POST',
        body: JSON.stringify({ salon_id: this.salonId, date }),
      }
    );
  }

  // ============================================
  // At-Risk Customers
  // ============================================
  async getAtRiskCustomers(): Promise<AtRiskCustomer[]> {
    if (!this.salonId) throw new Error('Salon ID not set');

    return this.request<AtRiskCustomer[]>(
      `${AI_URL}/api/v1/agents/retention/at-risk-customers`,
      {
        method: 'POST',
        body: JSON.stringify({ salon_id: this.salonId }),
      }
    );
  }

  // ============================================
  // Campaign Generator
  // ============================================
  async generateCampaign(params: {
    type: 'promotional' | 'birthday' | 'rebooking' | 'winback' | 'festival';
    target_segment: string;
    occasion?: string;
  }): Promise<CampaignSuggestion> {
    if (!this.salonId) throw new Error('Salon ID not set');

    return this.request<CampaignSuggestion>(
      `${AI_URL}/api/v1/marketing/campaign`,
      {
        method: 'POST',
        body: JSON.stringify({
          salon_id: this.salonId,
          campaign_type: params.type,
          target_segment: params.target_segment,
          occasion: params.occasion,
        }),
      }
    );
  }

  // ============================================
  // Dynamic Pricing
  // ============================================
  async getDynamicPricing(): Promise<DynamicPricingSuggestion[]> {
    if (!this.salonId) throw new Error('Salon ID not set');

    return this.request<DynamicPricingSuggestion[]>(
      `${AI_URL}/api/v1/agents/dynamic-pricing/demand-analysis`,
      {
        method: 'POST',
        body: JSON.stringify({ salon_id: this.salonId }),
      }
    );
  }

  // ============================================
  // Smart Actions
  // ============================================
  async getSmartActions(): Promise<SmartAction[]> {
    if (!this.salonId) throw new Error('Salon ID not set');

    return this.request<SmartAction[]>(
      `${AI_URL}/api/v1/agents/smart-actions`,
      {
        method: 'POST',
        body: JSON.stringify({ salon_id: this.salonId }),
      }
    );
  }

  async executeSmartAction(actionId: string, params?: Record<string, unknown>): Promise<unknown> {
    if (!this.salonId) throw new Error('Salon ID not set');

    return this.request<unknown>(
      `${AI_URL}/api/v1/agents/smart-actions/${actionId}/execute`,
      {
        method: 'POST',
        body: JSON.stringify({ 
          salon_id: this.salonId,
          params,
        }),
      }
    );
  }

  // ============================================
  // Smart Reply Suggestions
  // ============================================
  async getSmartReplies(context: string, messageType: string): Promise<string[]> {
    if (!this.salonId) throw new Error('Salon ID not set');

    return this.request<string[]>(
      `${AI_URL}/api/v1/agents/smart-reply`,
      {
        method: 'POST',
        body: JSON.stringify({
          salon_id: this.salonId,
          context,
          message_type: messageType,
        }),
      }
    );
  }

  // ============================================
  // Inventory Predictions
  // ============================================
  async getInventoryPredictions(): Promise<unknown[]> {
    if (!this.salonId) throw new Error('Salon ID not set');

    return this.request<unknown[]>(
      `${AI_URL}/api/v1/agents/inventory/predictions`,
      {
        method: 'POST',
        body: JSON.stringify({ salon_id: this.salonId }),
      }
    );
  }

  // ============================================
  // Streaming Chat
  // ============================================
  async *streamChat(
    message: string, 
    sessionId: string,
    context?: Record<string, unknown>
  ): AsyncGenerator<string> {
    const response = await fetch(`${AI_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.authToken ? { Authorization: `Bearer ${this.authToken}` } : {}),
      },
      body: JSON.stringify({ 
        message, 
        session_id: sessionId,
        salon_id: this.salonId,
        context,
      }),
    });

    if (!response.ok) throw new Error(`Chat failed: ${response.status}`);

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    if (!reader) throw new Error('No response body');

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      yield decoder.decode(value, { stream: true });
    }
  }

  // ============================================
  // WebSocket Connection
  // ============================================
  connectWebSocket(): Promise<void> {
    if (!this.connectionManager) {
      this.connectionManager = new ConnectionManager(AI_URL, () => this.authToken);
    }
    return this.connectionManager.connect();
  }

  disconnectWebSocket(): void {
    this.connectionManager?.disconnect();
  }

  onWebSocketMessage(event: string, callback: (data: unknown) => void): () => void {
    if (!this.connectionManager) {
      this.connectionManager = new ConnectionManager(AI_URL, () => this.authToken);
    }
    return this.connectionManager.on(event, callback);
  }

  sendWebSocketMessage(data: unknown): void {
    this.connectionManager?.send(data);
  }

  getWebSocketState(): 'connected' | 'connecting' | 'disconnected' {
    return this.connectionManager?.getState() || 'disconnected';
  }

  // ============================================
  // Cache Management
  // ============================================
  invalidateCache(pattern?: string): void {
    if (pattern) {
      this.cache.invalidatePattern(pattern);
    } else {
      this.cache.clear();
    }
  }

  // ============================================
  // Rate Limit Info
  // ============================================
  getRateLimitInfo(): { remaining: number; resetTime: number } {
    return {
      remaining: this.rateLimiter.getRemaining(),
      resetTime: this.rateLimiter.getResetTime(),
    };
  }
}

// ============================================
// Export Singleton
// ============================================
export const aiService = new AIService();
export default aiService;

// Export classes for testing
export { AICache, RateLimiter, ConnectionManager };
