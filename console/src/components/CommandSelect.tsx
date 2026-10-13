"use client";

import { useRouter } from "next/navigation";

/**
 * The dropdown of every command v1 supports. Choosing one opens that command's pipeline.
 *
 * Grouped so the fifteen commands the project is measuring come first; the rest is v1's
 * whole population, alphabetical, read from its checkout on each request.
 */
export function CommandSelect({
  current,
  groups,
}: {
  current: string;
  groups: { label: string; commands: readonly string[] }[];
}) {
  const router = useRouter();
  const known = groups.some((group) => group.commands.includes(current));
  return (
    <select
      className="picker__select mono"
      aria-label="Command"
      value={known ? current : ""}
      onChange={(event) => {
        const command = event.target.value;
        if (command) router.push(`/?command=${encodeURIComponent(command)}`);
      }}
    >
      {!known ? <option value="">{current} (not in v1's list)</option> : null}
      {groups.map((group) => (
        <optgroup key={group.label} label={group.label}>
          {group.commands.map((command) => (
            <option key={command} value={command}>
              {command}
            </option>
          ))}
        </optgroup>
      ))}
    </select>
  );
}
