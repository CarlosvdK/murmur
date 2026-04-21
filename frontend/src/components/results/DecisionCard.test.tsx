import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import DecisionCard from "./DecisionCard";

describe("<DecisionCard>", () => {
  it("renders the 'Go' label + reasoning for decision=proceed", () => {
    render(
      <DecisionCard
        decision="proceed"
        reasoning="Upside > downside, CI excludes zero"
      />
    );
    expect(screen.getByText(/^Go$/)).toBeInTheDocument();
    expect(screen.getByText(/Upside > downside/)).toBeInTheDocument();
  });

  it("uses 'Caution' label for decision=caution", () => {
    render(<DecisionCard decision="caution" reasoning="x" />);
    expect(screen.getByText(/^Caution$/)).toBeInTheDocument();
  });

  it("uses 'No-go' label for decision=avoid", () => {
    render(<DecisionCard decision="avoid" reasoning="x" />);
    expect(screen.getByText(/^No-go$/)).toBeInTheDocument();
  });

  it("uses 'Test first' label for decision=test_first", () => {
    render(<DecisionCard decision="test_first" reasoning="x" />);
    expect(screen.getByText(/Test first/i)).toBeInTheDocument();
  });

  it("falls back to 'Test first' for unknown decision values", () => {
    render(<DecisionCard decision="banana" reasoning="x" />);
    expect(screen.getByText(/Test first/i)).toBeInTheDocument();
  });

  it("optionally shows a confidence pill", () => {
    render(<DecisionCard decision="proceed" reasoning="x" confidence="high" />);
    expect(screen.getByText(/high confidence/i)).toBeInTheDocument();
  });

  it("hides the confidence pill when confidence is not provided", () => {
    render(<DecisionCard decision="proceed" reasoning="x" />);
    expect(screen.queryByText(/confidence/i)).not.toBeInTheDocument();
  });
});
