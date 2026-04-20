import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import LoginPage from './page';

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    pathname: '/login',
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
      signInWithPassword: vi.fn(),
      getSession: vi.fn(),
    },
  })),
}));

describe('LoginPage', () => {
  it('should render without crashing', () => {
    render(<LoginPage />);
    expect(document.body).toBeTruthy();
  });

  it('should not throw errors during render', () => {
    expect(() => {
      render(<LoginPage />);
    }).not.toThrow();
  });

  it('should render successfully', () => {
    const { container } = render(<LoginPage />);
    expect(container).toBeTruthy();
  });
});
