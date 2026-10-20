from pash_annotations.annotation_generation.annotation_generators.InputOutputInfoGenerator_Interface import InputOutputInfoGeneratorInterface


class InputOutputInfoGeneratorGrep(InputOutputInfoGeneratorInterface):

    # GNU grep 3.11:  grep [OPTION]... PATTERNS [FILE]...
    #
    # Inputs:
    #   * The patterns come from the first operand, unless at least one -e/--regexp or
    #     -f/--file is given; then every operand is a FILE.
    #   * -f FILE is a configuration input (typed CONFIG_INPUT by grep.json);
    #     --exclude-from FILE is typed EXCLUDES_FROM_INPUT there.
    #   * With no FILE operand grep reads standard input, except when searching
    #     recursively (-r, -R), where it reads the working directory instead.
    #     (-d recurse / --directories=recurse behaves like -r as well; its argument
    #     cannot be inspected through the interface used here, so that case is
    #     over-approximated as reading standard input.)
    #   * --include/--exclude/--exclude-dir only filter which files are searched and
    #     are ignored here, which over-approximates the set of inputs.
    # Outputs:
    #   * grep only ever writes to standard output; -q/--quiet/--silent suppresses it.
    #     (--help and -V also write to standard output but are assumed not to occur in
    #     scripts that are being parallelised.)

    def generate_info(self) -> None:
        if not self.does_flag_option_list_contain_at_least_one_of(["-q", "--quiet", "--silent"]):
            self.set_implicit_use_of_stdout()

        recursive = self.does_flag_option_list_contain_at_least_one_of(
            ["-r", "--recursive", "-R", "--dereference-recursive"])

        if self.does_flag_option_list_contain_at_least_one_of(["-e", "--regexp", "-f", "--file"]):
            # patterns are given by options: every operand is an input file
            number_of_files = self.get_operand_list_length()
            self.all_operands_are_streaming_inputs()  # also fine if there are none
        else:
            # the first operand is PATTERNS, the rest are input files
            self.set_first_operand_as_config_arg_type_string()
            number_of_files = self.get_operand_list_length() - 1
            self.all_but_first_operand_is_streaming_input()

        if number_of_files <= 0 and not recursive:
            self.set_implicit_use_of_stdin()
