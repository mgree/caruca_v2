/**
 * Step 4's default input: the newest trace run on disk for the command, from either side.
 *
 * Read from the archived run directories (vitest sets CARUCA_EVAL_ROOT), where cat has v2
 * trace runs with a traces file and a v1 trace run the console recorded on 2026-10-13.
 */
import { existsSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { latestTraceFile } from "../src/server/startRun.js";

describe("the newest trace file for a command", () => {
  it("prefers v2's own newest successful trace run", () => {
    const source = latestTraceFile("cat", "v2");
    expect(source).not.toBeNull();
    expect(source!.from).toBe("v2");
    expect(source!.path.endsWith("/cat.traces.json")).toBe(true);
    expect(existsSync(source!.path)).toBe(true);
  });

  it("can be asked for v1's side first", () => {
    const source = latestTraceFile("cat", "v1");
    expect(source).not.toBeNull();
    expect(source!.from).toBe("v1");
    expect(source!.runId).toBe("2026-10-13T160403Z_cat_f3d9efdf");
  });

  it("is null for a command neither side has traced", () => {
    expect(latestTraceFile("no-such-command")).toBeNull();
  });
});
