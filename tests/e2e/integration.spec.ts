/**
 * Integration Tests - Cross-Service Testing
 * Tests the full flow across all Salon Flow services
 */
import { test, expect } from '@playwright/test';

// Service URLs from verified deployment
const SERVICES = {
  api: 'https://salon-flow-api-rgvcleapsa-el.a.run.app',
  ai: 'https://salon-flow-ai-rgvcleapsa-el.a.run.app',
  notification: 'https://salon-flow-notification-rgvcleapsa-el.a.run.app',
  owner: 'https://salon-flow-owner-rgvcleapsa-el.a.run.app',
  manager: 'https://salon-flow-manager-rgvcleapsa-el.a.run.app',
};

test.describe('Cross-Service Integration Tests', () => {
  
  test.describe('Service Health Checks', () => {
    test('Backend API should be healthy', async ({ request }) => {
      const response = await request.get(`${SERVICES.api}/health/`);
      expect(response.ok()).toBeTruthy();
      const body = await response.json();
      expect(body.status).toBe('healthy');
    });

    test('AI Service should be healthy', async ({ request }) => {
      const response = await request.get(`${SERVICES.ai}/health`);
      expect(response.ok()).toBeTruthy();
    });

    test('Notification Service should be healthy', async ({ request }) => {
      const response = await request.get(`${SERVICES.notification}/health`);
      expect(response.ok()).toBeTruthy();
    });

    test('Owner PWA should be accessible', async ({ request }) => {
      const response = await request.get(SERVICES.owner);
      expect(response.ok()).toBeTruthy();
    });

    test('Manager PWA should be accessible', async ({ request }) => {
      const response = await request.get(SERVICES.manager);
      expect(response.ok()).toBeTruthy();
    });
  });

  test.describe('API Documentation', () => {
    test('Backend API docs should be accessible', async ({ request }) => {
      const response = await request.get(`${SERVICES.api}/docs`);
      expect(response.ok()).toBeTruthy();
    });

    test('AI Service docs should be accessible', async ({ request }) => {
      const response = await request.get(`${SERVICES.ai}/docs`);
      expect(response.ok()).toBeTruthy();
    });
  });

  test.describe('CORS Configuration', () => {
    test('API should allow Owner PWA origin', async ({ request }) => {
      const response = await request.fetch(`${SERVICES.api}/health/`, {
        method: 'OPTIONS',
        headers: {
          'Origin': SERVICES.owner,
          'Access-Control-Request-Method': 'GET'
        }
      });
      const allowOrigin = response.headers()['access-control-allow-origin'];
      expect(allowOrigin).toBeTruthy();
    });

    test('API should allow Manager PWA origin', async ({ request }) => {
      const response = await request.fetch(`${SERVICES.api}/health/`, {
        method: 'OPTIONS',
        headers: {
          'Origin': SERVICES.manager,
          'Access-Control-Request-Method': 'GET'
        }
      });
      const allowOrigin = response.headers()['access-control-allow-origin'];
      expect(allowOrigin).toBeTruthy();
    });

    test('AI Service should allow API origin', async ({ request }) => {
      const response = await request.fetch(`${SERVICES.ai}/health`, {
        method: 'OPTIONS',
        headers: {
          'Origin': SERVICES.api,
          'Access-Control-Request-Method': 'GET'
        }
      });
      const allowOrigin = response.headers()['access-control-allow-origin'];
      expect(allowOrigin).toBeTruthy();
    });
  });

  test.describe('AI Agent Integration', () => {
    test('AI Service should list available agents', async ({ request }) => {
      const response = await request.get(`${SERVICES.ai}/api/v1/agents`);
      expect(response.ok()).toBeTruthy();
      const body = await response.json();
      expect(body.agents).toBeDefined();
      expect(body.count).toBeGreaterThan(0);
    });

    test('AI Service should have Booking Agent', async ({ request }) => {
      const response = await request.get(`${SERVICES.ai}/api/v1/agents`);
      const body = await response.json();
      const agentNames = body.agents.map((a: any) => a.name);
      expect(agentNames).toContain('Booking Agent');
    });

    test('AI Service should have Marketing Agent', async ({ request }) => {
      const response = await request.get(`${SERVICES.ai}/api/v1/agents`);
      const body = await response.json();
      const agentNames = body.agents.map((a: any) => a.name);
      expect(agentNames).toContain('Marketing Agent');
    });

    test('AI Service should have Analytics Agent', async ({ request }) => {
      const response = await request.get(`${SERVICES.ai}/api/v1/agents`);
      const body = await response.json();
      const agentNames = body.agents.map((a: any) => a.name);
      expect(agentNames).toContain('Analytics Agent');
    });
  });

  test.describe('End-to-End Flow Simulation', () => {
    test('Full service chain should be operational', async ({ request }) => {
      // 1. Check API health
      const apiHealth = await request.get(`${SERVICES.api}/health/`);
      expect(apiHealth.ok()).toBeTruthy();
      
      // 2. Check AI service health
      const aiHealth = await request.get(`${SERVICES.ai}/health`);
      expect(aiHealth.ok()).toBeTruthy();
      
      // 3. Check notification service health
      const notifHealth = await request.get(`${SERVICES.notification}/health`);
      expect(notifHealth.ok()).toBeTruthy();
      
      // 4. Verify PWAs are accessible
      const ownerResponse = await request.get(SERVICES.owner);
      expect(ownerResponse.ok()).toBeTruthy();
      
      const managerResponse = await request.get(SERVICES.manager);
      expect(managerResponse.ok()).toBeTruthy();
    });
  });

  test.describe('Performance Benchmarks', () => {
    test('API health check should respond quickly', async ({ request }) => {
      const startTime = Date.now();
      await request.get(`${SERVICES.api}/health/`);
      const responseTime = Date.now() - startTime;
      expect(responseTime).toBeLessThan(5000); // 5 seconds max
    });

    test('AI service health check should respond quickly', async ({ request }) => {
      const startTime = Date.now();
      await request.get(`${SERVICES.ai}/health`);
      const responseTime = Date.now() - startTime;
      expect(responseTime).toBeLessThan(5000);
    });

    test('Owner PWA should load quickly', async ({ request }) => {
      const startTime = Date.now();
      await request.get(SERVICES.owner);
      const responseTime = Date.now() - startTime;
      expect(responseTime).toBeLessThan(10000); // 10 seconds max for cold start
    });

    test('Manager PWA should load quickly', async ({ request }) => {
      const startTime = Date.now();
      await request.get(SERVICES.manager);
      const responseTime = Date.now() - startTime;
      expect(responseTime).toBeLessThan(10000);
    });
  });
});
