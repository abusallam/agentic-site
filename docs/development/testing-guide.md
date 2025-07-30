# Testing and Validation Guide

## Overview

This comprehensive testing guide covers all aspects of testing and validation for the Agentic AI Platform, including unit tests, integration tests, end-to-end tests, performance testing, and deployment validation procedures.

## Testing Architecture

### Testing Pyramid
```
                    E2E Tests
                   /         \
                  /           \
                 /             \
            Integration Tests
           /                   \
          /                     \
         /                       \
    Unit Tests                Unit Tests
   (Frontend)                (Backend)
```

### Test Types and Coverage

#### Unit Tests (70% of tests)
- **Frontend**: Component testing, utility functions
- **Backend**: Service classes, agent logic, utilities
- **Coverage Target**: >80% code coverage

#### Integration Tests (20% of tests)
- **API Integration**: Service-to-service communication
- **Database Integration**: Data persistence and retrieval
- **External Services**: Third-party API integration

#### End-to-End Tests (10% of tests)
- **User Workflows**: Complete user journeys
- **Cross-browser Testing**: Multiple browser compatibility
- **Mobile Responsiveness**: Mobile device testing

## Frontend Testing

### Testing Stack
- **Test Runner**: Jest 30.0.5
- **Testing Library**: React Testing Library
- **E2E Testing**: Playwright 1.40.0
- **Mocking**: Jest mocks and MSW
- **Coverage**: Jest coverage reports

### Unit Testing

#### Component Testing Example
```typescript
// frontend/components/__tests__/chatbot.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Chatbot } from '../chatbot/chatbot';

describe('Chatbot Component', () => {
  it('should render chatbot interface', () => {
    render(<Chatbot />);
    
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  it('should send message when form is submitted', async () => {
    const mockSendMessage = jest.fn();
    render(<Chatbot onSendMessage={mockSendMessage} />);
    
    const input = screen.getByRole('textbox');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    fireEvent.change(input, { target: { value: 'Hello, AI!' } });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalledWith('Hello, AI!');
    });
  });

  it('should display AI response', async () => {
    render(<Chatbot />);
    
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.submit(input.closest('form')!);
    
    await waitFor(() => {
      expect(screen.getByText(/ai response/i)).toBeInTheDocument();
    });
  });
});
```

#### Utility Function Testing
```typescript
// frontend/lib/__tests__/utils.test.ts
import { formatCurrency, validateEmail, debounce } from '../utils';

describe('Utility Functions', () => {
  describe('formatCurrency', () => {
    it('should format currency correctly', () => {
      expect(formatCurrency(1234.56)).toBe('$1,234.56');
      expect(formatCurrency(0)).toBe('$0.00');
      expect(formatCurrency(-100)).toBe('-$100.00');
    });
  });

  describe('validateEmail', () => {
    it('should validate email addresses', () => {
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('invalid-email')).toBe(false);
      expect(validateEmail('')).toBe(false);
    });
  });

  describe('debounce', () => {
    jest.useFakeTimers();
    
    it('should debounce function calls', () => {
      const mockFn = jest.fn();
      const debouncedFn = debounce(mockFn, 100);
      
      debouncedFn();
      debouncedFn();
      debouncedFn();
      
      expect(mockFn).not.toHaveBeenCalled();
      
      jest.advanceTimersByTime(100);
      
      expect(mockFn).toHaveBeenCalledTimes(1);
    });
  });
});
```

### Integration Testing

#### API Integration Testing
```typescript
// frontend/__tests__/api-integration.test.ts
import { render, screen, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { UserProfile } from '../components/user-profile';

const server = setupServer(
  rest.get('/api/user/profile', (req, res, ctx) => {
    return res(ctx.json({
      id: '1',
      name: 'John Doe',
      email: 'john@example.com'
    }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('API Integration', () => {
  it('should fetch and display user profile', async () => {
    render(<UserProfile userId="1" />);
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('john@example.com')).toBeInTheDocument();
    });
  });

  it('should handle API errors gracefully', async () => {
    server.use(
      rest.get('/api/user/profile', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );
    
    render(<UserProfile userId="1" />);
    
    await waitFor(() => {
      expect(screen.getByText(/error loading profile/i)).toBeInTheDocument();
    });
  });
});
```

