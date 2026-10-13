from pash_annotations.annotation_generation.annotation_generators.InputOutputInfoGenerator_Interface import InputOutputInfoGeneratorInterface
from pash_annotations.datatypes.BasicDatatypes import Option


class InputOutputInfoGeneratorGrep(InputOutputInfoGeneratorInterface):

    # list_of_all_flags = ["-V", "--help", "-E", "-F", "-G", "-P", "-i", "--no-ignore-case", "-v", "-w",
    #                      "-x", "-y", "-c", "-L", "-l", "-o", "-q", "-s", "-b", "-H", "-h", "-n", "-T", "-Z",
    #                      "--no-group-separator", "-a", "-I", "-r", "-R", "--line-buffered", "-U", "-z"]
    # list_of_all_options = ["-e", "-f", "--color", "-m", "--label", "-A", "-B", "-C", "--group-separator",
    #                        "--binary-files", "-D", "-d", "--exclude", "--exclude-from", "--exclude-dir", "--include"]

    # Which ones do affect input/output?
    # -f affects input; -f - reads the patterns from standard input
    # -r actually does not really affect both since files and directories are both identified by their name
    # for now, we ignore --exclude, --exclude-from, --exclude-dir, and --include and, thus, over-approximate
    # for now, we ignore -D/-d with actions
    # with -r and no file operand grep searches the working directory, not standard input; we keep
    # standard input as an over-approximation here

    def generate_info(self) -> None:
        # --help and --version overrules -q (and no actual result returned) but we assume no help/version
        if not self.does_flag_option_list_contain_at_least_one_of(["-q"]):
            self.set_implicit_use_of_stdout()
        # case analysis how script is provided
        if self.does_flag_option_list_contain_at_least_one_of(["-e", "-f"]):
            if self.get_operand_list_length() == 0:
                self.set_implicit_use_of_stdin()
            else:
                self.all_operands_are_streaming_inputs() # this is true also if empty
        else:
            self.set_first_operand_as_config_arg_type_string()
            if self.get_operand_list_length() == 1:
                self.set_implicit_use_of_stdin()
            else:
                self.all_but_first_operand_is_streaming_input()
        # the pattern file given as "-f -" is read from standard input
        if any(isinstance(flagoption, Option) and flagoption.get_name() == "-f" and flagoption.get_arg() == "-"
               for flagoption in self.cmd_inv.flag_option_list):
            self.set_implicit_use_of_stdin()
        # a lone "-" operand names standard input
        if any(operand.get_name() == "-" for operand in self.cmd_inv.operand_list):
            self.set_implicit_use_of_stdin()
