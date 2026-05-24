import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Metric } from "./Metric";

describe("Metric", () => {
  it("renders the label and value", () => {
    render(<Metric label="Años disponibles" value={12} />);
    expect(screen.getByText("Años disponibles")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
  });
});
