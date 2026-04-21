import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import OutcomeForm from "./OutcomeForm";

vi.mock("@/lib/api", () => ({
  submitRealOutcome: vi.fn().mockResolvedValue({ id: "outcome-123" }),
}));

import { submitRealOutcome } from "@/lib/api";

describe("<OutcomeForm>", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the 'What happened?' CTA when not yet logged", () => {
    render(<OutcomeForm simulationId="sim-1" />);
    expect(screen.getByRole("button", { name: /what happened/i })).toBeInTheDocument();
  });

  it("opens the form when the CTA is clicked", () => {
    render(<OutcomeForm simulationId="sim-1" />);
    fireEvent.click(screen.getByRole("button", { name: /what happened/i }));
    expect(screen.getByLabelText(/what actually happened/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /submit/i })).toBeInTheDocument();
  });

  it("disables submit until the required field has content", () => {
    render(<OutcomeForm simulationId="sim-1" />);
    fireEvent.click(screen.getByRole("button", { name: /what happened/i }));
    const submit = screen.getByRole("button", { name: /submit/i });
    expect(submit).toBeDisabled();

    fireEvent.change(screen.getByLabelText(/what actually happened/i), {
      target: { value: "Revenue went up 8%" },
    });
    expect(submit).not.toBeDisabled();
  });

  it("submits the outcome and shows a 'Logged' badge", async () => {
    render(<OutcomeForm simulationId="sim-1" />);
    fireEvent.click(screen.getByRole("button", { name: /what happened/i }));
    fireEvent.change(screen.getByLabelText(/what actually happened/i), {
      target: { value: "Revenue went up 8%" },
    });
    fireEvent.click(screen.getByLabelText(/matched prediction/i));
    fireEvent.click(screen.getByRole("button", { name: /submit/i }));

    await waitFor(() => {
      expect(submitRealOutcome).toHaveBeenCalledWith("sim-1", {
        what_actually_happened: "Revenue went up 8%",
        outcome_matched: true,
      });
    });
    expect(await screen.findByText(/logged/i)).toBeInTheDocument();
  });

  it("shows error message on API failure without losing input", async () => {
    (submitRealOutcome as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error("boom"));
    render(<OutcomeForm simulationId="sim-1" />);
    fireEvent.click(screen.getByRole("button", { name: /what happened/i }));
    fireEvent.change(screen.getByLabelText(/what actually happened/i), {
      target: { value: "sales dipped 3%" },
    });
    fireEvent.click(screen.getByRole("button", { name: /submit/i }));

    await waitFor(() => {
      expect(screen.getByText(/couldn't save/i)).toBeInTheDocument();
    });
    // Preserve input so the user can retry
    expect(
      (screen.getByLabelText(/what actually happened/i) as HTMLTextAreaElement).value
    ).toBe("sales dipped 3%");
  });

  it("shows 'Logged' state immediately if outcome already exists", () => {
    render(<OutcomeForm simulationId="sim-1" existingOutcome={{ id: "o-1" }} />);
    expect(screen.getByText(/logged/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /what happened/i })).not.toBeInTheDocument();
  });
});
