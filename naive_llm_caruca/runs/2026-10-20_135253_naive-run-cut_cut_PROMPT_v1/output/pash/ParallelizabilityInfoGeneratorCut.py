from pash_annotations.annotation_generation.annotation_generators.ParallelizabilityInfoGenerator_Interface import ParallelizabilityInfoGeneratorInterface


class ParallelizabilityInfoGeneratorCut(ParallelizabilityInfoGeneratorInterface):

    # list_of_all_flags = ["-n", "--complement", "-s", "-z", "--help", "--version"]
    # list_of_all_options = ["-b", "-c", "-d", "-f", "--output-delimiter"]

    # Which ones do affect parallelizability?
    # cut processes every line independently of all other lines and keeps the
    # input order, so any line-based split with plain concatenation is exact:
    # consecutive chunks and round robin, both with the sequential command and conc.
    # -z makes the record terminator NUL instead of newline; PaSh's splitters work
    # on newline-terminated lines, so we do not parallelize in that case.
    # Output is order-dependent, so it is not commutative.

    def generate_info(self) -> None:
        if not self.does_flag_option_list_contain_at_least_one_of(["-z", "--zero-terminated"]):
            self.append_to_parallelizer_list_cc_seq_conc()
            self.append_to_parallelizer_list_rr_seq_conc()
