from caruca.ir.syntax import *

# cut OPTION... [FILE]...
#
# Exactly one of -b/--bytes, -c/--characters or -f/--fields must be given, and it
# may be given only once ("only one list may be specified" otherwise). This is
# modelled as three alternative syntaxes, one per selector, with the selector at
# Arity.EXACTLY_ONE. The remaining options are common to all three.


def _common_options() -> list:
    return [
        Char(flag="-d", alias=["--delimiter"], flag_followed_by_equals=True),  # DELIM, single character
        Flag("-n"),  # ignored
        Flag("--complement"),
        Flag("-s", alias=["--only-delimited"]),
        Separator(flag="--output-delimiter", flag_followed_by_equals=True),  # STRING
        Flag("-z", alias=["--zero-terminated"]),
        Flag("--help"),
        Flag("--version"),
    ]


def _operands() -> list:
    # With no FILE, or when FILE is -, read standard input.
    return [Path(arity=Arity.ZERO_OR_MORE, dash_as_stdin=True)]


cut_syntax_spec: list[SyntaxSpecification] = [
    # cut -b LIST ...
    [
        [
            Range(flag="-b", alias=["--bytes"], flag_followed_by_equals=True, arity=Arity.EXACTLY_ONE),
            *_common_options(),
        ],
        _operands(),
    ],
    # cut -c LIST ...
    [
        [
            Range(flag="-c", alias=["--characters"], flag_followed_by_equals=True, arity=Arity.EXACTLY_ONE),
            *_common_options(),
        ],
        _operands(),
    ],
    # cut -f LIST ...
    [
        [
            Range(flag="-f", alias=["--fields"], flag_followed_by_equals=True, arity=Arity.EXACTLY_ONE),
            *_common_options(),
        ],
        _operands(),
    ],
]
