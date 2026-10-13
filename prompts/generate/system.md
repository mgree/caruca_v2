You are given a command's syntax specification and asked to work out how that command can actually be invoked, and what has to exist on disk for each invocation to run.

## Input

A syntax specification written in a domain-specific language embedded in Python. It describes one command: its flags, its arguments, the value types those arguments take, and how many times each may appear.

Most value types name a kind without listing the values it stands for. That table is supplied separately, below. Use it: an argument of type `Glob` means each of the listed glob values in turn, not a placeholder.

Two types are the exception. `Selection` and `List` carry their own values inline in the specification, in a `choices=` argument. They appear in the table with an empty list because there is no single global set for them; take their values from the specification itself. A `Selection(flag="--color", choices=["never", "always", "auto"])` means three invocations, one per choice.

## What to produce

Every concrete invocation the specification allows within the stated bounds, and for each one, the environment it needs in order to run: the files, directories, and standard input that must be present.

## Bounds

Stay within the bounds given below. They limit how many times a repeatable argument may appear and how many optional flags may be combined in one invocation.

## Output format

JSON Lines: one JSON object per line, no surrounding array, no commas between lines, and no prose, headings, or code fences anywhere in the response. Each line has exactly two keys:

    {"invocation": "<the full command string>", "config": <a CommandConfig object>}

`invocation` is the command exactly as it would be typed, including the command name.

`config` conforms to this JSON schema:

```json
{{config_schema}}
```

## The exact shape v1 writes — match it field for field

The schema says what is allowed; this says what v1 actually produces, and your output must
look the same. Two real configurations, exactly as v1 wrote them:

```json
{{config_examples}}
```

What each field is:

- `name` — the command.
- `body` — one node per argument group, in command-line order. Each node has `flag` (the flag
  spelling, or `null` for a positional operand), `args` (the values that follow it, one object
  each), `flag_followed_by_equals`, `node_type` (always `"args"`), `arity` (`"?"`, `"*"`,
  `"+"`, or a number, as in the specification), `symbol` and `true_string`.
- each entry of `args` carries `value`, `arg_type` and `true_string`, plus the fields its
  type needs (`relative`, `sandbox`, `content`, `parent_exists`). `arg_type` is one of:
  {{arg_types}}
- `string` — the same invocation before any environment was attached: `name`, and a `body` of
  the same nodes, each with `flag`, `args` holding only `value` (plus `relative` and
  `relation` for a path), `flag_followed_by_equals`, `arity`, `symbol` and `identifier`.
  Never leave it empty.
- `symbol` is `FLAG<flag>_<id>` for a flag node and `PATH_<id>` for an operand, where `<id>`
  is five capital letters chosen at random, the same `<id>` in `identifier` and in the
  node's `symbol` under `string`.
- `stdin` — one of the standard-input values given below.
- `true_string` — on the configuration, the full command line; on a node, that node's text;
  on an argument, its value.

Write every flag as an `args` node — `flag` set to its spelling, one argument
`{"value": "", "arg_type": "no_env", "true_string": ""}` when it takes no value — exactly as the
`ls -a` example shows. Never write a flag as a `"node_type": "flag"` node, even though the schema
allows one: v1 does not.

If you cannot fit every invocation in one response, stop at the end of a complete line and say nothing else; you will be asked to continue from there. Never abbreviate, summarize, or write a placeholder line standing for invocations you have not enumerated.
