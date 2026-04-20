import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import SimulatePage from './page';

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    pathname: '/app/simulate',
    query: { businessId: 'test-123' },
  })),
  useSearchParams: vi.fn(() => new URLSearchParams('businessId=test-123')),
}));

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href }: any) => <a href={href}>{children}</a>,
}));

// Mock Supabase client
vi.mock('@/lib/supabase/client', () => ({
  createClient: vi.fn(() => ({
    auth: {
      getSession: vi.fn().mockResolvedValue({
        data: { session: { user: { id: 'user-123' } } },
      }),
    },
  })),
}));

// Mock API
vi.mock('@/lib/api', () => ({
  getBusiness: vi.fn().mockResolvedValue({
    id: 'test-123',
    name: 'Test Business',
    type: 'restaurant',
  }),
  listBusinesses: vi.fn().mockResolvedValue([
    {
      id: 'test-123',
      name: 'Test Business',
      type: 'restaurant',
    },
  ]),
  listSimulations: vi.fn().mockResolvedValue([]),
}));

vi.mock('@/components/simulate2/ChatInterface', () => ({
  default: () => <div>Chat Interface</div>,
}));

vi.mock('@/components/shell/TopNav', () => ({
  default: () => <div>Top Nav</div>,
}));

describe('SimulatePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render without crashing', () => {
    render(<SimulatePage />);
    expect(document.body).toBeTruthy();
  });

  it('should not throw errors during render', () => {
    expect(() => {
      render(<SimulatePage />);
    }).not.toThrow();
  });
});
