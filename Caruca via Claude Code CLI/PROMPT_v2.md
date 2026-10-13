# Task: describe the shell command `{{COMMAND}}` for downstream tools

## Objective

Produce a machine-readable description of the shell command `{{COMMAND}}` so that other programs can
understand it without ever running it themselves. One such program is PaSh, a tool that rewrites shell
scripts to run faster. Programs like PaSh need two things about a command: what command lines it accepts,
and how a given invocation behaves with respect to its inputs and outputs.

## Deliverable

Write two files into the `output/` directory of this folder:

1. `output/{{COMMAND}}.py` — a **syntax description**: which options the command accepts, what value each
   option takes, and what positional operands it takes. The file format is specified in
   [formats/syntax_description.md](formats/syntax_description.md).

2. `output/{{COMMAND}}.json` — a **behaviour annotation**: for each shape of invocation, what the command
   reads, what it writes, and which behaviour class it falls into. The file format is specified in
   [formats/pash_annotation.md](formats/pash_annotation.md).

Both files must follow their format exactly, because they are read by other programs, not by people.

## Examples of finished output

The `samples/` directory holds both files for four other commands, exactly as a downstream tool expects
them:

| Command | Syntax description | Behaviour annotation |
|---|---|---|
| `tee`  | [samples/tee/tee.py](samples/tee/tee.py)   | [samples/tee/tee.json](samples/tee/tee.json)   |
| `bc`   | [samples/bc/bc.py](samples/bc/bc.py)       | [samples/bc/bc.json](samples/bc/bc.json)       |
| `grep` | [samples/grep/grep.py](samples/grep/grep.py) | [samples/grep/grep.json](samples/grep/grep.json) |
| `rm`   | [samples/rm/rm.py](samples/rm/rm.py)       | [samples/rm/rm.json](samples/rm/rm.json)       |

## How the description must be established

- The command's parameters and its behaviour must be derived from **executing the command**, across
  all of its variations, not from memory or general knowledge of what the command does.
- Treat that probing as an experiment. Consider whether each observation is repeatable, and whether
  the result would be reproducible by someone repeating the same runs.
- Consider which operating system and which version of the command you are describing. Commands of
  this kind (the Unix core utilities and their relatives) differ in their options and arguments
  between Unix flavours and between versions, so establish which one is in front of you and state it
  in your report alongside the two files.

## Scope

The command to describe in this session is `{{COMMAND}}`. How you arrive at the two files is entirely up
to you. When both files are written, report what you did and anything you are unsure about.
