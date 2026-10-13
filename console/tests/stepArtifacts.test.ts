/**
 * The side-by-side popup's data, read from the archived runs (vitest sets CARUCA_EVAL_ROOT).
 */
import { describe, expect, it } from "vitest";
import { stepArtifacts, CAP_BYTES } from "../src/data/stepArtifacts.js";

describe("both sides' artifacts for a step", () => {
  it("finds cat's grammar on both sides, as Python text", () => {
    const { v1, v2 } = stepArtifacts("cat", "syntax_spec");
    expect(v1).not.toBeNull();
    expect(v2).not.toBeNull();
    expect(v1!.text).toContain("cat_syntax_spec");
    expect(v2!.text).toContain("cat_syntax_spec");
    expect(v2!.source).toMatch(/^v2 run 2026-/);
  });

  it("uses the console's own v1 trace run of cat from 13 October, and caps a large file", () => {
    const { v1, v2 } = stepArtifacts("cat", "trace");
    expect(v1?.source).toBe("v1 run 2026-10-13T160403Z_cat_f3d9efdf");
    expect(v2).not.toBeNull();
    for (const side of [v1!, v2!]) {
      expect(side.text.length).toBeLessThanOrEqual(CAP_BYTES);
      expect(side.truncated).toBe(side.bytes > CAP_BYTES);
    }
  });

  it("says plainly when a side has nothing", () => {
    const { v1, v2 } = stepArtifacts("no-such-command", "annotate");
    expect(v1).toBeNull();
    expect(v2).toBeNull();
  });
});
