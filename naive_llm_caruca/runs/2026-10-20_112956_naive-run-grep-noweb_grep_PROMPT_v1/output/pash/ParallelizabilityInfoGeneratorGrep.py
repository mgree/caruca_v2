from pash_annotations.annotation_generation.annotation_generators.ParallelizabilityInfoGenerator_Interface import ParallelizabilityInfoGeneratorInterface
from pash_annotations.annotation_generation.datatypes.parallelizability.Parallelizer import \
    AdditionalInfoSplitterToMapper, make_parallelizer_round_robin, make_parallelizer_consec_chunks
from pash_annotations.annotation_generation.datatypes.parallelizability.MapperSpec import make_mapper_spec_custom
from pash_annotations.annotation_generation.datatypes.parallelizability.AggregatorSpec import \
    make_aggregator_spec_custom_2_ary_from_string_representation


class ParallelizabilityInfoGeneratorGrep(ParallelizabilityInfoGeneratorInterface):

    # GNU grep 3.11 processes its input line by line, so its work can be split into
    # consecutive chunks or round-robin over lines and the outputs concatenated, except:
    #
    #   * -q/--quiet/--silent: grep stops reading at the first match and produces no
    #     output; only the exit status matters.  Not parallelised.
    #   * -m/--max-count NUM: stops after NUM selected lines over the whole input;
    #     a per-chunk limit would select too many lines.  Not parallelised.
    #   * -A/-B/-C/--after-context/--before-context/--context (and the -NUM form, which
    #     PaSh's parser cannot recognise): context lines cross chunk boundaries and group
    #     separators depend on adjacency.  Not parallelised.
    #   * -z/--null-data: records are terminated by NUL, not newline, so a line-based
    #     splitter would cut records apart.  Not parallelised.
    #   * -l/--files-with-matches: the output is the file name if any chunk matched;
    #     -L/--files-without-match: the file name only if no chunk matched.
    #     -l and -L override -c, which overrides -n and -b.
    #   * -c/--count: the per-chunk counts have to be added up.
    #   * -n/--line-number and -b/--byte-offset: each mapper must add the number of
    #     lines / bytes that precede its chunk; the -n prefix precedes the -b prefix.
    #     (-o -b prints the offset of each match and needs the same byte-offset shift.)
    #   * --help and -V/--version are assumed not to occur.
    #
    # Splitting over individual files (indiv_files) is deliberately not offered: with two
    # or more FILE operands grep prefixes each output line with the file name, and
    # -l/-L/-c print one line per file, so running one grep per file changes the output.
    # The custom mappers and aggregators are PLACEHOLDERs that PaSh does not provide yet;
    # invocations that need them are therefore currently not parallelised.

    def generate_info(self) -> None:
        if self.does_flag_option_list_contain_at_least_one_of(
                ["-q", "--quiet", "--silent",
                 "-m", "--max-count",
                 "-A", "--after-context", "-B", "--before-context", "-C", "--context",
                 "-z", "--null-data",
                 "--help", "-V", "--version"]):
            return

        mapper_spec = None
        aggregator_spec = None
        add_info_from_splitter = None

        if self.does_flag_option_list_contain_at_least_one_of(["-l", "--files-with-matches"]):
            # output is either empty or the (same) file name: keep it if any part printed it
            aggregator_spec = make_aggregator_spec_custom_2_ary_from_string_representation(
                cmd_inv_as_str='PLACEHOLDER:merge_keeping_longer_output', is_implemented=False)
            self.set_commutative()
        elif self.does_flag_option_list_contain_at_least_one_of(["-L", "--files-without-match"]):
            # file name is printed only if no part had a match, i.e. if every part printed it
            aggregator_spec = make_aggregator_spec_custom_2_ary_from_string_representation(
                cmd_inv_as_str='PLACEHOLDER:merge_keeping_output_if_all_nonempty', is_implemented=False)
            self.set_commutative()
        elif self.does_flag_option_list_contain_at_least_one_of(["-c", "--count"]):
            # cat part1 part2 | paste -s -d + - | bc
            aggregator_spec = make_aggregator_spec_custom_2_ary_from_string_representation(
                cmd_inv_as_str='PLACEHOLDER:sum_indiv_results_up', is_implemented=False)
            self.set_commutative()
        elif self.does_flag_option_list_contain_at_least_one_of(["-n", "--line-number"]) and \
                self.does_flag_option_list_contain_at_least_one_of(["-b", "--byte-offset"]):
            mapper_spec = make_mapper_spec_custom('PLACEHOLDER:grep_add_line_number_and_byte_offset',
                                                  is_implemented=False)
            add_info_from_splitter = AdditionalInfoSplitterToMapper.LINE_NUM_AND_BYTE_OFFSET
        elif self.does_flag_option_list_contain_at_least_one_of(["-n", "--line-number"]):
            mapper_spec = make_mapper_spec_custom('PLACEHOLDER:grep_add_line_number_offset',
                                                  is_implemented=False)
            add_info_from_splitter = AdditionalInfoSplitterToMapper.LINE_NUM_OFFSET
        elif self.does_flag_option_list_contain_at_least_one_of(["-b", "--byte-offset"]):
            mapper_spec = make_mapper_spec_custom('PLACEHOLDER:grep_add_byte_offset',
                                                  is_implemented=False)
            add_info_from_splitter = AdditionalInfoSplitterToMapper.BYTE_OFFSET
        # otherwise: plain sequential mapper and concatenation

        # mapper_spec None -> seq, aggregator_spec None -> conc.
        # Skip parallelizers whose custom parts PaSh does not implement yet.
        if (mapper_spec is None or mapper_spec.is_implemented) and \
                (aggregator_spec is None or aggregator_spec.is_implemented):
            self.append_to_parallelizer_list(make_parallelizer_consec_chunks(
                mapper_spec=mapper_spec, aggregator_spec=aggregator_spec,
                info_splitter_mapper=add_info_from_splitter))
            self.append_to_parallelizer_list(make_parallelizer_round_robin(
                mapper_spec=mapper_spec, aggregator_spec=aggregator_spec,
                info_splitter_mapper=add_info_from_splitter))
