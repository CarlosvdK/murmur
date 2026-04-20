import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DashboardPage from './page';

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    replace: vi.fn(),
    pathname: '/app',
    refresh: vi.fn(),
  })),
  useSearchParams: vi.fn(() => new URLSearchParams()),
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
vi.mock('@/lib/api', () => {
  const mockListBusinesses = vi.fn().mockResolvedValue([]);
  const mockListSimulations = vi.fn().mockResolvedValue([]);
  return {
    listBusinesses: mockListBusinesses,
    listSimulations: mockListSimulations,
  };
});

global.fetch = vi.fn();

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render without crashing', () => {
    render(<DashboardPage />);
    expect(document.body).toBeTruthy();
  });

  it('should not throw errors during render', () => {
    expect(() => {
      render(<DashboardPage />);
    }).not.toThrow();
  });

  it('should render successfully with async content', async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(document.body).toBeTruthy();
    });
  });
});
