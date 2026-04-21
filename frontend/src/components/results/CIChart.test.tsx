import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import CIChart from "./CIChart";

const base = {
  pointEstimate: 5,
  ciLow: -2,
  ciHigh: 12,
  rejectNull: true,
  decision: "proceed",
};

describe("<CIChart>", () => {
  it("renders the go/no-go badge with the right label for each decision", () => {
    const cases: Array<[string, RegExp]> = [
      ["proceed", /^Go$/],
      ["caution", /^Caution$/],
      ["avoid", /^No-go$/],
      ["test_first", /^Test first$/],
    ];
    for (const [decision, label] of cases) {
      const { unmount } = render(<CIChart {...base} decision={decision} />);
      expect(screen.getByText(label)).toBeInTheDocument();
      unmount();
    }
  });

  it("displays the point-estimate percentage with a plus sign when positive", () => {
    render(<CIChart {...base} pointEstimate={8} />);
    const matches = screen.getAllByText(/\+8%/);
    expect(matches.length).toBeGreaterThan(0);
  });

  it("displays negative point estimates without a plus sign", () => {
    render(<CIChart {...base} pointEstimate={-4} />);
    const matches = screen.getAllByText(/-4%/);
    expect(matches.length).toBeGreaterThan(0);
  });

  it("renders the probability breakdown when pPositive/pNegative are provided", () => {
    render(<CIChart {...base} pPositive={0.7} pNegative={0.3} />);
    expect(screen.getByText(/70% chance positive/i)).toBeInTheDocument();
    expect(screen.getByText(/30% chance negative/i)).toBeInTheDocument();
  });

  it("falls back to 'CI crosses zero' copy when rejectNull is false and no probabilities", () => {
    render(<CIChart {...base} rejectNull={false} />);
    expect(screen.getByText(/confidence interval crosses zero/i)).toBeInTheDocument();
  });

  it("uses a default 'Estimated impact' label when none is passed", () => {
    render(<CIChart {...base} />);
    // Label appears in header + subtitle -- just confirm at least one exists.
    expect(screen.getAllByText(/Estimated impact/i).length).toBeGreaterThan(0);
  });
});