### End-to-End Testing

#### Playwright E2E Tests
```typescript
// frontend/tests/e2e/chatbot.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Chatbot Functionality', () => {
  test('should complete full conversation flow', async ({ page }) => {
    await page.goto('/');
    
    // Open chatbot
    await page.click('[data-testid="chatbot-trigger"]');
    await expect(page.locator('[data-testid="chatbot-window"]')).toBeVisible();
    
    // Send message
    await page.fill('[data-testid="chat-input"]', 'Hello, I need help with pricing');
    await page.click('[data-testid="send-button"]');
    
    // Wait for AI response
    await expect(page.locator('[data-testid="ai-message"]')).toBeVisible();
    
    // Verify response contains pricing information
    const response = await page.textContent('[data-testid="ai-message"]');
    expect(response).toContain('pricing');
  });

  test('should handle live agent handoff', async ({ page }) => {
    await page.goto('/');
    
    // Start conversation
    await page.click('[data-testid="chatbot-trigger"]');
    await page.fill('[data-testid="chat-input"]', 'I need to speak with a human agent');
    await page.click('[data-testid="send-button"]');
    
    // Should show handoff option
    await expect(page.locator('[data-testid="live-agent-button"]')).toBeVisible();
    
    // Click live agent button
    await page.click('[data-testid="live-agent-button"]');
    
    // Should redirect to live chat
    await expect(page.locator('[data-testid="live-chat-interface"]')).toBeVisible();
  });
});
```

#### Cross-browser Testing
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'https://dev.consulting.sa',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
});
```

### Frontend Testing Commands

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run e2e

# Run E2E tests with UI
npm run e2e:ui

# Run specific test file
npm test -- chatbot.test.tsx

# Run tests matching pattern
npm test -- --testNamePattern="should render"
```

## Backend Testing

### Testing Stack
- **Test Runner**: pytest 7.0.0+
- **Async Testing**: pytest-asyncio
- **Mocking**: pytest-mock, unittest.mock
- **Coverage**: pytest-cov
- **Fixtures**: pytest fixtures

### Unit Testing

#### Service Class Testing
```python
# backend/agent/tests/test_supabase_service.py
import pytest
from unittest.mock import AsyncMock, patch
from my_adk_agent.services.supabase_service import SupabaseService

@pytest.fixture
def supabase_service():
    config = {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key'
    }
    return SupabaseService(config)

@pytest.mark.asyncio
async def test_create_user(supabase_service):
    """Test user creation functionality."""
    user_data = {
        'email': 'test@example.com',
        'name': 'Test User'
    }
    
    with patch.object(supabase_service.client, 'table') as mock_table:
        mock_table.return_value.insert.return_value.execute.return_value = {
            'data': [{'id': '123', **user_data}],
            'error': None
        }
        
        result = await supabase_service.create_user(user_data)
        
        assert result['id'] == '123'
        assert result['email'] == 'test@example.com'
        mock_table.assert_called_with('users')

@pytest.mark.asyncio
async def test_create_user_error_handling(supabase_service):
    """Test error handling in user creation."""
    user_data = {'email': 'invalid-email'}
    
    with patch.object(supabase_service.client, 'table') as mock_table:
        mock_table.return_value.insert.return_value.execute.return_value = {
            'data': None,
            'error': {'message': 'Invalid email format'}
        }
        
        with pytest.raises(ValueError, match='Invalid email format'):
            await supabase_service.create_user(user_data)
```

