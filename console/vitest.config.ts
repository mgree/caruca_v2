import { defineConfig } from "vitest/config";

/**
 * The reader tests run against real run directories, not fixtures (task 010 §9). Those
 * directories were archived on 2026-10-13 for a clean slate, so the tests read the archive:
 * `CARUCA_EVAL_ROOT` is resolved by `repoPaths()` relative to the repo root.
 */
export default defineConfig({
  test: {
    environment: "node",
    env: { CARUCA_EVAL_ROOT: "eval/_archive/2026-10-13_parity" },
  },
});
