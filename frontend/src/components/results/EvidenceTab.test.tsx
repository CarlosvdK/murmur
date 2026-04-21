import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import EvidenceTab from "./EvidenceTab";

vi.mock("./PersonaResponseCard", () => ({
  default: ({ response }: any) => (
    <div data-testid="persona-response">{response.persona_name}</div>
  ),
}));

const responses = [
  { persona_name: "Maria", response: "I'd still come", sentiment: 0.1 },
  { persona_name: "Jon", response: "I'd leave", sentiment: -0.5 },
] as any;

const groups = [
  {
    group: "Regulars",
    count: 1,
    avg_sentiment: 0.1,
    personas: ["Maria"],
    members: [{ persona_name: "Maria", sentiment: 0.1 }],
  },
  {
    group: "Occasionals",
    count: 1,
    avg_sentiment: -0.5,
    personas: ["Jon"],
    members: [{ persona_name: "Jon", sentiment: -0.5 }],
  },
];

describe("<EvidenceTab>", () => {
  it("renders the baseline summary when provided", () => {
    render(
      <EvidenceTab
        responses={responses}
        baselineSummary="Mostly regulars, 20% tourists"
      />
    );
    expect(screen.getByText(/Mostly regulars/i)).toBeInTheDocument();
  });

  it("renders the say-do gap callout when provided", () => {
    render(
      <EvidenceTab
        responses={responses}
        statedVsActualGap="Customers say they'd leave but historically absorb +10% hikes"
      />
    );
    expect(screen.getByText(/Say-Do Gap/i)).toBeInTheDocument();
    expect(screen.getByText(/historically absorb/i)).toBeInTheDocument();
  });

  it("renders behavioral-prediction cells for each provided field", () => {
    render(
      <EvidenceTab
        responses={responses}
        behavioralPrediction={{
          engagement_change: "slight dip",
          spend_change: "flat",
        }}
      />
    );
    expect(screen.getByText(/slight dip/i)).toBeInTheDocument();
    expect(screen.getByText(/flat/i)).toBeInTheDocument();
  });

  it("filters persona cards when a segment chip is clicked", () => {
    render(<EvidenceTab responses={responses} demographicGroups={groups} />);
    // Before filter: both personas visible
    expect(screen.getAllByTestId("persona-response")).toHaveLength(2);

    fireEvent.click(screen.getByRole("button", { name: /Regulars/ }));

    const after = screen.getAllByTestId("persona-response");
    expect(after).toHaveLength(1);
    expect(after[0]).toHaveTextContent("Maria");
  });

  it("clears the filter when the chip is clicked again", () => {
    render(<EvidenceTab responses={responses} demographicGroups={groups} />);
    const chip = screen.getByRole("button", { name: /Regulars/ });
    fireEvent.click(chip);
    fireEvent.click(chip);
    expect(screen.getAllByTestId("persona-response")).toHaveLength(2);
  });

  it("renders a persona card per response when no filter applied", () => {
    render(<EvidenceTab responses={responses} />);
    expect(screen.getAllByTestId("persona-response")).toHaveLength(2);
  });
});