#### Agent Logic Testing
```python
# backend/agent/tests/test_agent.py
import pytest
from unittest.mock import AsyncMock, patch
from my_adk_agent.agent import MyAgent

@pytest.fixture
def agent():
    return MyAgent()

@pytest.mark.asyncio
async def test_process_customer_inquiry(agent):
    """Test customer inquiry processing."""
    inquiry = {
        'message': 'I need help with pricing',
        'user_id': 'user123'
    }
    
    with patch.object(agent, 'gemini_service') as mock_gemini:
        mock_gemini.generate_response.return_value = {
            'response': 'Here are our pricing options...',
            'intent': 'pricing_inquiry'
        }
        
        result = await agent.process_inquiry(inquiry)
        
        assert 'response' in result
        assert 'pricing options' in result['response']
        assert result['intent'] == 'pricing_inquiry'

@pytest.mark.asyncio
async def test_live_agent_handoff(agent):
    """Test live agent handoff functionality."""
    request = {
        'message': 'I need to speak with a human',
        'user_id': 'user123'
    }
    
    with patch.object(agent, 'livekit_service') as mock_livekit:
        mock_livekit.create_room.return_value = {
            'room_id': 'room123',
            'token': 'token123'
        }
        
        result = await agent.initiate_handoff(request)
        
        assert result['type'] == 'live_handoff'
        assert 'room_id' in result
        assert 'token' in result
```

### Integration Testing

#### Database Integration
```python
# backend/agent/tests/integration/test_database_integration.py
import pytest
import asyncio
from my_adk_agent.services.supabase_service import SupabaseService

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_user_workflow():
    """Test complete user creation and retrieval workflow."""
    service = SupabaseService({
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key'
    })
    
    # Create user
    user_data = {
        'email': 'integration@test.com',
        'name': 'Integration Test User'
    }
    
    created_user = await service.create_user(user_data)
    assert created_user['email'] == user_data['email']
    
    # Retrieve user
    retrieved_user = await service.get_user(created_user['id'])
    assert retrieved_user['id'] == created_user['id']
    
    # Update user
    update_data = {'name': 'Updated Name'}
    updated_user = await service.update_user(created_user['id'], update_data)
    assert updated_user['name'] == 'Updated Name'
    
    # Delete user (cleanup)
    await service.delete_user(created_user['id'])
```

#### External Service Integration
```python
# backend/agent/tests/integration/test_external_services.py
import pytest
from my_adk_agent.services.stripe_service import StripeService

@pytest.mark.integration
@pytest.mark.asyncio
async def test_stripe_payment_flow():
    """Test Stripe payment processing integration."""
    stripe_service = StripeService({
        'STRIPE_SECRET_KEY': 'sk_test_...'
    })
    
    # Create payment intent
    payment_data = {
        'amount': 2000,  # $20.00
        'currency': 'usd',
        'customer_email': 'test@example.com'
    }
    
    payment_intent = await stripe_service.create_payment_intent(payment_data)
    
    assert payment_intent['amount'] == 2000
    assert payment_intent['currency'] == 'usd'
    assert payment_intent['status'] == 'requires_payment_method'
    
    # Simulate payment confirmation
    confirmed_payment = await stripe_service.confirm_payment(
        payment_intent['id'],
        'pm_card_visa'  # Test payment method
    )
    
    assert confirmed_payment['status'] == 'succeeded'
```

### Backend Testing Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=my_adk_agent

# Run specific test file
pytest tests/test_agent.py

# Run tests with specific marker
pytest -m integration

# Run tests in verbose mode
pytest -v

# Run tests and generate HTML coverage report
pytest --cov=my_adk_agent --cov-report=html

# Run tests in parallel
pytest -n auto
```

## Performance Testing

### Frontend Performance Testing

#### Lighthouse CI
```javascript
// frontend/scripts/performance-test.js
const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');

async function runLighthouse(url) {
  const chrome = await chromeLauncher.launch({chromeFlags: ['--headless']});
  const options = {
    logLevel: 'info',
    output: 'html',
    onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
    port: chrome.port,
  };
  
  const runnerResult = await lighthouse(url, options);
  
  // Performance thresholds
  const scores = runnerResult.lhr.categories;
  const performance = scores.performance.score * 100;
  const accessibility = scores.accessibility.score * 100;
  
  console.log(`Performance Score: ${performance}`);
  console.log(`Accessibility Score: ${accessibility}`);
  
  // Assert minimum scores
  if (performance < 90) {
    throw new Error(`Performance score ${performance} below threshold of 90`);
  }
  
  if (accessibility < 95) {
    throw new Error(`Accessibility score ${accessibility} below threshold of 95`);
  }
  
  await chrome.kill();
}

