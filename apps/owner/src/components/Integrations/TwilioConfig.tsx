/**
 * Twilio Configuration Component
 * 
 * Allows salon owners to configure WhatsApp/SMS messaging:
 * - Platform Mode: Use platform-provided Twilio subaccount
 * - BYOK Mode: Bring Your Own Keys (salon's own Twilio account)
 */
import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import integrationsService, {
  IntegrationMode,
  TwilioConfig as TwilioConfigType,
  TwilioConfigRequest,
  TwilioTestResponse,
} from '../../services/integrationsService';

// Icons
const WhatsAppIcon = () => (
  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
  </svg>
);

const CheckIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

const XIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const InfoIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

// Status Badge Component
const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const statusStyles: Record<string, string> = {
    active: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    failed: 'bg-red-100 text-red-800',
    disabled: 'bg-gray-100 text-gray-800',
  };

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusStyles[status] || statusStyles.disabled}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

// Mode Toggle Component
const ModeToggle: React.FC<{
  mode: IntegrationMode;
  onChange: (mode: IntegrationMode) => void;
  disabled?: boolean;
}> = ({ mode, onChange, disabled }) => (
  <div className="flex rounded-lg overflow-hidden border border-gray-300">
    <button
      type="button"
      onClick={() => onChange('platform')}
      disabled={disabled}
      className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
        mode === 'platform'
          ? 'bg-purple-600 text-white'
          : 'bg-white text-gray-700 hover:bg-gray-50'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      🏢 Platform Number
    </button>
    <button
      type="button"
      onClick={() => onChange('byok')}
      disabled={disabled}
      className={`flex-1 px-4 py-2 text-sm font-medium transition-colors border-l border-gray-300 ${
        mode === 'byok'
          ? 'bg-purple-600 text-white'
          : 'bg-white text-gray-700 hover:bg-gray-50'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      🔑 Bring Your Own
    </button>
  </div>
);

// BYOK Form Component
const BYOKForm: React.FC<{
  initialData?: Partial<TwilioConfigType>;
  onSubmit: (data: TwilioConfigRequest) => void;
  onTest: (to: string) => void;
  isLoading: boolean;
  testResult: TwilioTestResponse | null;
}> = ({ initialData, onSubmit, onTest, isLoading, testResult }) => {
  const [formData, setFormData] = useState<TwilioConfigRequest>({
    account_sid: '',
    auth_token: '',
    whatsapp_number: initialData?.whatsapp_number || '',
    sms_number: initialData?.sms_number || '',
  });
  const [testPhone, setTestPhone] = useState('');
  const [showTestInput, setShowTestInput] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleTest = () => {
    if (testPhone) {
      onTest(testPhone);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Twilio Account SID *
        </label>
        <input
          type="text"
          required
          placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
          value={formData.account_sid}
          onChange={(e) => setFormData({ ...formData, account_sid: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        />
        <p className="mt-1 text-xs text-gray-500">
          Find this in your Twilio Console Dashboard
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Auth Token *
        </label>
        <input
          type="password"
          required
          placeholder="Your Twilio Auth Token"
          value={formData.auth_token}
          onChange={(e) => setFormData({ ...formData, auth_token: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        />
        <p className="mt-1 text-xs text-gray-500">
          Keep this secret! Find it in Twilio Console → Settings → API Keys
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          WhatsApp Number *
        </label>
        <input
          type="tel"
          required
          placeholder="+91XXXXXXXXXX"
          value={formData.whatsapp_number}
          onChange={(e) => setFormData({ ...formData, whatsapp_number: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        />
        <p className="mt-1 text-xs text-gray-500">
          Your Twilio WhatsApp number in E.164 format
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          SMS Number (Optional)
        </label>
        <input
          type="tel"
          placeholder="+91XXXXXXXXXX"
          value={formData.sms_number}
          onChange={(e) => setFormData({ ...formData, sms_number: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        />
      </div>

      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          disabled={isLoading}
          className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Saving...' : 'Save Configuration'}
        </button>
        <button
          type="button"
          onClick={() => setShowTestInput(!showTestInput)}
          className="px-4 py-2 border border-purple-600 text-purple-600 rounded-lg hover:bg-purple-50 transition-colors"
        >
          Test
        </button>
      </div>

      {showTestInput && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Send test message to:
          </label>
          <div className="flex gap-2">
            <input
              type="tel"
              placeholder="+91XXXXXXXXXX"
              value={testPhone}
              onChange={(e) => setTestPhone(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <button
              type="button"
              onClick={handleTest}
              disabled={!testPhone || isLoading}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      )}

      {testResult && (
        <div className={`mt-4 p-4 rounded-lg ${testResult.success ? 'bg-green-50' : 'bg-red-50'}`}>
          <div className="flex items-center gap-2">
            {testResult.success ? (
              <span className="text-green-600"><CheckIcon /></span>
            ) : (
              <span className="text-red-600"><XIcon /></span>
            )}
            <span className={testResult.success ? 'text-green-800' : 'text-red-800'}>
              {testResult.message}
            </span>
          </div>
          {testResult.message_sid && (
            <p className="mt-1 text-xs text-gray-500">Message SID: {testResult.message_sid}</p>
          )}
          {testResult.error && (
            <p className="mt-1 text-sm text-red-600">{testResult.error}</p>
          )}
        </div>
      )}
    </form>
  );
};

// Main TwilioConfig Component
const TwilioConfig: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedMode, setSelectedMode] = useState<IntegrationMode>('platform');
  const [testResult, setTestResult] = useState<TwilioTestResponse | null>(null);

  // Fetch current config
  const { data: config, isLoading: configLoading } = useQuery({
    queryKey: ['twilio-config'],
    queryFn: integrationsService.getTwilioConfig,
  });

  // Fetch integration status
  const { data: status } = useQuery({
    queryKey: ['integration-status'],
    queryFn: integrationsService.getIntegrationStatus,
  });

  // Save BYOK config mutation
  const saveMutation = useMutation({
    mutationFn: integrationsService.saveTwilioConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['twilio-config'] });
      queryClient.invalidateQueries({ queryKey: ['integration-status'] });
    },
  });

  // Delete BYOK config mutation
  const deleteMutation = useMutation({
    mutationFn: integrationsService.deleteTwilioConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['twilio-config'] });
      queryClient.invalidateQueries({ queryKey: ['integration-status'] });
      setSelectedMode('platform');
    },
  });

  // Test config mutation
  const testMutation = useMutation({
    mutationFn: integrationsService.testTwilioConfig,
    onSuccess: (data) => {
      setTestResult(data);
    },
  });

  // Update mode when config loads
  useEffect(() => {
    if (config) {
      setSelectedMode(config.mode);
    }
  }, [config]);

  const handleModeChange = (mode: IntegrationMode) => {
    if (mode === 'platform' && config?.mode === 'byok') {
      // Confirm before switching to platform
      if (window.confirm('Switching to platform mode will remove your BYOK credentials. Continue?')) {
        deleteMutation.mutate();
      }
    } else {
      setSelectedMode(mode);
    }
  };

  const handleSaveBYOK = (data: TwilioConfigRequest) => {
    saveMutation.mutate(data);
  };

  const handleTest = (to: string) => {
    setTestResult(null);
    testMutation.mutate({ to_number: to });
  };

  if (configLoading) {
    return (
      <div className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="h-32 bg-gray-200 rounded"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-purple-50 to-blue-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg text-green-600">
              <WhatsAppIcon />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">WhatsApp & SMS</h3>
              <p className="text-sm text-gray-500">Configure messaging for your salon</p>
            </div>
          </div>
          {config && <StatusBadge status={config.status} />}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Mode Toggle */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Integration Mode
          </label>
          <ModeToggle
            mode={selectedMode}
            onChange={handleModeChange}
            disabled={saveMutation.isPending || deleteMutation.isPending}
          />
        </div>

        {/* Platform Mode Info */}
        {selectedMode === 'platform' && (
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-start gap-3">
                <span className="text-blue-600 mt-0.5"><InfoIcon /></span>
                <div>
                  <h4 className="font-medium text-blue-900">Platform Number</h4>
                  <p className="text-sm text-blue-700 mt-1">
                    Use our pre-configured WhatsApp Business API number for quick setup.
                    Messages will be sent from a shared platform number.
                  </p>
                </div>
              </div>
            </div>

            {status?.platform_whatsapp_number && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Platform WhatsApp Number:</span>{' '}
                  <span className="text-gray-900">{status.platform_whatsapp_number}</span>
                </p>
              </div>
            )}

            <div className="flex items-center gap-2 text-sm text-green-600">
              <CheckIcon />
              <span>Ready to send messages</span>
            </div>

            {/* Test Platform */}
            <div className="pt-4 border-t border-gray-200">
              <button
                onClick={() => {
                  const phone = prompt('Enter phone number to send test message (E.164 format):');
                  if (phone) handleTest(phone);
                }}
                className="px-4 py-2 border border-purple-600 text-purple-600 rounded-lg hover:bg-purple-50 transition-colors"
              >
                Send Test Message
              </button>
            </div>
          </div>
        )}

        {/* BYOK Form */}
        {selectedMode === 'byok' && (
          <div className="space-y-4">
            <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
              <div className="flex items-start gap-3">
                <span className="text-amber-600 mt-0.5"><InfoIcon /></span>
                <div>
                  <h4 className="font-medium text-amber-900">Bring Your Own Keys</h4>
                  <p className="text-sm text-amber-700 mt-1">
                    Use your own Twilio account for full control. You'll need your
                    Account SID, Auth Token, and a WhatsApp-enabled number.
                  </p>
                </div>
              </div>
            </div>

            <BYOKForm
              initialData={config?.mode === 'byok' ? config : undefined}
              onSubmit={handleSaveBYOK}
              onTest={handleTest}
              isLoading={saveMutation.isPending}
              testResult={testResult}
            />

            {/* Help Links */}
            <div className="pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-500 mb-2">Need help?</p>
              <div className="flex gap-4">
                <a
                  href="https://www.twilio.com/docs/usage/requests-to-twilios-api"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-purple-600 hover:text-purple-700 underline"
                >
                  Finding your credentials
                </a>
                <a
                  href="https://www.twilio.com/docs/whatsapp/api"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-purple-600 hover:text-purple-700 underline"
                >
                  WhatsApp setup guide
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Test Result */}
        {testResult && selectedMode === 'platform' && (
          <div className={`mt-4 p-4 rounded-lg ${testResult.success ? 'bg-green-50' : 'bg-red-50'}`}>
            <div className="flex items-center gap-2">
              {testResult.success ? (
                <span className="text-green-600"><CheckIcon /></span>
              ) : (
                <span className="text-red-600"><XIcon /></span>
              )}
              <span className={testResult.success ? 'text-green-800' : 'text-red-800'}>
                {testResult.message}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TwilioConfig;
