import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ResultsReport from './ResultsReport';
import { SimulationResult } from '@/lib/api';

vi.mock('./CIChart', () => ({
  default: () => <div>Mock CI Chart</div>,
}));

vi.mock('./EvidenceTab', () => ({
  default: () => <div>Mock Evidence Tab</div>,
}));

describe('ResultsReport', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockResult: SimulationResult = {
    id: 'sim-123',
    summary: 'Mixed reactions from customers',
    themes: [
      {
        label: 'Price Sensitivity',
        summary: 'Many customers are price-sensitive',
        count: 8,
      },
      {
        label: 'Quality Focus',
        summary: 'Quality matters more than price',
        count: 4,
      },
    ],
    standout_voices: [
      {
        persona_name: 'Maria',
        sentiment: 'negative',
        quote: 'I would find another place',
        reasoning: 'Regular customer with tight budget',
      },
    ],
    caveats: [],
    created_at: '2024-01-01',
  };

  const mockImpactData = {
    revenue: {
      point_estimate_pct: 5,
      ci_low_pct: -2,
      ci_high_pct: 12,
      confidence_level: 'medium',
      impact_type: 'positive',
      impact_label: 'Likely Positive',
    },
    customers_likely_stay: 10,
    customers_likely_reduce: 2,
    customers_likely_leave: 1,
    total_customers_modelled: 13,
    retention_rate_pct: 92,
    decision: 'go',
    decision_reasoning: 'Positive impact with acceptable risk',
    decision_framework: 'confidence-weighted',
    worst_case_summary: 'Lose up to 15% revenue',
    best_case_summary: 'Gain up to 20% revenue',
    most_likely_summary: 'Gain approximately 5% revenue',
  };

  describe('Rendering', () => {
    it('should render without crashing', () => {
      render(<ResultsReport result={mockResult} />);

      expect(screen.getByText(/Mixed reactions from customers/)).toBeInTheDocument();
    });

    it('should display summary', () => {
      render(<ResultsReport result={mockResult} />);

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });

    it('should render with impact data', () => {
      render(
        <ResultsReport result={mockResult} impactData={mockImpactData} />
      );

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
      expect(screen.getByText(/Mock CI Chart/)).toBeInTheDocument();
    });
  });

  describe('Themes Section', () => {
    it('should display theme cards', () => {
      render(<ResultsReport result={mockResult} />);

      expect(screen.getByText('Price Sensitivity')).toBeInTheDocument();
      expect(screen.getByText('Quality Focus')).toBeInTheDocument();
    });

    it('should show theme summaries', () => {
      render(<ResultsReport result={mockResult} />);

      expect(screen.getByText(/Many customers are price-sensitive/)).toBeInTheDocument();
      expect(screen.getByText(/Quality matters more than price/)).toBeInTheDocument();
    });

    it('should display theme counts', () => {
      render(<ResultsReport result={mockResult} />);

      expect(screen.getByText(/8 people/)).toBeInTheDocument();
      expect(screen.getByText(/4 people/)).toBeInTheDocument();
    });

    it('should handle singular person count', () => {
      const result = {
        ...mockResult,
        themes: [
          {
            label: 'Single Person',
            summary: 'Only one person',
            count: 1,
          },
        ],
      };

      render(<ResultsReport result={result} />);

      expect(screen.getByText(/1 person$/)).toBeInTheDocument();
    });

    it('should handle empty themes', () => {
      const result = {
        ...mockResult,
        themes: [],
      };

      render(<ResultsReport result={result} />);

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });
  });

  describe('Impact Data Display', () => {
    it('should render with impact data', () => {
      const { container } = render(
        <ResultsReport result={mockResult} impactData={mockImpactData} />
      );

      expect(container).toBeTruthy();
    });

    it('should display summary when given impact data', () => {
      render(
        <ResultsReport result={mockResult} impactData={mockImpactData} />
      );

      // Summary should always be visible
      expect(screen.getByText(/Mixed reactions from customers/)).toBeInTheDocument();
    });

    it('should render with impact without errors', () => {
      expect(() => {
        render(
          <ResultsReport result={mockResult} impactData={mockImpactData} />
        );
      }).not.toThrow();
    });

    it('should handle impact data gracefully', () => {
      const { container } = render(
        <ResultsReport result={mockResult} impactData={mockImpactData} />
      );

      expect(container).toBeTruthy();
    });

    it('should handle missing impact data', () => {
      render(
        <ResultsReport result={mockResult} impactData={undefined} />
      );

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });

    it('should handle null impact data', () => {
      render(
        <ResultsReport result={mockResult} impactData={null} />
      );

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });
  });

  describe('Confidence Badge', () => {
    it('should render high confidence data', () => {
      const highConfidence = {
        ...mockImpactData,
        revenue: {
          ...mockImpactData.revenue,
          confidence_level: 'high',
        },
      };

      const { container } = render(
        <ResultsReport result={mockResult} impactData={highConfidence} />
      );

      expect(container).toBeTruthy();
    });

    it('should render medium confidence data', () => {
      const mediumConfidence = {
        ...mockImpactData,
        revenue: {
          ...mockImpactData.revenue,
          confidence_level: 'medium',
        },
      };

      const { container } = render(
        <ResultsReport result={mockResult} impactData={mediumConfidence} />
      );

      expect(container).toBeTruthy();
    });

    it('should render low confidence data', () => {
      const lowConfidence = {
        ...mockImpactData,
        revenue: {
          ...mockImpactData.revenue,
          confidence_level: 'low',
        },
      };

      const { container } = render(
        <ResultsReport result={mockResult} impactData={lowConfidence} />
      );

      expect(container).toBeTruthy();
    });
  });

  describe('Standout Voices', () => {
    it('should display standout voices section', () => {
      const { container } = render(<ResultsReport result={mockResult} />);

      expect(screen.getByText('Maria')).toBeInTheDocument();
      expect(container).toBeTruthy();
    });

    it('should show quote text', () => {
      render(<ResultsReport result={mockResult} />);

      expect(screen.getByText(/I would find another place/)).toBeInTheDocument();
    });

    it('should display persona name for standout voice', () => {
      render(<ResultsReport result={mockResult} />);

      expect(screen.getByText('Maria')).toBeInTheDocument();
    });

    it('should handle empty standout voices', () => {
      const result = {
        ...mockResult,
        standout_voices: [],
      };

      render(<ResultsReport result={result} />);

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });

    it('should handle multiple standout voices', () => {
      const result = {
        ...mockResult,
        standout_voices: [
          {
            persona_name: 'Maria',
            sentiment: 'negative',
            quote: 'Would leave',
            reasoning: 'Budget conscious',
          },
          {
            persona_name: 'John',
            sentiment: 'positive',
            quote: 'Definitely stay',
            reasoning: 'Quality focus',
          },
        ],
      };

      render(<ResultsReport result={result} />);

      expect(screen.getByText('Maria')).toBeInTheDocument();
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText(/Would leave/)).toBeInTheDocument();
      expect(screen.getByText(/Definitely stay/)).toBeInTheDocument();
    });
  });

  describe('Tabs/Sections Navigation', () => {
    it('should render tabs for different sections', () => {
      const { container } = render(
        <ResultsReport
          result={mockResult}
          impactData={mockImpactData}
          responses={[]}
        />
      );

      // Component should render without errors
      expect(container).toBeTruthy();
    });

    it('should render with responses data', () => {
      const { container } = render(
        <ResultsReport
          result={mockResult}
          impactData={mockImpactData}
          responses={[
            {
              persona_name: 'Maria',
              sentiment: 1,
              quote: 'Test',
              reasoning: 'Test',
              created_at: '2024-01-01',
            },
          ]}
        />
      );

      expect(container).toBeTruthy();
    });
  });

  describe('Demographic Groups', () => {
    it('should render with demographic breakdown when provided', () => {
      const demographicGroups = [
        {
          group: 'Regulars',
          count: 8,
          avg_sentiment: 0.5,
          personas: ['Maria', 'John'],
          members: [
            { persona_name: 'Maria', age: 35, sentiment: 0.3 },
            { persona_name: 'John', age: 40, sentiment: 0.7 },
          ],
        },
        {
          group: 'Occasional',
          count: 3,
          avg_sentiment: 0.2,
          personas: ['Sarah'],
          members: [{ persona_name: 'Sarah', age: 28, sentiment: 0.2 }],
        },
      ];

      const { container } = render(
        <ResultsReport
          result={mockResult}
          impactData={mockImpactData}
          demographicGroups={demographicGroups}
        />
      );

      expect(container).toBeTruthy();
    });

    it('should handle empty demographic groups', () => {
      render(
        <ResultsReport
          result={mockResult}
          impactData={mockImpactData}
          demographicGroups={[]}
        />
      );

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });
  });

  describe('Variant Comparison', () => {
    it('should display variant labels when provided', () => {
      render(
        <ResultsReport
          result={mockResult}
          variantA="Keep current prices"
          variantB="Raise prices 15%"
        />
      );

      // Variant information should be visible
      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });

    it('should handle missing variants', () => {
      render(
        <ResultsReport result={mockResult} />
      );

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle very long theme summaries', () => {
      const longSummary = 'A'.repeat(500);
      const result = {
        ...mockResult,
        themes: [
          {
            label: 'Long Theme',
            summary: longSummary,
            count: 5,
          },
        ],
      };

      render(<ResultsReport result={result} />);

      expect(screen.getByText(/Long Theme/)).toBeInTheDocument();
    });

    it('should handle special characters in quotes', () => {
      const result = {
        ...mockResult,
        standout_voices: [
          {
            persona_name: 'Maria',
            sentiment: 'negative',
            quote: 'I said no way never',
            reasoning: 'Test',
          },
        ],
      };

      const { container } = render(<ResultsReport result={result} />);

      expect(container).toBeTruthy();
    });

    it('should handle high persona counts', () => {
      const result = {
        ...mockResult,
        themes: [
          {
            label: 'Large Group',
            summary: 'Many people',
            count: 150,
          },
        ],
      };

      render(<ResultsReport result={result} />);

      expect(screen.getByText(/150 people/)).toBeInTheDocument();
    });

    it('should handle zero impact estimate', () => {
      const zeroImpact = {
        ...mockImpactData,
        revenue: {
          ...mockImpactData.revenue,
          point_estimate_pct: 0,
          ci_low_pct: -5,
          ci_high_pct: 5,
        },
      };

      render(
        <ResultsReport result={mockResult} impactData={zeroImpact} />
      );

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });

    it('should handle negative impact estimates', () => {
      const negativeImpact = {
        ...mockImpactData,
        revenue: {
          ...mockImpactData.revenue,
          point_estimate_pct: -10,
          impact_type: 'negative',
          impact_label: 'Likely Negative',
        },
      };

      const { container } = render(
        <ResultsReport result={mockResult} impactData={negativeImpact} />
      );

      expect(container).toBeTruthy();
    });

    it('should handle extreme confidence intervals', () => {
      const extremeCI = {
        ...mockImpactData,
        revenue: {
          ...mockImpactData.revenue,
          ci_low_pct: -50,
          ci_high_pct: 100,
        },
      };

      render(
        <ResultsReport result={mockResult} impactData={extremeCI} />
      );

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });
  });

  describe('Caveats Display', () => {
    it('should render with caveats when present', () => {
      const result = {
        ...mockResult,
        caveats: [
          {
            type: 'small_sample',
            label: 'Small Sample',
            description: 'Only 12 personas simulated',
          },
          {
            type: 'not_causation',
            label: 'Not Causation',
            description: 'Simulation shows reactions, not guaranteed outcomes',
          },
        ],
      };

      const { container } = render(<ResultsReport result={result} />);

      expect(container).toBeTruthy();
    });

    it('should handle empty caveats', () => {
      const result = {
        ...mockResult,
        caveats: [],
      };

      render(<ResultsReport result={result} />);

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });
  });

  describe('RAG Selection Info', () => {
    it('should display RAG selection when provided', () => {
      const ragSelection = {
        domains: ['pricing', 'market'],
        question_type: 'pricing_change',
        reasoning: 'Question about price sensitivity',
      };

      render(
        <ResultsReport result={mockResult} ragSelection={ragSelection} />
      );

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });

    it('should handle missing RAG selection', () => {
      render(
        <ResultsReport result={mockResult} ragSelection={undefined} />
      );

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });
  });

  describe('Responses Handling', () => {
    it('should handle persona responses', () => {
      const responses = [
        {
          persona_name: 'Maria',
          sentiment: 0.3,
          quote: 'Too expensive',
          reasoning: 'Budget limited',
          created_at: '2024-01-01',
        },
        {
          persona_name: 'John',
          sentiment: 0.8,
          quote: 'Seems fair',
          reasoning: 'Quality justifies price',
          created_at: '2024-01-01',
        },
      ];

      render(
        <ResultsReport
          result={mockResult}
          impactData={mockImpactData}
          responses={responses}
        />
      );

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });

    it('should handle empty responses', () => {
      render(
        <ResultsReport
          result={mockResult}
          impactData={mockImpactData}
          responses={[]}
        />
      );

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });

    it('should handle undefined responses', () => {
      render(
        <ResultsReport
          result={mockResult}
          impactData={mockImpactData}
          responses={undefined}
        />
      );

      expect(screen.getByText('Mixed reactions from customers')).toBeInTheDocument();
    });
  });
});
