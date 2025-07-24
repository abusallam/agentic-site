import { defineConfig, devices } from '@playwright/test'

/**
 * Staging environment configuration for Playwright tests
 */
export default defineConfig({
  testDir: './tests/e2e/staging',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 3 : 1,
  workers: process.env.CI ? 2 : undefined,
  reporter: [['html'], ['junit', { outputFile: 'test-results/staging-results.xml' }]],
  
  use: {
    baseURL: process.env.STAGING_URL || 'https://staging.consulting.sa',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'staging-smoke',
      testMatch: '**/smoke/**/*.spec.ts',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'staging-critical',
      testMatch: '**/critical/**/*.spec.ts',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  timeout: 30000,
  expect: {
    timeout: 10000,
  },
})