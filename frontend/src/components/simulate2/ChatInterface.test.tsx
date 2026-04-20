import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Mock Supabase before importing component
vi.mock('@/lib/supabase/client', () => ({
  createClient: vi.fn(() => ({
    auth: {
      getSession: vi.fn().mockResolvedValue({
        data: { session: { access_token: 'test-token' } },
      }),
    },
  })),
}));

// Mock API
vi.mock('@/lib/api', () => ({
  createSimulation: vi.fn(),
  getSimulationProgress: vi.fn(),
  getSimulationResult: vi.fn(),
  getSimulationResponses: vi.fn().mockResolvedValue([]),
  getSimulationCaveats: vi.fn().mockResolvedValue([]),
}));

// Mock fetch
global.fetch = vi.fn();

import ChatInterface from './ChatInterface';

describe('ChatInterface', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render without crashing', () => {
      const { container } = render(<ChatInterface businessId="test-business" />);
      expect(container).toBeTruthy();
    });

    it('should display initial prompt', () => {
      render(<ChatInterface businessId="test-business" />);
      expect(screen.getByText('What do you want to simulate?')).toBeInTheDocument();
    });

    it('should render input field', () => {
      render(<ChatInterface businessId="test-business" />);
      const input = screen.getByPlaceholderText('What would happen if...');
      expect(input).toBeInTheDocument();
    });

    it('should render Run button', () => {
      render(<ChatInterface businessId="test-business" />);
      expect(screen.getByRole('button', { name: /run/i })).toBeInTheDocument();
    });
  });

  describe('Input Handling', () => {
    it('should update input value when typing', async () => {
      const user = userEvent.setup();
      render(<ChatInterface businessId="test-business" />);

      const input = screen.getByPlaceholderText('What would happen if...');
      await user.type(input, 'Test question');

      expect(input).toHaveValue('Test question');
    });

    it('should disable Run button when empty', () => {
      render(<ChatInterface businessId="test-business" />);
      const runButton = screen.getByRole('button', { name: /^Run$/ });
      expect(runButton).toBeDisabled();
    });

    it('should enable Run button when has text', async () => {
      const user = userEvent.setup();
      render(<ChatInterface businessId="test-business" />);

      const input = screen.getByPlaceholderText('What would happen if...');
      await user.type(input, 'Question');

      const runButton = screen.getByRole('button', { name: /^Run$/ });
      expect(runButton).not.toBeDisabled();
    });
  });

  describe('Edge Cases', () => {
    it('should handle null businessId gracefully', () => {
      const { container } = render(<ChatInterface businessId={null} />);
      expect(container).toBeTruthy();
    });

    it('should handle very long input text', async () => {
      const user = userEvent.setup();
      render(<ChatInterface businessId="test-business" />);

      const input = screen.getByPlaceholderText('What would happen if...');
      const longText = 'A'.repeat(500);
      await user.type(input, longText);

      expect(input).toHaveValue(longText);
    });
  });
});
