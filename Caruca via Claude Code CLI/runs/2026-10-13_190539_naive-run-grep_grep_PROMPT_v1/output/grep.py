from caruca.ir.syntax import *

# Options of GNU grep 3.11, from grep(1) and checked against the binary. Every option that takes a value
# may be repeated (the last value wins), so those nodes are ZERO_OR_MORE. grep's -E/-F/-G/-P are mutually
# exclusive ("conflicting matchers"); that is not expressible here.
_grep_options = [
    Flag("--help"),
    Flag("-V", alias=["--version"]),
    Flag("-E", alias=["--extended-regexp"]),
    Flag("-F", alias=["--fixed-strings"]),
    Flag("-G", alias=["--basic-regexp"]),
    Flag("-P", alias=["--perl-regexp"]),
    Flag("-i", alias=["--ignore-case", "-y"]),  # -y is an undocumented synonym of -i
    Flag("--no-ignore-case"),
    Flag("-v", alias=["--invert-match"]),
    Flag("-w", alias=["--word-regexp"]),
    Flag("-x", alias=["--line-regexp"]),
    Flag("-c", alias=["--count"]),
    # --color takes its WHEN only in the attached form (--color=WHEN); a bare --color means auto.
    Selection(
        flag="--color",
        alias=["--colour"],
        choices=["never", "always", "auto"],
        flag_followed_by_equals=True,
        arity=Arity.ZERO_OR_MORE,
    ),
    Flag("-L", alias=["--files-without-match"]),
    Flag("-l", alias=["--files-with-matches"]),
    Integer(flag="-m", alias=["--max-count"], arity=Arity.ZERO_OR_MORE),  # any negative value means no limit
    Flag("-o", alias=["--only-matching"]),
    Flag("-q", alias=["--quiet", "--silent"]),
    Flag("-s", alias=["--no-messages"]),
    Flag("-b", alias=["--byte-offset"]),
    Flag("-H", alias=["--with-filename"]),
    Flag("-h", alias=["--no-filename"]),
    String(flag="--label", arity=Arity.ZERO_OR_MORE),
    Flag("-n", alias=["--line-number"]),
    Flag("-T", alias=["--initial-tab"]),
    Flag("-Z", alias=["--null"]),
    Flag("-u", alias=["--unix-byte-offsets"]),  # obsolete; grep accepts it with a warning
    Regex(flag="-e", alias=["--regexp"], arity=Arity.ZERO_OR_MORE),
    Path(flag="-f", alias=["--file"], dash_as_stdin=True, arity=Arity.ZERO_OR_MORE),
    Integer(flag="-A", alias=["--after-context"], min=0, arity=Arity.ZERO_OR_MORE),
    Integer(flag="-B", alias=["--before-context"], min=0, arity=Arity.ZERO_OR_MORE),
    Integer(flag="-C", alias=["--context"], min=0, arity=Arity.ZERO_OR_MORE),  # also -NUM, not expressible
    Separator(flag="--group-separator", arity=Arity.ZERO_OR_MORE),
    Flag("--no-group-separator"),
    Flag("-a", alias=["--text"]),
    Flag("-I"),
    Selection(
        flag="--binary-files",
        choices=["binary", "text", "without-match"],
        arity=Arity.ZERO_OR_MORE,
    ),
    Selection(flag="-D", alias=["--devices"], choices=["read", "skip"], arity=Arity.ZERO_OR_MORE),
    Selection(
        flag="-d",
        alias=["--directories"],
        choices=["read", "skip", "recurse"],
        arity=Arity.ZERO_OR_MORE,
    ),
    Glob(flag="--exclude", arity=Arity.ZERO_OR_MORE),
    Path(flag="--exclude-from", arity=Arity.ZERO_OR_MORE),
    Glob(flag="--exclude-dir", arity=Arity.ZERO_OR_MORE),
    Glob(flag="--include", arity=Arity.ZERO_OR_MORE),
    Flag("-r", alias=["--recursive"]),
    Flag("-R", alias=["--dereference-recursive"]),
    Flag("--line-buffered"),
    Flag("-U", alias=["--binary"]),
    Flag("-z", alias=["--null-data"]),
]

grep_syntax_spec: list[SyntaxSpecification] = [
    # grep [OPTION...] PATTERNS [FILE...]
    [
        _grep_options,
        [
            Regex(arity=Arity.EXACTLY_ONE),  # PATTERNS
            Path(arity=Arity.ZERO_OR_MORE, dash_as_stdin=True),  # [FILE...]
        ],
    ],
    # grep [OPTION...] -e PATTERNS ... [FILE...]  and  grep [OPTION...] -f PATTERN_FILE ... [FILE...]
    [
        _grep_options,
        [
            Path(arity=Arity.ZERO_OR_MORE, dash_as_stdin=True),  # [FILE...]
        ],
    ],
    # grep --help  and  grep -V
    [
        [
            Flag("--help"),
            Flag("-V", alias=["--version"]),
        ],
        [],
    ],
]
