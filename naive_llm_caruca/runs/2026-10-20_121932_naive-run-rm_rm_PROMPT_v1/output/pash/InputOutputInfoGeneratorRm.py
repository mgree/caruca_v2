from pash_annotations.annotation_generation.annotation_generators.InputOutputInfoGenerator_Interface import InputOutputInfoGeneratorInterface


class InputOutputInfoGeneratorRm(InputOutputInfoGeneratorInterface):

    # list_of_all_flags = ["-f", "-i", "-I", "--one-file-system", "--no-preserve-root",
    #                      "-r", "-d", "-v", "--help", "--version"]
    # list_of_all_options = ["--interactive", "--preserve-root"]

    # rm never reads its operands as a data stream and never reads stdin as
    # data (only for interactive prompts, which are not a data input).
    # Every operand is a path that is removed, i.e. a non-stream output.
    # With -v, messages go to stdout; with --help/--version stdout is written
    # and nothing is removed.  No option changes the operand classification.

    def generate_info(self) -> None:
        self.all_operands_are_other_outputs()
        if self.does_flag_option_list_contain_at_least_one_of(["-v", "--help", "--version"]):
            self.set_implicit_use_of_stdout()
