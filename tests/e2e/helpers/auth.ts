import { Page, expect } from '@playwright/test';

export interface TestUser {
  email: string;
  password: string;
}

export const GCP_TEST_USER: TestUser = {
  email: 'e2e_test@salonflow.com',
  password: 'TestPass123!'
};

export async function loginWithGCP(page: Page, user: TestUser = GCP_TEST_USER): Promise<void> {
  await page.goto('/login');
  
  // Wait for login form to be visible using accessible selectors
  await expect(page.getByRole('heading', { name: 'Welcome back' })).toBeVisible({ timeout: 10000 });
  
  // Fill login form using accessible selectors
  await page.getByPlaceholder('you@example.com').fill(user.email);
  await page.getByPlaceholder('••••••••').fill(user.password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  
  // Wait for dashboard to load - URL change indicates successful login
  await page.waitForURL('/dashboard', { timeout: 15000 });
  
  // Wait for dashboard content to be visible - check for main heading with longer timeout
  await expect(page.getByRole('heading', { name: /Salon Owner|Dashboard|Welcome/ })).toBeVisible({ timeout: 10000 });
}

export async function getGCPAuthToken(user: TestUser = GCP_TEST_USER): Promise<string> {
  // Use the correct production API URL from memories
  const response = await fetch('https://salon-flow-api-687369167038.asia-south1.run.app/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: user.email, password: user.password })
  });
  if (!response.ok) throw new Error(`Auth failed: ${response.status}`);
  const data = await response.json();
  return data.access_token;
}

export async function setAuthToken(page: Page, token: string): Promise<void> {
  await page.addInitScript((authToken) => {
    localStorage.setItem('salon_flow_token', authToken);
  }, token);
}
