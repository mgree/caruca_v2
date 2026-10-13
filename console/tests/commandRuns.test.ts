import { describe, expect, it } from "vitest";
import { runIdsForCommand } from "../src/data/commandRuns.js";

describe("the runs that belong to one command", () => {
  it("collects cat's v2 runs, its empty shells and its v1 runs from the archive", () => {
    const ids = runIdsForCommand("cat");
    expect(ids.v2.length).toBeGreaterThan(0);
    expect(ids.v1.length).toBeGreaterThan(0);
    for (const id of ids.all) expect(id).toContain("_cat_");
    expect(ids.all.length).toBe(ids.v2.length + ids.v2Empty.length + ids.v1.length);
  });

  it("is empty for a command nothing has run", () => {
    expect(runIdsForCommand("no-such-command").all).toEqual([]);
  });
});
