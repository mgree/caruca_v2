from caruca.ir.syntax import *

dirname_syntax_spec: list[SyntaxSpecification] = [
    [
        [
            Flag("-z", alias=["--zero"]),
            Flag("--help"),
            Flag("--version"),
        ],
        # Each NAME is a path string that is manipulated textually; dirname never opens it,
        # so a nonexistent path (or a lone "-") is accepted and "-" does not mean stdin.
        [Path(arity=Arity.AT_LEAST_ONE)],
    ]
]
