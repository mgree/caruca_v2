/**
 * Every command v1 supports, read from its checkout.
 *
 * v1 registers a command by one rule only: a file `syntax_specs/<cmd>.py` defining
 * `<cmd>_syntax_spec` (CLAUDE.md, "Command registration is reflective and name-coupled").
 * So the list of files *is* the list of commands, and the console reads it rather than
 * keeping a copy that would drift.
 */
import { readdirSync } from "node:fs";
import { join } from "node:path";
import { v1Root } from "./paths.js";

export function v1SyntaxSpecsDir(root = v1Root()): string {
  return join(root, "caruca", "src", "caruca", "syntax_specs");
}

/** Command names in v1's order of registration: alphabetical by file. */
export function v1SupportedCommands(root = v1Root()): string[] {
  let names: string[];
  try {
    names = readdirSync(v1SyntaxSpecsDir(root));
  } catch {
    return [];
  }
  return names
    .filter((name) => name.endsWith(".py") && !name.startsWith("__"))
    .map((name) => name.slice(0, -".py".length))
    .sort();
}
