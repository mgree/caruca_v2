from pash_annotations.annotation_generation.annotation_generators.ParallelizabilityInfoGenerator_Interface import ParallelizabilityInfoGeneratorInterface


class ParallelizabilityInfoGeneratorRm(ParallelizabilityInfoGeneratorInterface):

    # rm has no input stream to split: its operands are paths that are
    # removed, and it produces no data on stdout (only -v messages).
    # There is therefore nothing to parallelize; no parallelizer is appended,
    # which PaSh treats as "not parallelizable".

    def generate_info(self) -> None:
        pass
