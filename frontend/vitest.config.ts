import react from "@vitejs/plugin-react";
import { configDefaults, defineConfig } from "vitest/config";
import { fileURLToPath } from "node:url";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {"@": fileURLToPath(new URL("./src", import.meta.url))},
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.ts"],
    restoreMocks: true,
    clearMocks: true,
    // This is a standalone Node assertion script, not a Vitest suite.
    // package.json runs it explicitly after Vitest succeeds.
    exclude: [...configDefaults.exclude, "**/scripts/responsive-css-tools.test.mjs"],
  },
});
