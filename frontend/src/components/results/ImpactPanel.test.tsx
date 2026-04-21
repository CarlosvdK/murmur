import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import ImpactPanel from "./ImpactPanel";

const sample = {
  revenue: {
    point_estimate_pct: 5,
    ci_low_pct: -2,
    ci_high_pct: 12,
    confidence_level: "medium",
    impact_label: "Estimated revenue change",
  },
  customers_likely_stay: 10,
  customers_likely_reduce: 2,
  customers_likely_leave: 1,
  total_customers_modelled: 13,
  retention_rate_pct: 92,
  decision: "proceed",
  decision_reasoning: "Positive impact with acceptable risk",
  decision_framework: "confidence-weighted",
  worst_case_summary: "Lose 15%",
  best_case_summary: "Gain 20%",
  most_likely_summary: "Gain 5%",
};

function mockFetch(payload: unknown, ok = true) {
  global.fetch = vi.fn().mockResolvedValue({
    ok,
    json: () => Promise.resolve(payload),
  }) as any;
}

describe("<ImpactPanel>", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders nothing before the fetch resolves", () => {
    global.fetch = vi.fn().mockReturnValue(new Promise(() => {})) as any;
    const { container } = render(<ImpactPanel simulationId="sim-1" />);
    expect(container.firstChild).toBeNull();
  });

  it("renders the decision badge once data is loaded", async () => {
    mockFetch(sample);
    render(<ImpactPanel simulationId="sim-1" />);
    await waitFor(() =>
      expect(screen.getByText(/Likely worth it/i)).toBeInTheDocument()
    );
  });

  it("renders the point estimate with a plus sign when positive", async () => {
    mockFetch(sample);
    render(<ImpactPanel simulationId="sim-1" />);
    await waitFor(() => {
      const matches = screen.getAllByText(/\+5%/);
      expect(matches.length).toBeGreaterThan(0);
    });
  });

  it("uses the 'Proceed with caution' label when decision is 'caution'", async () => {
    mockFetch({ ...sample, decision: "caution" });
    render(<ImpactPanel simulationId="sim-1" />);
    await waitFor(() =>
      expect(screen.getByText(/Proceed with caution/i)).toBeInTheDocument()
    );
  });

  it("falls back to the default impact_label when not supplied", async () => {
    const noLabel = { ...sample, revenue: { ...sample.revenue, impact_label: undefined } };
    mockFetch(noLabel);
    render(<ImpactPanel simulationId="sim-1" />);
    await waitFor(() =>
      expect(screen.getByText(/Estimated Impact/)).toBeInTheDocument()
    );
  });

  it("renders nothing when the endpoint returns non-ok", async () => {
    mockFetch(null, false);
    const { container } = render(<ImpactPanel simulationId="sim-1" />);
    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
    expect(container.firstChild).toBeNull();
  });
});
