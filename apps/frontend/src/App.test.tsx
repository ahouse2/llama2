import { act } from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

vi.mock("./components/ui/toast-demo", () => ({
  ToastDemo: () => <div data-testid="toast-demo" />
}));

import App from "./App";

describe("App", () => {
  it("renders module buttons and switches selection", async () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: /Discovery Intelligence Console/i })).toBeInTheDocument();

    const correspondenceButton = screen.getByRole("button", { name: /Correspondence/i });
    const user = userEvent.setup();
    await act(async () => {
      await user.click(correspondenceButton);
    });

    expect(screen.getByText(/Noah Patel/)).toBeInTheDocument();
    expect(screen.getByText(/Communications Sleuth/)).toBeInTheDocument();
  });
});
