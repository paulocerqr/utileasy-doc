import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "./App";

describe("App", () => {
  it("renders the application identity", () => {
    render(<App />);

    expect(screen.getByText("UtileasyDoc")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Documentos" }),
    ).toBeInTheDocument();
  });
});
