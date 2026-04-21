import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import ProfileQualityNote from "./ProfileQualityNote";

describe("<ProfileQualityNote>", () => {
  it("renders nothing when completeness is null or undefined", () => {
    const { container: c1 } = render(<ProfileQualityNote completeness={null} />);
    const { container: c2 } = render(<ProfileQualityNote completeness={undefined} />);
    expect(c1.firstChild).toBeNull();
    expect(c2.firstChild).toBeNull();
  });

  it("renders nothing when completeness >= 60 (good profile, no need to warn)", () => {
    const { container } = render(<ProfileQualityNote completeness={85} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders a soft caution when completeness is 40-59", () => {
    render(<ProfileQualityNote completeness={50} />);
    expect(screen.getByText(/profile is partially complete/i)).toBeInTheDocument();
    expect(screen.getByText(/50%/)).toBeInTheDocument();
  });

  it("renders a stronger warning when completeness < 40", () => {
    render(<ProfileQualityNote completeness={25} />);
    expect(screen.getByText(/profile is sparse/i)).toBeInTheDocument();
    expect(screen.getByText(/25%/)).toBeInTheDocument();
  });

  it("optionally shows the top next-improvement hint", () => {
    render(
      <ProfileQualityNote
        completeness={40}
        nextImprovement="customer_age_distribution"
      />
    );
    expect(screen.getByText(/customer_age_distribution/i)).toBeInTheDocument();
  });
});
