from caruca.ir.syntax import *

# Syntax description of GNU grep 3.11 (/usr/bin/grep).
#
# grep has two ways of receiving its patterns:
#   grep [OPTION]... PATTERNS [FILE]...            (patterns are the first operand)
#   grep [OPTION]... -e PATTERNS|-f FILE ... [FILE]...  (patterns come from options; every
#                                                   operand is a file)
# They are given below as two alternative syntaxes that share one option list.
#
# Not expressible in this format and therefore omitted:
#   * "-NUM", the shorthand for "--context=NUM" (e.g. "grep -2 pat f").
#   * "--color"/"--colour" may also be given without "=WHEN" (meaning "auto").
#   * At least one of -e/-f must be present in the second syntax.

_common_options = [
    Flag("--help"),
    Flag("-V", alias=["--version"]),
    # pattern selection and interpretation (mutually exclusive matchers)
    Flag("-E", alias=["--extended-regexp"]),
    Flag("-F", alias=["--fixed-strings"]),
    Flag("-G", alias=["--basic-regexp"]),
    Flag("-P", alias=["--perl-regexp"]),
    Flag("-i", alias=["--ignore-case", "-y"]),  # -y is an obsolete synonym
    Flag("--no-ignore-case"),
    Flag("-v", alias=["--invert-match"]),
    Flag("-w", alias=["--word-regexp"]),
    Flag("-x", alias=["--line-regexp"]),
    Flag("-z", alias=["--null-data"]),
    # miscellaneous
    Flag("-s", alias=["--no-messages"]),
    # output control
    Integer(flag="-m", alias=["--max-count"]),  # negative NUM means "no limit"
    Flag("-b", alias=["--byte-offset"]),
    Flag("-u", alias=["--unix-byte-offsets"]),  # obsolete, accepted with a warning
    Flag("-n", alias=["--line-number"]),
    Flag("--line-buffered"),
    Flag("-H", alias=["--with-filename"]),
    Flag("-h", alias=["--no-filename"]),
    String(flag="--label"),
    Flag("-o", alias=["--only-matching"]),
    Flag("-q", alias=["--quiet", "--silent"]),
    Selection(
        flag="--binary-files",
        choices=["binary", "text", "without-match"],
    ),
    Flag("-a", alias=["--text"]),
    Flag("-I"),
    Selection(
        flag="-d", alias=["--directories"], choices=["read", "recurse", "skip"]
    ),
    Selection(flag="-D", alias=["--devices"], choices=["read", "skip"]),
    Flag("-r", alias=["--recursive"]),
    Flag("-R", alias=["--dereference-recursive"]),
    Glob(flag="--include", arity=Arity.ZERO_OR_MORE),
    Glob(flag="--exclude", arity=Arity.ZERO_OR_MORE),
    Path(flag="--exclude-from", arity=Arity.ZERO_OR_MORE),
    Glob(flag="--exclude-dir", arity=Arity.ZERO_OR_MORE),
    Flag("-L", alias=["--files-without-match"]),
    Flag("-l", alias=["--files-with-matches"]),
    Flag("-c", alias=["--count"]),
    Flag("-T", alias=["--initial-tab"]),
    Flag("-Z", alias=["--null"]),
    # context control
    Integer(flag="-B", alias=["--before-context"], min=0),
    Integer(flag="-A", alias=["--after-context"], min=0),
    Integer(flag="-C", alias=["--context"], min=0),
    Separator(flag="--group-separator"),
    Flag("--no-group-separator"),
    Selection(
        flag="--color",
        alias=["--colour"],
        flag_followed_by_equals=True,
        choices=["never", "always", "auto"],
    ),
    Flag("-U", alias=["--binary"]),
]

_pattern_options = [
    Regex(flag="-e", alias=["--regexp"], arity=Arity.ZERO_OR_MORE),
    Path(flag="-f", alias=["--file"], arity=Arity.ZERO_OR_MORE, dash_as_stdin=True),
]

grep_syntax_spec: list[SyntaxSpecification] = [
    # grep [OPTION]... PATTERNS [FILE]...
    [
        list(_common_options),
        [
            Regex(arity=Arity.EXACTLY_ONE),  # PATTERNS (newline-separated)
            Path(arity=Arity.ZERO_OR_MORE, dash_as_stdin=True),  # [FILE]...
        ],
    ],
    # grep [OPTION]... (-e PATTERNS | -f FILE)... [FILE]...
    [
        list(_common_options) + _pattern_options,
        [
            Path(arity=Arity.ZERO_OR_MORE, dash_as_stdin=True),  # [FILE]...
        ],
    ],
]
