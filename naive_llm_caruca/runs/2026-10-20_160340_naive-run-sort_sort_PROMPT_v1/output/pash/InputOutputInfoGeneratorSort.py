from pash_annotations.annotation_generation.annotation_generators.InputOutputInfoGenerator_Interface import InputOutputInfoGeneratorInterface


class InputOutputInfoGeneratorSort(InputOutputInfoGeneratorInterface):

    # list_of_all_flags = ["-b", "-d", "-f", "-g", "-i", "-M", "-h", "-n", "-R", "-r", "-V", "-c", "-C",
    #                      "--debug", "-m", "-s", "-u", "-z", "-y", "--help", "--version"]
    # list_of_all_options = ["--random-source", "--sort", "--batch-size", "--check", "--compress-program",
    #                        "--files0-from", "-k", "-o", "-S", "-t", "-T", "--parallel"]

    # Which ones do affect input/output?
    # -o FILE: the result is written to FILE instead of stdout (typed STREAM_OUTPUT from the parser table;
    #          verified: sort -o f f is allowed, sort reads f fully before writing)
    # -c/-C/--check: nothing is written to stdout, only a diagnostic to stderr and the exit status;
    #          at most one FILE operand, -o is rejected by sort
    # --files0-from=F: the inputs are the files named in F (typed CONTAINER_FOR_INPUT from the parser
    #          table); sort rejects FILE operands together with it; F may be - for stdin
    # --random-source=FILE: read as configuration (typed CONFIG_INPUT from the parser table)
    # -T DIR: temporaries are created there (typed OTHER_OUTPUT from the parser table)
    # all other flags/options do not change which files are read or written

    def generate_info(self) -> None:
        # assumption: --help and --version are not given
        # inputs
        if self.does_flag_option_list_contain_at_least_one_of(["--files0-from"]):
            # the data comes from the files listed in F, not from operands (sort rejects operands here);
            # if F is "-" the list of names, not the data, is read from stdin, so stdin is not a stream input
            pass
        else:
            # with no FILE, or when FILE is -, read standard input
            self.if_no_operands_given_stdin_implicitly_used()
            self.all_operands_are_streaming_inputs()
        # outputs
        if self.does_flag_option_list_contain_at_least_one_of(["-c", "-C", "--check"]):
            # check mode only reports via stderr and the exit status; -o is not allowed with it
            pass
        elif self.does_flag_option_list_contain_at_least_one_of(["-o", "--output"]):
            # output goes to the file given to -o (already typed as STREAM_OUTPUT), not to stdout
            pass
        else:
            self.set_implicit_use_of_stdout()
