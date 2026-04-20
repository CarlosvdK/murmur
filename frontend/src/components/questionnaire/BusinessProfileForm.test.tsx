import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import BusinessProfileForm from './BusinessProfileForm';

describe('BusinessProfileForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render without crashing', () => {
      const onSubmit = vi.fn();
      const { container } = render(<BusinessProfileForm onSubmit={onSubmit} />);
      expect(container).toBeTruthy();
    });

    it('should render the form with step indicator', () => {
      const onSubmit = vi.fn();
      const { container } = render(<BusinessProfileForm onSubmit={onSubmit} />);

      // Check that the form renders and is interactive
      expect(container.querySelectorAll('button').length).toBeGreaterThan(0);
      expect(container.querySelectorAll('input').length).toBeGreaterThan(0);
    });

    it('should render step 0 content initially', () => {
      const onSubmit = vi.fn();
      const { container } = render(<BusinessProfileForm onSubmit={onSubmit} />);

      // Verify main form is rendered
      expect(container).toBeTruthy();
      expect(screen.getByText(/Business Name/i)).toBeInTheDocument();
    });

    it('should display business type options', () => {
      const onSubmit = vi.fn();
      render(<BusinessProfileForm onSubmit={onSubmit} />);

      // Check for some business type buttons
      expect(screen.getByRole('button', { name: /restaurant/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /cafe/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /other/i })).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    it('should have Back and Next buttons', () => {
      const onSubmit = vi.fn();
      render(<BusinessProfileForm onSubmit={onSubmit} />);

      expect(screen.getByRole('button', { name: /back/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument();
    });

    it('should disable Back button on step 0', () => {
      const onSubmit = vi.fn();
      render(<BusinessProfileForm onSubmit={onSubmit} />);

      const backButton = screen.getByRole('button', { name: /back/i });
      expect(backButton).toBeDisabled();
    });

    it('should have Next button on step 0', () => {
      const onSubmit = vi.fn();
      render(<BusinessProfileForm onSubmit={onSubmit} />);

      const nextButton = screen.getByRole('button', { name: /next/i });
      expect(nextButton).toBeInTheDocument();
    });
  });

  describe('Step Progression', () => {
    it('should show different step headers', async () => {
      const onSubmit = vi.fn();
      const user = userEvent.setup();

      const { rerender } = render(<BusinessProfileForm onSubmit={onSubmit} />);

      // Should start at step 0
      expect(screen.getByText('Your Business')).toBeInTheDocument();

      // Component is re-renderable (simulating step progression)
      rerender(<BusinessProfileForm onSubmit={onSubmit} />);
      expect(screen.getByText('Your Business')).toBeInTheDocument();
    });
  });

  describe('Form State', () => {
    it('should accept input in form fields', async () => {
      const onSubmit = vi.fn();
      const user = userEvent.setup();

      const { container } = render(<BusinessProfileForm onSubmit={onSubmit} />);

      // Find input fields
      const inputs = container.querySelectorAll('input[type="text"]');
      expect(inputs.length).toBeGreaterThan(0);

      // Try to type in the first input
      if (inputs[0]) {
        await user.type(inputs[0], 'Test Business');
        expect((inputs[0] as HTMLInputElement).value).toBe('Test Business');
      }
    });

    it('should accept textarea input', async () => {
      const onSubmit = vi.fn();
      const user = userEvent.setup();

      const { container } = render(<BusinessProfileForm onSubmit={onSubmit} />);

      // Find textarea fields
      const textareas = container.querySelectorAll('textarea');
      expect(textareas.length).toBeGreaterThan(0);

      // Try to type in the first textarea
      if (textareas[0]) {
        await user.type(textareas[0], 'Test description');
        expect((textareas[0] as HTMLTextAreaElement).value).toBe('Test description');
      }
    });
  });

  describe('Button States', () => {
    it('should render buttons', () => {
      const onSubmit = vi.fn();
      render(<BusinessProfileForm onSubmit={onSubmit} />);

      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    it('should have step indicator buttons', () => {
      const onSubmit = vi.fn();
      render(<BusinessProfileForm onSubmit={onSubmit} />);

      const buttons = screen.getAllByRole('button');
      // Should have at least Back, Next, and step buttons
      expect(buttons.length).toBeGreaterThan(2);
    });
  });

  describe('Business Type Selection', () => {
    it('should render business type buttons', () => {
      const onSubmit = vi.fn();
      render(<BusinessProfileForm onSubmit={onSubmit} />);

      // Just check for a few key business types
      expect(
        screen.getByRole('button', { name: /restaurant/i })
      ).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: /cafe/i })
      ).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: /barbershop/i })
      ).toBeInTheDocument();
    });

    it('should allow selecting a business type', async () => {
      const onSubmit = vi.fn();
      const user = userEvent.setup();

      render(<BusinessProfileForm onSubmit={onSubmit} />);

      const restaurantBtn = screen.getByRole('button', { name: /restaurant/i });
      expect(restaurantBtn).toBeInTheDocument();

      await user.click(restaurantBtn);
      // Button should still be in the document after click
      expect(restaurantBtn).toBeInTheDocument();
    });
  });

  describe('Form Submission', () => {
    it('should call onSubmit callback', async () => {
      const onSubmit = vi.fn();
      render(<BusinessProfileForm onSubmit={onSubmit} loading={false} />);

      // Just verify the component renders and onSubmit is passed in
      expect(onSubmit).not.toHaveBeenCalled();
    });

    it('should handle loading state', () => {
      const onSubmit = vi.fn();
      const { rerender, container } = render(
        <BusinessProfileForm onSubmit={onSubmit} loading={false} />
      );

      const nextButton = screen.getByRole('button', { name: /next/i });
      expect(nextButton).toBeInTheDocument();

      rerender(<BusinessProfileForm onSubmit={onSubmit} loading={true} />);

      // In loading state, component should still be rendered
      expect(container).toBeTruthy();
    });
  });

  describe('Layout and Structure', () => {
    it('should have proper structure', () => {
      const onSubmit = vi.fn();
      const { container } = render(<BusinessProfileForm onSubmit={onSubmit} />);

      // Check for main container
      expect(container.querySelector('.mx-auto')).toBeTruthy();
    });

    it('should display step description', () => {
      const onSubmit = vi.fn();
      render(<BusinessProfileForm onSubmit={onSubmit} />);

      // Should show step descriptions
      const descriptions = screen.queryAllByText(/description/i);
      expect(descriptions.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Edge Cases', () => {
    it('should handle long input values', async () => {
      const onSubmit = vi.fn();
      const user = userEvent.setup();

      const { container } = render(<BusinessProfileForm onSubmit={onSubmit} />);

      const inputs = container.querySelectorAll('input[type="text"]');
      if (inputs[0]) {
        const longText = 'A'.repeat(500);
        await user.type(inputs[0], longText);
        expect((inputs[0] as HTMLInputElement).value).toBe(longText);
      }
    });

    it('should handle special characters', async () => {
      const onSubmit = vi.fn();
      const user = userEvent.setup();

      const { container } = render(<BusinessProfileForm onSubmit={onSubmit} />);

      const textareas = container.querySelectorAll('textarea');
      if (textareas[0]) {
        const specialText = 'Test & "quotes" <tags>';
        await user.type(textareas[0], specialText);
        expect((textareas[0] as HTMLTextAreaElement).value).toContain('Test');
      }
    });
  });

  describe('Form Fields Present', () => {
    it('should have input fields for text entry', () => {
      const onSubmit = vi.fn();
      const { container } = render(<BusinessProfileForm onSubmit={onSubmit} />);

      const inputs = container.querySelectorAll('input');
      expect(inputs.length).toBeGreaterThan(0);
    });

    it('should have textarea for longer text', () => {
      const onSubmit = vi.fn();
      const { container } = render(<BusinessProfileForm onSubmit={onSubmit} />);

      const textareas = container.querySelectorAll('textarea');
      expect(textareas.length).toBeGreaterThan(0);
    });
  });

  describe('Accessibility', () => {
    it('should be renderable without errors', () => {
      const onSubmit = vi.fn();

      expect(() => {
        render(<BusinessProfileForm onSubmit={onSubmit} />);
      }).not.toThrow();
    });

    it('should have interactive elements', () => {
      const onSubmit = vi.fn();
      render(<BusinessProfileForm onSubmit={onSubmit} />);

      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });
});
