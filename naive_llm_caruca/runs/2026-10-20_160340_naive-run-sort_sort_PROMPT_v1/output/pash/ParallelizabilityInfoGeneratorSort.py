from pash_annotations.annotation_generation.annotation_generators.ParallelizabilityInfoGenerator_Interface import ParallelizabilityInfoGeneratorInterface
from pash_annotations.annotation_generation.datatypes.parallelizability.Parallelizer import \
    make_parallelizer_round_robin, make_parallelizer_consec_chunks
from pash_annotations.annotation_generation.datatypes.parallelizability.AggregatorSpec import \
    make_aggregator_spec_custom_2_ary_from_string_representation


class ParallelizabilityInfoGeneratorSort(ParallelizabilityInfoGeneratorInterface):

    # list_of_all_flags = ["-b", "-d", "-f", "-g", "-i", "-M", "-h", "-n", "-R", "-r", "-V", "-c", "-C",
    #                      "--debug", "-m", "-s", "-u", "-z", "-y", "--help", "--version"]
    # list_of_all_options = ["--random-source", "--sort", "--batch-size", "--check", "--compress-program",
    #                        "--files0-from", "-k", "-o", "-S", "-t", "-T", "--parallel"]

    # Which ones do affect parallelizability?
    # base-line: sort each part with the sequential command and merge the sorted parts with
    #   `sort -m <same ordering options>`; verified with the binary that
    #   `sort -m -n s1 s2` == `cat n1 n2 | sort -n` and `sort -m -u p1 p2` == `sort -u whole`.
    #   Without -s/-u, sort's last-resort byte comparison makes the output a function of the multiset of
    #   lines only, so CC and RR both work and the merge is commutative.
    # -s, -u: sort disables the last-resort comparison (-u implies -s), so lines with equal keys keep their
    #   input order; only CC preserves that order, and the merge must take parts in order (not commutative).
    # -c, -C, --check: no sorting is done, output is a diagnostic + exit status; not parallelized.
    # -m: the inputs are already sorted and are merged; the merge itself is not split.
    # -R, --sort=random: each part would be shuffled independently; the merge is not a shuffle of the whole.
    # --debug: writes annotation lines to stdout; the merge would not reproduce them.
    # -o: each mapper would write to the same FILE; not parallelized (the seq mapper reuses the invocation).
    # -z: NUL-terminated records; PaSh's splitters work on newline-delimited lines.
    # --files0-from: there is no streaming input operand to split.
    # the ordering options (-b -d -f -g -i -M -h -n -r -V --sort -k -t) are forwarded to the merge;
    # resource options (-S -T --parallel --batch-size --compress-program --random-source) are harmless.

    non_parallelizable = ["-c", "-C", "--check", "-m", "--merge", "-R", "--random-sort", "--debug",
                          "-o", "--output", "-z", "--zero-terminated", "--files0-from", "--help", "--version"]
    # options whose spelling and argument must be forwarded to the merge so it compares like the mappers
    ordering_options = ["-b", "--ignore-leading-blanks", "-d", "--dictionary-order", "-f", "--ignore-case",
                        "-g", "--general-numeric-sort", "-i", "--ignore-nonprinting", "-M", "--month-sort",
                        "-h", "--human-numeric-sort", "-n", "--numeric-sort", "-r", "--reverse",
                        "-V", "--version-sort", "--sort", "-k", "--key", "-t", "--field-separator",
                        "-s", "--stable", "-u", "--unique"]

    def generate_info(self) -> None:
        if self.does_flag_option_list_contain_at_least_one_of(self.non_parallelizable):
            return
        if self.sorts_randomly():
            return
        aggregator_spec = make_aggregator_spec_custom_2_ary_from_string_representation(
            cmd_inv_as_str=self.merge_command_as_string(), is_implemented=True)
        parallelizer_cc = make_parallelizer_consec_chunks(aggregator_spec=aggregator_spec)
        self.append_to_parallelizer_list(parallelizer_cc)
        if not self.does_flag_option_list_contain_at_least_one_of(["-s", "--stable", "-u", "--unique"]):
            # order of equal lines is fully determined, so dealing lines out round-robin is fine too
            parallelizer_rr = make_parallelizer_round_robin(aggregator_spec=aggregator_spec)
            self.append_to_parallelizer_list(parallelizer_rr)
            self.set_commutative()

    def sorts_randomly(self) -> bool:
        for flag_option in self.get_flag_option_list_filtered_with(["--sort"]):
            if str(self._arg_of(flag_option)) == "random":
                return True
        return False

    def merge_command_as_string(self) -> str:
        # `sort -m` followed by the ordering options of the invocation, with their arguments
        words = ["sort", "-m"]
        for flag_option in self.get_flag_option_list_filtered_with(self.ordering_options):
            words.append(self._name_of(flag_option))
            arg = self._arg_of(flag_option)
            if arg is not None:
                words.append(str(arg))
        return " ".join(words)

    @staticmethod
    def _name_of(flag_option) -> str:
        if hasattr(flag_option, "get_name"):
            return str(flag_option.get_name())
        return str(getattr(flag_option, "name", flag_option))

    @staticmethod
    def _arg_of(flag_option):
        if hasattr(flag_option, "get_arg"):
            return flag_option.get_arg()
        return getattr(flag_option, "option_arg", None)