// Run performance tests
runLighthouse('https://dev.consulting.sa').catch(console.error);
```

#### Bundle Size Analysis
```bash
# Analyze bundle size
npm run analyze

# Check for large dependencies
npx webpack-bundle-analyzer build/static/js/*.js
```

### Backend Performance Testing

#### Load Testing with pytest-benchmark
```python
# backend/agent/tests/performance/test_agent_performance.py
import pytest
from my_adk_agent.agent import MyAgent

@pytest.fixture
def agent():
    return MyAgent()

def test_inquiry_processing_performance(benchmark, agent):
    """Benchmark inquiry processing performance."""
    inquiry = {
        'message': 'What are your pricing options?',
        'user_id': 'test_user'
    }
    
    # Benchmark the function
    result = benchmark(agent.process_inquiry_sync, inquiry)
    
    # Assert performance requirements
    assert benchmark.stats.mean < 0.1  # Less than 100ms average
    assert result is not None

@pytest.mark.asyncio
async def test_concurrent_requests(agent):
    """Test handling multiple concurrent requests."""
    import asyncio
    
    inquiries = [
        {'message': f'Question {i}', 'user_id': f'user{i}'}
        for i in range(100)
    ]
    
    start_time = asyncio.get_event_loop().time()
    
    # Process all inquiries concurrently
    results = await asyncio.gather(*[
        agent.process_inquiry(inquiry) for inquiry in inquiries
    ])
    
    end_time = asyncio.get_event_loop().time()
    total_time = end_time - start_time
    
    # Should handle 100 requests in under 5 seconds
    assert total_time < 5.0
    assert len(results) == 100
    assert all(result is not None for result in results)
```

## Deployment Validation

### Pre-Deployment Testing

#### Development Environment Validation
```bash
#!/bin/bash
# scripts/validate-development.sh

echo "=== Development Environment Validation ==="

# 1. Health Checks
echo "1. Running health checks..."
curl -f https://dev.consulting.sa/api/health || exit 1
curl -f https://dev.consulting.sa:8001/health || exit 1

# 2. Frontend Tests
echo "2. Running frontend tests..."
cd frontend
npm test -- --watchAll=false --coverage || exit 1

# 3. Backend Tests
echo "3. Running backend tests..."
cd ../backend/agent
pytest --cov=my_adk_agent || exit 1

# 4. E2E Tests
echo "4. Running E2E tests..."
cd ../../frontend
npm run e2e || exit 1

# 5. Performance Tests
echo "5. Running performance tests..."
node scripts/performance-test.js || exit 1

echo "✅ All validation checks passed!"
```

#### Production Readiness Checklist
```bash
#!/bin/bash
# scripts/production-readiness-check.sh

echo "=== Production Readiness Check ==="

# Security checks
echo "1. Security audit..."
npm audit --audit-level high || exit 1

# Build verification
echo "2. Production build test..."
cd frontend
npm run build || exit 1

# Environment validation
echo "3. Environment configuration check..."
if [ -z "$SUPABASE_SERVICE_KEY" ]; then
  echo "❌ Missing SUPABASE_SERVICE_KEY"
  exit 1
fi

if [ -z "$STRIPE_SECRET_KEY" ]; then
  echo "❌ Missing STRIPE_SECRET_KEY"
  exit 1
fi

# SSL certificate check
echo "4. SSL certificate validation..."
openssl x509 -in /etc/ssl/certs/consulting.sa.crt -noout -checkend 2592000 || {
  echo "❌ SSL certificate expires within 30 days"
  exit 1
}

echo "✅ Production readiness check passed!"
```

### Post-Deployment Validation

#### Automated Smoke Tests
```bash
#!/bin/bash
# scripts/smoke-tests.sh

ENVIRONMENT=${1:-development}
BASE_URL=${2:-https://dev.consulting.sa}

echo "=== Smoke Tests for $ENVIRONMENT ==="

# 1. Basic connectivity
echo "1. Testing basic connectivity..."
curl -f "$BASE_URL" || exit 1

# 2. API health
echo "2. Testing API health..."
curl -f "$BASE_URL/api/health" || exit 1

# 3. Authentication endpoints
echo "3. Testing authentication..."
curl -f "$BASE_URL/api/auth/status" || exit 1

# 4. Database connectivity
echo "4. Testing database connectivity..."
curl -f "$BASE_URL/api/db/health" || exit 1

# 5. External service integration
echo "5. Testing external services..."
curl -f "$BASE_URL/api/services/status" || exit 1

echo "✅ All smoke tests passed!"
```

#### Comprehensive Integration Tests
```typescript
// tests/integration/post-deployment.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Post-Deployment Integration Tests', () => {
  test('should complete full user journey', async ({ page }) => {
    // 1. Visit homepage
    await page.goto('/');
    await expect(page).toHaveTitle(/Agentic AI Platform/);
    
    // 2. Test chatbot functionality
    await page.click('[data-testid="chatbot-trigger"]');
    await page.fill('[data-testid="chat-input"]', 'Hello, I need pricing information');
    await page.click('[data-testid="send-button"]');
    
    // 3. Verify AI response
    await expect(page.locator('[data-testid="ai-message"]')).toBeVisible();
    
    // 4. Test contact form
    await page.goto('/contact');
    await page.fill('[name="name"]', 'Test User');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="message"]', 'Test message');
    await page.click('[type="submit"]');
    
    // 5. Verify form submission
    await expect(page.locator('.success-message')).toBeVisible();
  });

  test('should handle error scenarios gracefully', async ({ page }) => {
    // Test 404 page
    await page.goto('/non-existent-page');
    await expect(page.locator('h1')).toContainText('404');
    
    // Test API error handling
    await page.route('/api/test-error', route => {
      route.fulfill({ status: 500, body: 'Server Error' });
    });
    
    await page.goto('/test-error-page');
    await expect(page.locator('.error-message')).toBeVisible();
  });
});
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: cd frontend && npm ci
      
      - name: Run tests
        run: cd frontend && npm test -- --coverage --watchAll=false
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: frontend/coverage/lcov.info

  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          cd backend/agent
          pip install uv
          uv pip install -e .
          uv pip install pytest pytest-cov pytest-asyncio
      
      - name: Run tests
        run: cd backend/agent && pytest --cov=my_adk_agent --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: backend/agent/coverage.xml

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: cd frontend && npm ci
      
      - name: Install Playwright
        run: cd frontend && npx playwright install
      
      - name: Run E2E tests
        run: cd frontend && npm run e2e
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

## Test Data Management

### Test Fixtures

#### Frontend Test Data
```typescript
// frontend/tests/fixtures/test-data.ts
export const mockUser = {
  id: '123',
  name: 'Test User',
  email: 'test@example.com',
  role: 'customer'
};

export const mockChatMessages = [
  {
    id: '1',
    message: 'Hello, I need help',
    sender: 'user',
    timestamp: '2025-01-28T10:00:00Z'
  },
  {
    id: '2',
    message: 'How can I assist you today?',
    sender: 'ai',
    timestamp: '2025-01-28T10:00:05Z'
  }
];

export const mockApiResponses = {
  userProfile: {
    data: mockUser,
    error: null
  },
  chatResponse: {
    response: 'I can help you with that!',
    intent: 'general_inquiry'
  }
};
```

#### Backend Test Data
```python
# backend/agent/tests/fixtures/test_data.py
import pytest

@pytest.fixture
def sample_user():
    return {
        'id': '123',
        'email': 'test@example.com',
        'name': 'Test User',
        'created_at': '2025-01-28T10:00:00Z'
    }

@pytest.fixture
def sample_inquiry():
    return {
        'message': 'I need help with pricing',
        'user_id': '123',
        'timestamp': '2025-01-28T10:00:00Z'
    }

@pytest.fixture
def mock_gemini_response():
    return {
        'response': 'Here are our pricing options...',
        'intent': 'pricing_inquiry',
        'confidence': 0.95
    }
```

## Quality Gates

### Code Quality Metrics

#### Coverage Requirements
- **Frontend**: Minimum 80% code coverage
- **Backend**: Minimum 85% code coverage
- **Integration**: Minimum 70% coverage
- **E2E**: Cover all critical user paths

#### Performance Requirements
- **Page Load Time**: < 3 seconds
- **API Response Time**: < 100ms (95th percentile)
- **Bundle Size**: < 500KB gzipped
- **Lighthouse Score**: > 90 for all categories

#### Security Requirements
- **Vulnerability Scan**: Zero high/critical vulnerabilities
- **Dependency Audit**: All dependencies up to date
- **SSL Grade**: A+ rating
- **OWASP Compliance**: Pass all OWASP top 10 checks

### Automated Quality Checks

```bash
#!/bin/bash
# scripts/quality-gate.sh

echo "=== Quality Gate Checks ==="

# 1. Code coverage
echo "1. Checking code coverage..."
cd frontend && npm test -- --coverage --watchAll=false
FRONTEND_COVERAGE=$(grep -o '"lines":{"pct":[0-9.]*' coverage/coverage-summary.json | cut -d: -f3)
if (( $(echo "$FRONTEND_COVERAGE < 80" | bc -l) )); then
  echo "❌ Frontend coverage $FRONTEND_COVERAGE% below 80%"
  exit 1
fi

cd ../backend/agent && pytest --cov=my_adk_agent --cov-report=term-missing
BACKEND_COVERAGE=$(pytest --cov=my_adk_agent --cov-report=term | grep TOTAL | awk '{print $4}' | sed 's/%//')
if (( $(echo "$BACKEND_COVERAGE < 85" | bc -l) )); then
  echo "❌ Backend coverage $BACKEND_COVERAGE% below 85%"
  exit 1
fi

# 2. Security audit
echo "2. Running security audit..."
cd ../../frontend && npm audit --audit-level high

# 3. Performance check
echo "3. Running performance tests..."
node scripts/performance-test.js

# 4. Linting
echo "4. Running linting checks..."
npm run lint
cd ../backend/agent && flake8 my_adk_agent/

echo "✅ All quality gates passed!"
```

## Best Practices

### Testing Best Practices

#### ✅ Do's
- Write tests before or alongside code (TDD/BDD)
- Use descriptive test names that explain the scenario
- Keep tests independent and isolated
- Use appropriate test doubles (mocks, stubs, fakes)
- Test edge cases and error conditions
- Maintain test data fixtures
- Run tests in CI/CD pipeline
- Monitor test performance and flakiness

#### ❌ Don'ts
- Don't test implementation details
- Don't write tests that depend on external services in unit tests
- Don't ignore failing tests
- Don't write overly complex tests
- Don't test third-party library functionality
- Don't commit code without tests
- Don't skip integration and E2E tests

### Test Organization

#### File Structure
```
frontend/
├── __tests__/           # Global test utilities
├── components/
│   └── __tests__/       # Component tests
├── lib/
│   └── __tests__/       # Utility tests
├── tests/
│   ├── e2e/            # End-to-end tests
│   ├── integration/    # Integration tests
│   └── fixtures/       # Test data
└── jest.config.js      # Jest configuration

backend/agent/
├── tests/
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   ├── performance/    # Performance tests
│   └── fixtures/       # Test data
├── conftest.py         # Pytest configuration
└── pytest.ini         # Pytest settings
```

## Conclusion

This comprehensive testing guide ensures:

- **Quality Assurance**: Thorough testing at all levels
- **Reliability**: Consistent and predictable application behavior
- **Performance**: Optimal application performance
- **Security**: Secure application deployment
- **Maintainability**: Easy to maintain and extend test suites
- **Confidence**: High confidence in deployments

Follow these testing practices to maintain a robust, reliable, and high-quality application.