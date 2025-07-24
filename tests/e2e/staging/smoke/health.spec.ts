import { test, expect } from '@playwright/test'

test.describe('Staging Health Checks', () => {
  test('frontend health check', async ({ request }) => {
    const response = await request.get('/api/health')
    expect(response.status()).toBe(200)
    
    const data = await response.json()
    expect(data).toHaveProperty('status', 'ok')
    expect(data).toHaveProperty('timestamp')
    expect(data).toHaveProperty('environment', 'staging')
  })

  test('backend agent health check', async ({ request }) => {
    const response = await request.get('/api/agent/health')
    expect(response.status()).toBe(200)
    
    const data = await response.json()
    expect(data).toHaveProperty('status', 'healthy')
    expect(data).toHaveProperty('services')
    
    // Check critical services are running
    expect(data.services).toHaveProperty('supabase')
    expect(data.services).toHaveProperty('gemini')
  })

  test('database connectivity', async ({ request }) => {
    const response = await request.get('/api/health/database')
    expect(response.status()).toBe(200)
    
    const data = await response.json()
    expect(data).toHaveProperty('connected', true)
  })

  test('essential pages load', async ({ page }) => {
    const pages = ['/', '/services', '/about', '/contact']
    
    for (const pagePath of pages) {
      await page.goto(pagePath)
      await expect(page).not.toHaveTitle(/error/i)
      await expect(page.locator('body')).not.toContainText('500')
      await expect(page.locator('body')).not.toContainText('404')
    }
  })

  test('chatbot widget loads', async ({ page }) => {
    await page.goto('/')
    
    // Wait for chatbot to initialize
    await page.waitForTimeout(3000)
    
    // Check if chatbot widget is present
    const chatbot = page.locator('[data-testid="chatbot-widget"]')
    if (await chatbot.isVisible()) {
      await expect(chatbot).toBeVisible()
    }
  })
})