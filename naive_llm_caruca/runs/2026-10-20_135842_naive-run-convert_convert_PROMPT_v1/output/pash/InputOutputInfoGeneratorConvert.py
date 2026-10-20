from pash_annotations.annotation_generation.annotation_generators.InputOutputInfoGenerator_Interface import InputOutputInfoGeneratorInterface


class InputOutputInfoGeneratorConvert(InputOutputInfoGeneratorInterface):

    # ImageMagick 6 `convert`:
    #     convert [options...] input-file... [options...] output-file
    #
    # Options are single words with one leading "-" (or "+"), no "=" form and no bundling;
    # they may appear anywhere between the operands.  The parser table (convert.json)
    # lists every flag and every option that takes an argument.
    #
    # Which flags/options affect input/output?
    # - operands: every operand but the last is an image read in full (not streamed);
    #   the last operand is the image file that is written.  "-" or "fmt:-" as an input
    #   operand reads standard input; "-", "fmt:-" or "info:-" as the output operand
    #   writes standard output.  (A single operand only prints the version banner.)
    # - -write FILE writes an extra image file (typed OTHER_OUTPUT in convert.json);
    #   "-write png:-" / "-write info:-" writes to standard output instead.
    # - -cdl/-decipher/-encipher/-profile read a configuration file, and
    #   -clip-mask/-mask/-remap/-texture/-tile read an auxiliary image (typed in the table).
    # - -identify, -print, -verbose, -monitor(stderr), -list, -help and -version print to
    #   standard output; -format only matters together with -identify or "info:" output.
    # - "(" and ")" operands delimit an image sub-list; they are not files, and neither are
    #   pseudo-images such as "xc:red", "rose:" or "logo:".  The interface offers no
    #   per-operand marking, so these are over-approximated as "other" input files.
    # - If the parser left option words in the operand list (it stops at the first operand),
    #   those words are over-approximated as input files as well; the output decision
    #   (last operand) is unaffected.

    STDOUT_OPTIONS = ["-identify", "+identify", "-print", "-verbose", "-list", "-help", "-version"]

    @staticmethod
    def _operand_as_string(operand) -> str:
        for attr in ("get_name_as_string", "get_name", "name", "value"):
            value = getattr(operand, attr, None)
            if callable(value):
                value = value()
            if isinstance(value, str):
                return value
        return str(operand)

    @staticmethod
    def _is_std_descriptor(name: str) -> bool:
        # "-", "png:-", "info:-", ... all denote a standard stream
        return name == "-" or name.endswith(":-")

    def generate_info(self) -> None:
        n_operands = self.get_operand_list_length()
        if n_operands >= 2:
            self.all_but_last_operand_is_other_input()
            self.only_last_operand_is_other_output()
        elif n_operands == 1:
            # `convert file` alone reads nothing and prints the version banner
            self.set_all_operands_as_config_arg_type_string()
            self.set_implicit_use_of_stdout()
        else:
            # no operands at all: usage/version text on standard output
            self.set_implicit_use_of_stdout()

        operand_names = [self._operand_as_string(op) for op in self.cmd_inv.operand_list]
        # a "-" right after -write/+write is that option's argument, not an input operand
        write_targets = {index + 1 for index, name in enumerate(operand_names) if name in ("-write", "+write")}
        if n_operands >= 2:
            if any(self._is_std_descriptor(name) for index, name in enumerate(operand_names[:-1])
                   if index not in write_targets):
                self.set_implicit_use_of_stdin()
            if self._is_std_descriptor(operand_names[-1]):
                self.set_implicit_use_of_stdout()

        if self.does_flag_option_list_contain_at_least_one_of(self.STDOUT_OPTIONS):
            self.set_implicit_use_of_stdout()
        # the same, for option words the parser may have left among the operands
        for index, name in enumerate(operand_names[:-1]):
            if name in self.STDOUT_OPTIONS:
                self.set_implicit_use_of_stdout()
            if name in ("-write", "+write") and self._is_std_descriptor(operand_names[index + 1]):
                self.set_implicit_use_of_stdout()
        # -write with a standard-stream target also writes standard output
        for flag_option in self.get_flag_option_list_filtered_with(["-write", "+write"]):
            for attr in ("get_arg_as_string", "get_arg", "arg", "argument"):
                value = getattr(flag_option, attr, None)
                if callable(value):
                    value = value()
                if isinstance(value, str):
                    if self._is_std_descriptor(value):
                        self.set_implicit_use_of_stdout()
                    break
