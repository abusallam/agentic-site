import { test, expect } from '@playwright/test'

test.describe('Basic Smoke Tests', () => {
  test('homepage loads successfully', async ({ page }) => {
    await page.goto('/')
    
    // Check that the page loads
    await expect(page).toHaveTitle(/consulting\.sa/i)
    
    // Check for main navigation
    await expect(page.locator('nav')).toBeVisible()
    
    // Check for main content
    await expect(page.locator('main')).toBeVisible()
  })

  test('health check endpoint responds', async ({ request }) => {
    const response = await request.get('/api/health')
    expect(response.status()).toBe(200)
    
    const data = await response.json()
    expect(data).toHaveProperty('status', 'ok')
  })

  test('navigation menu works', async ({ page }) => {
    await page.goto('/')
    
    // Test services navigation
    await page.click('text=Services')
    await expect(page).toHaveURL(/.*services/)
    
    // Test about navigation
    await page.goto('/')
    await page.click('text=About')
    await expect(page).toHaveURL(/.*about/)
  })

  test('contact form is accessible', async ({ page }) => {
    await page.goto('/contact')
    
    // Check form elements exist
    await expect(page.locator('input[name="name"]')).toBeVisible()
    await expect(page.locator('input[name="email"]')).toBeVisible()
    await expect(page.locator('textarea[name="message"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('responsive design works', async ({ page }) => {
    // Test desktop view
    await page.setViewportSize({ width: 1200, height: 800 })
    await page.goto('/')
    await expect(page.locator('nav')).toBeVisible()
    
    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')
    
    // Mobile menu should be present
    const mobileMenu = page.locator('[data-testid="mobile-menu"]')
    if (await mobileMenu.isVisible()) {
      await expect(mobileMenu).toBeVisible()
    }
  })
})