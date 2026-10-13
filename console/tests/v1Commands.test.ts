import { describe, expect, it } from "vitest";
import { v1SupportedCommands } from "../src/data/v1Commands.js";

describe("v1's supported commands", () => {
  it("are read from v1's syntax_specs folder, alphabetical, without the package file", () => {
    const commands = v1SupportedCommands();
    expect(commands.length).toBeGreaterThanOrEqual(100);
    expect(commands).toEqual([...commands].sort());
    expect(commands).toContain("grep");
    expect(commands).toContain("rm");
    expect(commands.some((c) => c.startsWith("__"))).toBe(false);
  });
});
