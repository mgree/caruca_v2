from caruca.ir.syntax import *

# binwalk v2.3.3 (the installed binary; the man page is for 2.3.2 and lacks
# -0/--run-as and -1/--preserve-symlinks, which the binary does accept).
#
# Parsing notes, verified against the binary:
#   * All options are parsed with Python argparse, so a value may be given as
#     "-l 70", "-l70", "--length 70" or "--length=70", and unambiguous prefixes
#     of long options ("--len") are accepted.  Short flags may be bundled
#     ("-Bq").  Integers accept a base prefix ("-o 0x3E").
#   * -D, -R, -m, -x and -y may be repeated (argparse "append"); every other
#     option keeps only its last occurrence.
#   * Every word that is not a recognised option is a target file.  A lone
#     "-" is a literal file name, not standard input; binwalk never reads
#     stdin and prints its help (exit status 1) when no file is given.
#     Target files must be seekable regular files (pipes fail with
#     "Illegal seek").
#   * The hidden, API-only "--string" flag is deliberately omitted: it makes
#     the command crash when used from the shell.

binwalk_syntax_spec: list[SyntaxSpecification] = [
    [
        [
            # Signature scan options
            Flag("-B", alias=["--signature"]),
            String(flag="-R", alias=["--raw"], arity=Arity.ZERO_OR_MORE),
            Flag("-A", alias=["--opcodes"]),
            Path(flag="-m", alias=["--magic"], arity=Arity.ZERO_OR_MORE),
            Flag("-b", alias=["--dumb"]),
            Flag("-I", alias=["--invalid"]),
            Regex(flag="-x", alias=["--exclude"], arity=Arity.ZERO_OR_MORE),
            Regex(flag="-y", alias=["--include"], arity=Arity.ZERO_OR_MORE),
            # Extraction options
            Flag("-e", alias=["--extract"]),
            String(flag="-D", alias=["--dd"], arity=Arity.ZERO_OR_MORE),  # <type[:ext[:cmd]]>
            Flag("-M", alias=["--matryoshka"]),
            Integer(flag="-d", alias=["--depth"]),
            Path(flag="-C", alias=["--directory"]),
            Integer(flag="-j", alias=["--size"]),
            Integer(flag="-n", alias=["--count"]),
            User(flag="-0", alias=["--run-as"]),
            Flag("-1", alias=["--preserve-symlinks"]),
            Flag("-r", alias=["--rm"]),
            Flag("-z", alias=["--carve"]),
            Flag("-V", alias=["--subdirs"]),
            # Entropy options
            Flag("-E", alias=["--entropy"]),
            Flag("-F", alias=["--fast"]),
            Flag("-J", alias=["--save"]),
            Flag("-Q", alias=["--nlegend"]),
            Flag("-N", alias=["--nplot"]),
            Other(flag="-H", alias=["--high"]),  # floating-point threshold, e.g. 0.95
            Other(flag="-L", alias=["--low"]),  # floating-point threshold, e.g. 0.85
            # Binary diffing options
            Flag("-W", alias=["--hexdump"]),
            Flag("-G", alias=["--green"]),
            Flag("-i", alias=["--red"]),
            Flag("-U", alias=["--blue"]),
            Flag("-u", alias=["--similar"]),
            Flag("-w", alias=["--terse"]),
            # Raw compression options
            Flag("-X", alias=["--deflate"]),
            Flag("-Z", alias=["--lzma"]),
            Flag("-P", alias=["--partial"]),
            Flag("-S", alias=["--stop"]),
            # General options
            Integer(flag="-l", alias=["--length"]),
            Integer(flag="-o", alias=["--offset"]),
            Integer(flag="-O", alias=["--base"]),
            Integer(flag="-K", alias=["--block"]),
            Integer(flag="-g", alias=["--swap"]),
            Path(flag="-f", alias=["--log"]),
            Flag("-c", alias=["--csv"]),
            Flag("-t", alias=["--term"]),
            Flag("-q", alias=["--quiet"]),
            Flag("-v", alias=["--verbose"]),
            Flag("-h", alias=["--help"]),
            Regex(flag="-a", alias=["--finclude"]),
            Regex(flag="-p", alias=["--fexclude"]),
            Integer(flag="-s", alias=["--status"], min=0, max=65535),
        ],
        [
            # [FILE1] [FILE2] ...  With no file binwalk only prints its help.
            Path(arity=Arity.ZERO_OR_MORE),
        ],
    ]
]
