from caruca.ir.syntax import *

# Options accepted whatever supplies the pattern. Context counts (-A, -B, -C) must not be negative; -m
# also accepts a negative value, which means no limit. Options marked "undocumented" are not in grep --help
# but the binary accepts them.
_options = [
    Flag("--help"),
    Flag("-V", alias=["--version"]),
    Flag("-E", alias=["--extended-regexp"]),
    Flag("-F", alias=["--fixed-strings"]),
    Flag("-G", alias=["--basic-regexp"]),
    Flag("-P", alias=["--perl-regexp"]),
    Flag("-i", alias=["--ignore-case", "-y"]),  # -y: accepted but undocumented synonym of -i
    Flag("--no-ignore-case"),
    Flag("-w", alias=["--word-regexp"]),
    Flag("-x", alias=["--line-regexp"]),
    Flag("-z", alias=["--null-data"]),
    Flag("-s", alias=["--no-messages"]),
    Flag("-v", alias=["--invert-match"]),
    Integer(flag="-m", alias=["--max-count"]),
    Flag("-b", alias=["--byte-offset"]),
    Flag("-n", alias=["--line-number"]),
    Flag("--line-buffered"),
    Flag("-H", alias=["--with-filename"]),
    Flag("-h", alias=["--no-filename"]),
    String(flag="--label"),
    Flag("-o", alias=["--only-matching"]),
    Flag("-q", alias=["--quiet", "--silent"]),
    Selection(flag="--binary-files", choices=["binary", "without-match", "text"]),
    Flag("-a", alias=["--text"]),
    Flag("-I"),
    Selection(flag="-d", alias=["--directories"], choices=["read", "skip", "recurse"]),
    Selection(flag="-D", alias=["--devices"], choices=["read", "skip"]),
    Flag("-r", alias=["--recursive"]),
    Flag("-R", alias=["--dereference-recursive"]),
    Glob(flag="--include", arity=Arity.ZERO_OR_MORE),
    Glob(flag="--exclude", arity=Arity.ZERO_OR_MORE),
    Glob(flag="--exclude-dir", arity=Arity.ZERO_OR_MORE),
    Path(flag="--exclude-from", arity=Arity.ZERO_OR_MORE),
    Flag("-L", alias=["--files-without-match"]),
    Flag("-l", alias=["--files-with-matches"]),
    Flag("-c", alias=["--count"]),
    Flag("-T", alias=["--initial-tab"]),
    Flag("-Z", alias=["--null"]),
    Flag("-u", alias=["--unix-byte-offsets"]),  # accepted but undocumented and obsolete (prints a warning)
    Integer(flag="-B", alias=["--before-context"], min=0),
    Integer(flag="-A", alias=["--after-context"], min=0),
    Integer(flag="-C", alias=["--context"], min=0),
    Separator(flag="--group-separator"),
    Flag("--no-group-separator"),
    # --color takes its WHEN value only after '=' (a bare --color means auto), so it is two nodes.
    Flag("--color", alias=["--colour"]),
    Selection(
        flag="--color",
        alias=["--colour"],
        choices=["always", "yes", "force", "never", "no", "none", "auto", "tty", "if-tty"],
        flag_followed_by_equals=True,
    ),
    Flag("-U", alias=["--binary"]),
    # -NUM (context of NUM lines, e.g. -5) is not expressible here; it is listed in grep.json as -0 to -9.
]

grep_syntax_spec: list[SyntaxSpecification] = [
    # grep --help / grep -V: no pattern and no file
    [
        [Flag("--help"), Flag("-V", alias=["--version"])],
        [],
    ],
    # grep [OPTION...] PATTERNS [FILE...]
    [
        _options,
        [
            Regex(arity=Arity.EXACTLY_ONE),
            Path(arity=Arity.ZERO_OR_MORE, dash_as_stdin=True),
        ],
    ],
    # grep [OPTION...] -e PATTERNS ... [FILE...]
    [
        _options
        + [
            Regex(flag="-e", alias=["--regexp"], arity=Arity.AT_LEAST_ONE),
            Path(flag="-f", alias=["--file"], arity=Arity.ZERO_OR_MORE, dash_as_stdin=True),
        ],
        [Path(arity=Arity.ZERO_OR_MORE, dash_as_stdin=True)],
    ],
    # grep [OPTION...] -f PATTERN_FILE ... [FILE...]
    [
        _options
        + [
            Regex(flag="-e", alias=["--regexp"], arity=Arity.ZERO_OR_MORE),
            Path(flag="-f", alias=["--file"], arity=Arity.AT_LEAST_ONE, dash_as_stdin=True),
        ],
        [Path(arity=Arity.ZERO_OR_MORE, dash_as_stdin=True)],
    ],
]
