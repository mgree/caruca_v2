from caruca.ir.syntax import (
    Flag,
    Selection,
    Path,
    Arity,
    SyntaxSpecification,
)

# rm (GNU coreutils 9.4): rm [OPTION]... [FILE]...
# Verified against /usr/bin/rm:
#   * --interactive takes its value only as --interactive=WHEN; a bare
#     --interactive means "always", and "--interactive never" treats "never"
#     as a file operand.  Accepted values (from the binary's error message):
#     never/no/none, once, always/yes.
#   * --preserve-root is accepted bare or as --preserve-root=all; any other
#     value is rejected.
#   * The operand list may be empty: "rm -f" exits 0 without operands, while
#     "rm" alone reports "missing operand".  The syntax is therefore
#     ZERO_OR_MORE paths.
rm_syntax_spec: list[SyntaxSpecification] = [
    [
        [
            Flag("-f", alias=["--force"]),
            Flag("-i"),
            Flag("-I"),
            Selection(
                flag="--interactive",
                choices=["never", "no", "none", "once", "always", "yes"],
                flag_followed_by_equals=True,
            ),
            Flag("--one-file-system"),
            Flag("--no-preserve-root"),
            Selection(
                flag="--preserve-root",
                choices=["", "all"],
                flag_followed_by_equals=True,
            ),
            Flag("-r", alias=["-R", "--recursive"]),
            Flag("-d", alias=["--dir"]),
            Flag("-v", alias=["--verbose"]),
            Flag("--help"),
            Flag("--version"),
        ],
        [Path(arity=Arity.ZERO_OR_MORE)],
    ],
]
