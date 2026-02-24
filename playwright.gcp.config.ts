import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for testing against GCP production
 * Tests the deployed Owner PWA directly against live backend services
 */
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 1,
  workers: 1,
  reporter: [['list'], ['html', { outputFolder: 'playwright-report-gcp' }]],
  
  use: {
    // Production deployed PWA URL (WORKING - alternate)
    baseURL: 'https://salon-flow-owner-687369167038.asia-south1.run.app',
    
    // GCP Backend API
    apiBaseURL: 'https://salon-flow-api-687369167038.asia-south1.run.app/api/v1',
    
    // Test credentials for E2E
    testUser: {
      email: 'e2e_test@salonflow.com',
      password: 'TestPass123!'
    },
    
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
    actionTimeout: 15000,
    navigationTimeout: 30000,
    
    // Browser context options
    contextOptions: {
      viewport: { width: 1280, height: 720 },
    },
  },

  projects: [
    {
      name: 'chromium-gcp',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: ['--disable-web-security', '--disable-features=IsolateOrigins,site-per-process']
        }
      },
    },
    {
      name: 'chromium-mobile-gcp',
      use: {
        ...devices['Pixel 5'],
        launchOptions: {
          args: ['--disable-web-security']
        }
      },
    },
  ],

  // No local dev server - testing production deployment directly
});
