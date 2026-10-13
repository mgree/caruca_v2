from pash_annotations.annotation_generation.annotation_generators.ParallelizabilityInfoGenerator_Interface import ParallelizabilityInfoGeneratorInterface


class ParallelizabilityInfoGeneratorGrep(ParallelizabilityInfoGeneratorInterface):

    # Every spelling is listed, for the same reason as in InputOutputInfoGeneratorGrep.
    QUIET_FLAGS = ["-q", "--quiet", "--silent"]
    MAX_COUNT_OPTIONS = ["-m", "--max-count"]
    CONTEXT_OPTIONS = ["-A", "--after-context", "-B", "--before-context", "-C", "--context"]
    # -NUM is the same as -C NUM, and the parser table lists each digit as its own flag
    CONTEXT_FLAGS = [f"-{digit}" for digit in "0123456789"]
    # counts, file lists, and line numbers or offsets depend on the whole input, not on one part of it
    PER_INPUT_OUTPUT_FLAGS = ["-c", "--count", "-l", "--files-with-matches", "-L", "--files-without-match",
                              "-n", "--line-number", "-b", "--byte-offset"]
    # -z ends records with NUL, so splitting on newlines would cut records apart
    NULL_DATA_FLAGS = ["-z", "--null-data"]
    PATTERN_OPTIONS = ["-e", "--regexp", "-f", "--file"]
    RECURSIVE_FLAGS = ["-r", "-R", "--recursive", "--dereference-recursive"]
    DIRECTORY_OPTIONS = ["-d", "--directories"]
    DIRECTORY_ACTIONS = ["read", "skip", "recurse"]

    def generate_info(self) -> None:
        if self.can_split_input():
            # each part is searched on its own, and the parts' outputs are joined in order
            self.append_to_parallelizer_list_cc_seq_conc()
            self.append_to_parallelizer_list_rr_seq_conc()

    def can_split_input(self) -> bool:
        # an option the parser did not know is left among the operands, so the rest of the invocation is unclear
        if self.has_unrecognised_option():
            return False
        if self.does_flag_option_list_contain_at_least_one_of(self.QUIET_FLAGS + self.MAX_COUNT_OPTIONS +
                                                              self.CONTEXT_OPTIONS + self.CONTEXT_FLAGS +
                                                              self.PER_INPUT_OUTPUT_FLAGS + self.NULL_DATA_FLAGS):
            return False
        # the split is only sound when there is one input stream: standard input, or a single FILE
        # (several files, or a directory walk, put file names into the output)
        if self.is_recursive():
            return False
        if self.does_flag_option_list_contain_at_least_one_of(self.PATTERN_OPTIONS):
            file_count = self.get_operand_list_length()
        elif self.get_operand_list_length() > 0:
            file_count = self.get_operand_list_length() - 1  # the first operand is PATTERNS
        else:
            return False  # no pattern at all
        return file_count <= 1

    def has_unrecognised_option(self) -> bool:
        # a leftover operand starting with '-' is an option the parser did not know (or a '--')
        return any(operand.get_name().startswith("-") and operand.get_name() != "-"
                   for operand in self.cmd_inv.operand_list)

    def is_recursive(self) -> bool:
        # -r, -R and -d ACTION all set how directories are handled, and the last one given wins
        recursive = False
        for flag_option in self.cmd_inv.flag_option_list:
            name = flag_option.get_name()
            if name in self.RECURSIVE_FLAGS:
                recursive = True
            elif name in self.DIRECTORY_OPTIONS:
                recursive = self.is_recursing_action(flag_option.get_arg())
        return recursive

    def is_recursing_action(self, action: str) -> bool:
        # grep accepts any prefix of an action name that matches only one action
        matches = [name for name in self.DIRECTORY_ACTIONS if name.startswith(action)]
        return matches == ["recurse"]
