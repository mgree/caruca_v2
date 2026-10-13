# Format: the behaviour annotation (`<command>.json`)

This file tells a downstream program how a command behaves once it has been invoked a particular way:
what it reads, what it writes, and whether its work can be split up. It is a JSON document.

## Top level

```json
{
  "command": "<command>",
  "cases": [ ... ],
  "options": []
}
```

| Field | Meaning |
|---|---|
| `command` | The command's name. |
| `cases` | A list of cases (below). A downstream program picks the first case whose predicate matches the invocation it is looking at. |
| `options` | A list of strings. It is empty in every sample. |

## A case

```json
{
  "predicate": { ... },
  "pclass": "stateless",
  "inputs": [ ... ],
  "outputs": [ ... ],
  "true_str": "grep -v relpath_1",
  "comments": "..."
}
```

### `predicate`

A tree that selects which invocations the case applies to. Every node has an `operator` and a list of
`operands`; an operand is either another node, a string, or an integer. The operators that appear in the
samples:

| Operator | Operands | Matches an invocation when |
|---|---|---|
| `and` | nodes | every operand node matches |
| `exists` | option spellings (strings) | each listed option is present on the command line; an empty list places no requirement |
| `len_args_eq` | one integer | the number of non-option arguments equals the integer |

### `pclass`

The behaviour class, one of four strings. The class tells a downstream program what it may do with the
invocation.

| Value | Meaning to the consumer |
|---|---|
| `stateless` | Each line of input is handled independently. The input may be cut into pieces, each piece run separately, and the outputs joined back in order. |
| `pure` | The output depends only on the inputs and nothing else is changed, but the whole input is needed; a consumer may still run pieces in parallel if it knows how to combine the partial results for this command. |
| `non-pure` | Nothing outside the listed outputs is changed, but the work cannot be split up. |
| `side-effectful` | The invocation changes state beyond its standard output, for example by creating, writing, or removing files. |

### `inputs` and `outputs`

Lists of strings naming what the invocation reads and what it writes. The forms that appear in the
samples:

| Entry | Meaning |
|---|---|
| `stdin` | the standard input stream |
| `stdout` | the standard output stream |
| `args[0]`, `args[1]`, ... | the file named by the first, second, ... non-option argument |
| a literal file name such as `relpath_1.jpg` or `abspath_1.jpg` | a file read or written whose name was recorded as-is; `relpath_N` and `abspath_N` are placeholder names standing for a relative and an absolute path |
| `pipe:[12345]` | the identifier of an operating-system pipe that was open while this case was recorded; it names no file and has no meaning outside the run that produced it |

### `true_str`

One concrete command line that the case covers, written with the same placeholder names (`relpath_1`,
`abspath_1`) for path arguments.

### `comments`

Free text.
