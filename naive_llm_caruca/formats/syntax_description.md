# Format: the syntax description (`<command>.py`)

This file states the command's argument syntax: the options it accepts, the type of argument each
option takes, and the types of its operands. It is a Python module that defines one variable.
Downstream programs import the module and read that variable; they do not call anything else in it.

## Shape of the file

```python
from caruca.ir.syntax import *

<command>_syntax_spec: list[SyntaxSpecification] = [
    [                      # one syntax (a command may have several alternative syntaxes)
        [ ...option nodes... ],      # position 0
        [ ...positional nodes... ],  # position 1
    ],
]
```

- The file is named `<command>.py` and the variable is named `<command>_syntax_spec`. Both use the
  command's name, so `tee.py` defines `tee_syntax_spec`.
- All constructors come from the module `caruca.ir.syntax`.
- `<command>_syntax_spec` is a list of **syntaxes**. Each syntax is one way the command line can be laid
  out; most commands have exactly one.
- A syntax is a list of **positions**, in order. Each position is a list of **argument nodes** allowed at
  that position. In every sample, position 0 holds the option nodes and position 1 holds the positional
  operands.

## Argument nodes

An argument node is one constructor call. Two kinds exist.

**`Flag(flag, alias=[...])`** — an option that takes no value, such as `-v` or `--verbose`. The first
argument is the option's spelling; `alias` lists other spellings of the same option.

**Value nodes** — anything that carries a value. The constructor name states the kind of value (see the
vocabulary below). Keyword arguments:

| Keyword | Meaning |
|---|---|
| `flag="-m"` | The node is an option that takes a value, written `-m VALUE`. Omit `flag` and the node is a positional operand instead. |
| `alias=["--max-count"]` | Other spellings of the same option. |
| `flag_followed_by_equals=True` | The value is attached with `=`, as in `--interactive=always`. |
| `choices=["never", "once", "always"]` | The allowed values, for `Selection` and `String`. |
| `arity=Arity.<name>` | How many times this node may appear on the command line (see below). |
| `dash_as_stdin=True` | On `Path` only: a lone `-` in this position means standard input. |

`Integer` also accepts `min=` and `max=` (an inclusive value range) and `suffixes=(...)`.
`List` describes a separator-joined list of values and accepts `of=<value node type>` and `separator=","`.

## Arity

`arity` says how many times a node may appear, not how many values it takes. The default is `OPTIONAL`.

| Name | Meaning |
|---|---|
| `Arity.OPTIONAL`, `Arity.ZERO_OR_ONE` | zero or one time (the default) |
| `Arity.EXACTLY_ONE` | exactly once |
| `Arity.EXACTLY_TWO` | exactly twice |
| `Arity.ZERO_OR_MORE` | any number of times, including none |
| `Arity.AT_LEAST_ONE`, `Arity.ONE_OR_MORE` | one or more times |

## Vocabulary of value nodes

Each name below is a constructor exported by `caruca.ir.syntax`. Names on the same line are the same type
under different names.

| Constructor | Value it stands for |
|---|---|
| `Path` | a file or directory path |
| `Integer`, `Int`, `Number`, `Pid`, `Duration` | an integer |
| `String`, `Other`, `User`, `Format` | free text; `Other` is the catch-all when nothing more specific fits |
| `Selection` | one value out of a fixed set given in `choices` |
| `List` | several values joined by a separator |
| `Regex` | a regular expression |
| `Glob` | a shell wildcard pattern such as `*.txt` |
| `Separator`, `Delimiter` | a delimiter string |
| `Char` | a single character |
| `Range` | a numeric range such as `1-2` or `1,3` |
| `Size` | a size with a unit suffix, such as `1k` or `1m` |
| `Permission` | a file permission such as `u+r` or `0755` |
| `OwnerGroup` | an `owner:group` pair |
| `Group` | a group name |
| `Signal` | a signal name or number |
| `Variable` | an environment variable name |
| `Command` | the name of another command |
| `Hostname` | a host name |
| `Filesystem` | a filesystem type such as `ext4` |
| `Date`, `DateTime` | a date or a date-time |
| `DateFormat` | a `strftime`-style date format |
| `TimeStyle` | a time style name such as `iso` or `full-iso` |
| `Expression` | an arithmetic expression |
| `PrintfFormat`, `SprintfFormat` | a `printf`-style format string |
| `Geometry` | a size or percentage such as `100x100` or `50%` |
| `SecurityContext`, `SecurityRange`, `SecurityRole`, `SecurityType` | SELinux security attributes |
