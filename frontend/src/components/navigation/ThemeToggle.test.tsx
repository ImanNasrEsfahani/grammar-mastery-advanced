import {fireEvent, render, screen, waitFor} from "@testing-library/react";
import {beforeEach, expect, test} from "vitest";
import {ThemeToggle} from "./ThemeToggle";

beforeEach(() => {
  window.localStorage.clear();
  document.documentElement.dataset.theme = "light";
  document.documentElement.style.colorScheme = "light";
});

test("theme toggle persists the selected mode and synchronizes duplicate header instances", async () => {
  render(
    <>
      <ThemeToggle locale="fa" />
      <ThemeToggle locale="fa" />
    </>,
  );

  await waitFor(() =>
    expect(
      screen.getAllByRole("button", {name: "فعال کردن حالت تاریک"}),
    ).toHaveLength(2),
  );

  const darkButtons = screen.getAllByRole("button", {
    name: "فعال کردن حالت تاریک",
  });
  fireEvent.click(darkButtons[0]!);

  await waitFor(() =>
    expect(document.documentElement.dataset.theme).toBe("dark"),
  );
  expect(window.localStorage.getItem("gmp-theme")).toBe("dark");

  const lightButtons = screen.getAllByRole("button", {
    name: "فعال کردن حالت روشن",
  });
  expect(lightButtons).toHaveLength(2);
  expect(lightButtons[0]!).toHaveAttribute("aria-pressed", "true");
});
