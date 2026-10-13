/**
 * The home screen's data: one command's four steps, read from what is on disk.
 *
 * Tested on the committed run directories and v1's real artifacts, as the other readers are.
 */
import { describe, expect, it } from "vitest";
import {
  commandOverview,
  knownCommands,
  PINNED_COMMANDS,
  CONFIRMATION_COMMANDS,
} from "../src/data/commandOverview.js";

describe("the command picker", () => {
  it("offers the nine and the six first, in a fixed order, then anything else with data", () => {
    const commands = knownCommands();
    expect(commands.slice(0, 15)).toEqual([...PINNED_COMMANDS, ...CONFIRMATION_COMMANDS]);
    expect(new Set(commands).size).toBe(commands.length);
  });
});

describe("one command's steps", () => {
  it("reads cat's four steps with v1's artifacts and v2's runs", () => {
    const overview = commandOverview("cat");
    expect(overview.steps.map((step) => step.stage)).toEqual([
      "syntax_spec",
      "generate",
      "trace",
      "annotate",
    ]);
    // cat has a committed grammar, an archived LLM output, a parity expansion, parity traces
    // and a parity annotation: every v1 artifact is present.
    for (const step of overview.steps) expect(step.v1.complete).toBe(true);
    // The September parity campaigns ran every step on cat, so v2 has a result at each.
    for (const step of overview.steps) expect(step.v2.latestOk).not.toBeNull();
    expect(overview.nextStage).toBeNull();
    // The parity expansion is counted, not just detected.
    expect(overview.steps[1]!.v1.artifacts[0]!.summary).toBe("35 configurations");
  });

  it("names the first step v2 has not finished as the next one", () => {
    // dirname has v1's side (generated 2026-10-13) and no v2 run yet.
    const overview = commandOverview("dirname");
    expect(overview.steps[2]!.v1.complete).toBe(true);
    expect(overview.nextStage).toBe("syntax_spec");
    expect(overview.steps[0]!.v2.latest).toBeNull();
  });

  it("marks a command nothing has touched as entirely absent on both sides", () => {
    const overview = commandOverview("no-such-command");
    for (const step of overview.steps) {
      expect(step.v2.runs).toEqual([]);
      expect(step.score).toBeNull();
    }
    expect(overview.steps[1]!.v1.complete).toBe(false);
    expect(overview.nextStage).toBe("syntax_spec");
  });
});
