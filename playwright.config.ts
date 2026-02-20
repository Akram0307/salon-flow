import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['list'],
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  actionTimeout: 10000,
    navigationTimeout: 30000,
  },
  projects: [
    // Client PWA tests
    {
      name: 'client-chrome',
      testMatch: /.*client.*\.spec\.ts/,
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'client-mobile',
      testMatch: /.*client.*\.spec\.ts/,
      use: { ...devices['iPhone 14'] },
    },
    // Staff PWA tests
    {
      name: 'staff-chrome',
      testMatch: /.*staff.*\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], baseURL: 'http://localhost:3001' },
    },
    // Manager PWA tests
    {
      name: 'manager-chrome',
      testMatch: /.*manager.*\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], baseURL: 'http://localhost:3002' },
    },
    // Owner PWA tests
    {
      name: 'owner-chrome',
      testMatch: /.*owner.*\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], baseURL: 'http://localhost:3003' },
    },
  ],
  webServer: [
    {
      command: 'npm run dev',
      url: 'http://localhost:3000',
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
    },
  ],
  outputDir: 'test-results/',
  timeout: 30000,
  expect: {
    timeout: 5000,
  },
});
