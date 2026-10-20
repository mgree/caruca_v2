from pash_annotations.annotation_generation.annotation_generators.InputOutputInfoGenerator_Interface import InputOutputInfoGeneratorInterface


class InputOutputInfoGeneratorCut(InputOutputInfoGeneratorInterface):

    # list_of_all_flags = ["-n", "--complement", "-s", "-z", "--help", "--version"]
    # list_of_all_options = ["-b", "-c", "-d", "-f", "--output-delimiter"]

    # Which ones do affect input/output?
    # none: every option only changes which parts of each line are printed.
    # All operands are files read as a stream (a "-" operand means stdin);
    # with no operand, stdin is read. Output always goes to stdout.
    # (tested with GNU coreutils 9.4; --help/--version assumed not given)

    def generate_info(self) -> None:
        self.all_operands_are_streaming_inputs()
        self.if_no_operands_given_stdin_implicitly_used()
        self.set_implicit_use_of_stdout()
