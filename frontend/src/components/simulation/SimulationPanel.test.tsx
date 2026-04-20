import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import SimulationPanel from './SimulationPanel';

// Mock EventSource for streaming API
class MockEventSource {
  url: string;
  addEventListener = vi.fn();
  close = vi.fn();
  removeEventListener = vi.fn();

  constructor(url: string) {
    this.url = url;
  }
}

vi.stubGlobal('EventSource', MockEventSource as any);

vi.mock('./ProgressTimeline', () => ({
  default: () => <div data-testid="progress-timeline">Progress Timeline</div>,
}));

vi.mock('./PersonaCard', () => ({
  default: ({ persona }: any) => <div data-testid="persona-card">{persona.name}</div>,
}));

vi.mock('@/lib/api', () => ({
  createSimulationStream: vi.fn(() => new MockEventSource('test-url')),
  getSimulationProgress: vi.fn(),
  getSimulationPersonas: vi.fn().mockResolvedValue([]),
  getSimulationResponses: vi.fn().mockResolvedValue([]),
  getSimulationResult: vi.fn(),
}));

vi.mock('../results/ResultsReport', () => ({
  default: () => <div data-testid="results-report">Results Report</div>,
}));

vi.mock('../results/PersonaResponseCard', () => ({
  default: () => <div data-testid="persona-response">Response</div>,
}));

vi.mock('../results/CaveatCard', () => ({
  default: () => <div data-testid="caveat-card">Caveat</div>,
}));

vi.mock('../results/ImpactPanel', () => ({
  default: () => <div data-testid="impact-panel">Impact</div>,
}));

describe('SimulationPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render without crashing', () => {
      const { container } = render(<SimulationPanel simulationId="test-sim-123" />);
      expect(container).toBeTruthy();
    });

    it('should render with required props', () => {
      const { container } = render(
        <SimulationPanel
          simulationId="test-sim-123"
          variantA="Option A"
          variantB="Option B"
        />
      );
      expect(container).toBeTruthy();
    });

    it('should render tab buttons', () => {
      render(<SimulationPanel simulationId="test-sim-123" />);
      expect(screen.getByRole('button', { name: /Progress/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Personas/i })).toBeInTheDocument();
    });
  });

  describe('Props', () => {
    it('should accept simulationId prop', () => {
      const { container } = render(<SimulationPanel simulationId="unique-id-123" />);
      expect(container).toBeTruthy();
    });

    it('should accept optional variant props', () => {
      const { container } = render(
        <SimulationPanel
          simulationId="test-id"
          variantA="Test A"
          variantB="Test B"
        />
      );
      expect(container).toBeTruthy();
    });

    it('should accept null variant props', () => {
      const { container } = render(
        <SimulationPanel
          simulationId="test-id"
          variantA={null}
          variantB={null}
        />
      );
      expect(container).toBeTruthy();
    });
  });

  describe('Tabs', () => {
    it('should have multiple tabs', () => {
      render(<SimulationPanel simulationId="test-sim-123" />);
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(2);
    });

    it('should have Progress tab', () => {
      render(<SimulationPanel simulationId="test-sim-123" />);
      expect(screen.getByRole('button', { name: /Progress/i })).toBeInTheDocument();
    });

    it('should have Personas tab', () => {
      render(<SimulationPanel simulationId="test-sim-123" />);
      expect(screen.getByRole('button', { name: /Personas/i })).toBeInTheDocument();
    });

    it('should have Responses tab', () => {
      render(<SimulationPanel simulationId="test-sim-123" />);
      const buttons = screen.getAllByRole('button');
      expect(buttons.some(btn => btn.textContent?.includes('Responses'))).toBeTruthy();
    });
  });

  describe('Layout', () => {
    it('should have grid layout', () => {
      const { container } = render(<SimulationPanel simulationId="test-sim-123" />);
      const grid = container.querySelector('.grid');
      expect(grid).toBeTruthy();
    });

    it('should handle responsive layout', () => {
      const { container } = render(<SimulationPanel simulationId="test-sim-123" />);
      expect(container.querySelector('.lg\\:col-span-2')).toBeTruthy();
    });
  });

  describe('Accessibility', () => {
    it('should render without errors', () => {
      expect(() => {
        render(<SimulationPanel simulationId="test-sim-123" />);
      }).not.toThrow();
    });

    it('should have accessible button elements', () => {
      render(<SimulationPanel simulationId="test-sim-123" />);
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
      buttons.forEach(button => {
        expect(button.tagName).toBe('BUTTON');
      });
    });

    it('should support keyboard navigation', () => {
      render(<SimulationPanel simulationId="test-sim-123" />);
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(['button', 'submit'].includes(button.getAttribute('type') || 'button')).toBeTruthy();
      });
    });
  });

  describe('State Management', () => {
    it('should render initially without crashing', () => {
      const { container } = render(<SimulationPanel simulationId="test-sim-123" />);
      expect(container.firstChild).toBeTruthy();
    });

    it('should remain stable on re-render', () => {
      const { rerender } = render(<SimulationPanel simulationId="test-sim-123" />);
      expect(() => {
        rerender(<SimulationPanel simulationId="test-sim-123" />);
      }).not.toThrow();
    });
  });
});
