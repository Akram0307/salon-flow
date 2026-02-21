/**
 * Integrations Service
 * Handles API calls for salon integrations (Twilio BYOK)
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Types
export type IntegrationMode = 'platform' | 'byok';
export type IntegrationStatus = 'active' | 'pending' | 'failed' | 'disabled';

export interface TwilioConfig {
  salon_id: string;
  mode: IntegrationMode;
  status: IntegrationStatus;
  whatsapp_number: string | null;
  sms_number: string | null;
  account_sid_preview: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface IntegrationStatusResponse {
  twilio: TwilioConfig | null;
  has_platform_access: boolean;
  platform_whatsapp_number: string | null;
}

export interface TwilioConfigRequest {
  account_sid: string;
  auth_token: string;
  whatsapp_number: string;
  sms_number?: string;
}

export interface TwilioTestRequest {
  to_number: string;
}

export interface TwilioTestResponse {
  success: boolean;
  message: string;
  message_sid?: string;
  error?: string;
}

export interface ProvisionNumberRequest {
  area_code?: string;
  capabilities?: string[];
}

export interface ProvisionNumberResponse {
  success: boolean;
  message: string;
  phone_number?: string;
  error?: string;
}

// API Client
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Integrations Service
 */
export const integrationsService = {
  /**
   * Get current Twilio configuration
   */
  async getTwilioConfig(): Promise<TwilioConfig> {
    const response = await api.get<TwilioConfig>('/api/v1/integrations/twilio');
    return response.data;
  },

  /**
   * Get overall integration status
   */
  async getIntegrationStatus(): Promise<IntegrationStatusResponse> {
    const response = await api.get<IntegrationStatusResponse>('/api/v1/integrations/status');
    return response.data;
  },

  /**
   * Save Twilio BYOK configuration
   */
  async saveTwilioConfig(config: TwilioConfigRequest): Promise<TwilioConfig> {
    const response = await api.post<TwilioConfig>('/api/v1/integrations/twilio', config);
    return response.data;
  },

  /**
   * Delete BYOK configuration (switch to platform)
   */
  async deleteTwilioConfig(): Promise<{ success: boolean; message: string; mode: string }> {
    const response = await api.delete<{ success: boolean; message: string; mode: string }>('/api/v1/integrations/twilio');
    return response.data;
  },

  /**
   * Test Twilio configuration
   */
  async testTwilioConfig(request: TwilioTestRequest): Promise<TwilioTestResponse> {
    const response = await api.post<TwilioTestResponse>('/api/v1/integrations/twilio/test', request);
    return response.data;
  },

  /**
   * Provision a platform Twilio number
   */
  async provisionPlatformNumber(request: ProvisionNumberRequest): Promise<ProvisionNumberResponse> {
    const response = await api.post<ProvisionNumberResponse>('/api/v1/integrations/twilio/provision', request);
    return response.data;
  },
};

export default integrationsService;
