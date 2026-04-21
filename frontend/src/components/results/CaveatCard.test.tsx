import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import CaveatCard from "./CaveatCard";

vi.mock("@/lib/api", () => ({
  getSimulationCaveats: vi.fn(),
}));

import { getSimulationCaveats } from "@/lib/api";

describe("<CaveatCard>", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders nothing while the API is pending", () => {
    (getSimulationCaveats as any).mockReturnValue(new Promise(() => {}));
    const { container } = render(<CaveatCard simulationId="sim-1" />);
    expect(container.firstChild).toBeNull();
  });

  it("renders each caveat title + message once loaded", async () => {
    (getSimulationCaveats as any).mockResolvedValue([
      { severity: "warning", title: "Small sample", message: "Only 8 personas" },
      { severity: "info", title: "Not causation", message: "We simulate intent" },
    ]);
    render(<CaveatCard simulationId="sim-1" />);
    expect(await screen.findByText(/Small sample/)).toBeInTheDocument();
    // info caveats are hidden by default when any warnings exist; expand to see
    fireEvent.click(screen.getByRole("button", { name: /Show/i }));
    expect(screen.getByText(/Not causation/)).toBeInTheDocument();
  });

  it("sorts critical > warning > info", async () => {
    (getSimulationCaveats as any).mockResolvedValue([
      { severity: "info", title: "Info A", message: "x" },
      { severity: "critical", title: "Critical A", message: "x" },
      { severity: "warning", title: "Warning A", message: "x" },
    ]);
    render(<CaveatCard simulationId="sim-1" />);
    await waitFor(() =>
      expect(screen.getByText(/Critical A/)).toBeInTheDocument()
    );
    const html = document.body.innerHTML;
    expect(html.indexOf("Critical A")).toBeLessThan(html.indexOf("Warning A"));
  });

  it("shows caveat-count badge", async () => {
    (getSimulationCaveats as any).mockResolvedValue([
      { severity: "warning", title: "a", message: "x" },
      { severity: "warning", title: "b", message: "x" },
      { severity: "warning", title: "c", message: "x" },
    ]);
    render(<CaveatCard simulationId="sim-1" />);
    await waitFor(() =>
      expect(screen.getByText(/3 caveats/i)).toBeInTheDocument()
    );
  });

  it("renders 'caveat' singular when there is exactly one", async () => {
    (getSimulationCaveats as any).mockResolvedValue([
      { severity: "warning", title: "only", message: "x" },
    ]);
    render(<CaveatCard simulationId="sim-1" />);
    await waitFor(() =>
      expect(screen.getByText(/1 caveat$/i)).toBeInTheDocument()
    );
  });
});
