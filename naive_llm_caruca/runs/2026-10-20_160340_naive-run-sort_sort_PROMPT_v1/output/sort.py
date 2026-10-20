from caruca.ir.syntax import *

# GNU coreutils 9.4 sort(1).
#
#   sort [OPTION]... [FILE]...
#   sort [OPTION]... --files0-from=F
#
# Verified against /usr/bin/sort:
#   * -o/--output may be given at most once ("multiple output files specified").
#   * -k/--key and -T/--temporary-directory may be repeated; each occurrence adds a key / directory.
#   * --check takes its value only in the "--check=WORD" form; a bare "--check" is the same as -c and
#     the following word is an operand.  This is modelled as rm's --preserve-root is: a Selection whose
#     empty choice stands for the bare spelling.
#   * -c/-C/--check accept at most one FILE operand and are incompatible with -o.
#   * --files0-from=F cannot be combined with FILE operands; "-" means standard input.
#   * -t/--field-separator accepts exactly one character or the two-character spelling '\0'.
#   * -S/--buffer-size accepts an integer with an optional suffix %, b, K, M, G, T, P, E, Z, Y, R, Q.
#   * --batch-size must be >= 2; --parallel must be >= 1.
#   * -y is an obsolete Solaris-compatibility option that sort accepts and ignores.

sort_syntax_spec: list[SyntaxSpecification] = [
    [
        [
            # Ordering options
            Flag("-b", alias=["--ignore-leading-blanks"]),
            Flag("-d", alias=["--dictionary-order"]),
            Flag("-f", alias=["--ignore-case"]),
            Flag("-g", alias=["--general-numeric-sort"]),
            Flag("-i", alias=["--ignore-nonprinting"]),
            Flag("-M", alias=["--month-sort"]),
            Flag("-h", alias=["--human-numeric-sort"]),
            Flag("-n", alias=["--numeric-sort"]),
            Flag("-R", alias=["--random-sort"]),
            Path(flag="--random-source", flag_followed_by_equals=True),
            Flag("-r", alias=["--reverse"]),
            Selection(
                flag="--sort",
                choices=["general-numeric", "human-numeric", "month", "numeric", "random", "version"],
                flag_followed_by_equals=True,
            ),
            Flag("-V", alias=["--version-sort"]),
            # Other options
            Integer(flag="--batch-size", flag_followed_by_equals=True, min=2),
            Flag("-c"),
            Flag("-C"),
            Selection(
                flag="--check",
                choices=["", "diagnose-first", "quiet", "silent"],
                flag_followed_by_equals=True,
            ),
            Command(flag="--compress-program", flag_followed_by_equals=True),
            Flag("--debug"),
            Path(flag="--files0-from", flag_followed_by_equals=True, dash_as_stdin=True),
            String(flag="-k", alias=["--key"], flag_followed_by_equals=True, arity=Arity.ZERO_OR_MORE),  # KEYDEF
            Flag("-m", alias=["--merge"]),
            Path(flag="-o", alias=["--output"], flag_followed_by_equals=True),
            Flag("-s", alias=["--stable"]),
            Size(flag="-S", alias=["--buffer-size"], flag_followed_by_equals=True),
            Char(flag="-t", alias=["--field-separator"], flag_followed_by_equals=True),
            Path(flag="-T", alias=["--temporary-directory"], flag_followed_by_equals=True, arity=Arity.ZERO_OR_MORE),
            Integer(flag="--parallel", flag_followed_by_equals=True, min=1),
            Flag("-u", alias=["--unique"]),
            Flag("-z", alias=["--zero-terminated"]),
            Flag("-y"),  # obsolete, accepted and ignored
            Flag("--help"),
            Flag("--version"),
        ],
        [
            Path(arity=Arity.ZERO_OR_MORE, dash_as_stdin=True),  # [FILE...]
        ],
    ]
]
