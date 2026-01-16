# Test Examples and Patterns

## Unit Test (Jest/Vitest)

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { UserService } from './user.service';
import { UserRepository } from './user.repository';

describe('UserService', () => {
  let userService: UserService;
  let mockRepository: UserRepository;

  beforeEach(() => {
    mockRepository = {
      findById: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
    } as unknown as UserRepository;
    userService = new UserService(mockRepository);
  });

  describe('findById', () => {
    it('should return user when found', async () => {
      const mockUser = { id: '1', email: 'test@example.com' };
      vi.mocked(mockRepository.findById).mockResolvedValue(mockUser);

      const result = await userService.findById('1');

      expect(result).toEqual(mockUser);
      expect(mockRepository.findById).toHaveBeenCalledWith('1');
    });

    it('should return null when user not found', async () => {
      vi.mocked(mockRepository.findById).mockResolvedValue(null);
      const result = await userService.findById('999');
      expect(result).toBeNull();
    });

    it('should throw error on repository failure', async () => {
      vi.mocked(mockRepository.findById).mockRejectedValue(new Error('DB error'));
      await expect(userService.findById('1')).rejects.toThrow('DB error');
    });
  });
});
```

## React Component Test

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

## Integration Test (API)

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import request from 'supertest';
import { app } from '../src/app';
import { setupTestDatabase, teardownTestDatabase } from './helpers';

describe('User API', () => {
  beforeAll(async () => { await setupTestDatabase(); });
  afterAll(async () => { await teardownTestDatabase(); });

  describe('POST /api/users', () => {
    it('creates a new user', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({ email: 'new@example.com', password: 'password123', name: 'Test User' })
        .expect(201);

      expect(response.body).toMatchObject({ email: 'new@example.com', name: 'Test User' });
      expect(response.body.password).toBeUndefined();
    });

    it('returns 400 for invalid email', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({ email: 'invalid-email', password: 'password123' })
        .expect(400);
      expect(response.body.error).toContain('email');
    });
  });
});
```

## E2E Test (Playwright)

```typescript
import { test, expect } from '@playwright/test';

test.describe('User Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('displays user information', async ({ page }) => {
    await expect(page.locator('[data-testid="user-name"]')).toContainText('Test User');
  });

  test('logs out successfully', async ({ page }) => {
    await page.click('[data-testid="logout-button"]');
    await expect(page).toHaveURL('/login');
  });
});
```

## AAA Pattern Structure

```typescript
it('should do something', async () => {
  // Arrange - Set up test data and mocks
  const input = { email: 'test@example.com' };
  mockRepository.findByEmail.mockResolvedValue(null);

  // Act - Execute the code being tested
  const result = await userService.create(input);

  // Assert - Verify the expected outcome
  expect(result).toBeDefined();
  expect(mockRepository.create).toHaveBeenCalledWith(input);
});
```

## Mocking Strategies

```typescript
// Mock external dependencies
vi.mock('./external-api', () => ({ fetchData: vi.fn() }));

// Mock specific return values
vi.mocked(externalApi.fetchData).mockResolvedValue({ data: 'test' });

// Spy on internal methods
const spy = vi.spyOn(userService, 'validate');
```

## Test File Structure

```
src/
├── services/
│   ├── user.service.ts
│   └── __tests__/
│       └── user.service.test.ts
├── components/
│   ├── Button.tsx
│   └── __tests__/
│       └── Button.test.tsx
└── tests/
    ├── integration/
    │   └── user.api.test.ts
    └── e2e/
        └── dashboard.spec.ts
```

## Test Commands

```bash
npm test                          # Run all tests
npm test -- --watch              # Watch mode
npm test -- --coverage           # With coverage
npm test -- -t "user service"    # Filter by name
npx playwright test               # Run E2E
npx playwright test --ui          # Interactive mode
```
