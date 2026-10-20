from pash_annotations.annotation_generation.annotation_generators.ParallelizabilityInfoGenerator_Interface import ParallelizabilityInfoGeneratorInterface


class ParallelizabilityInfoGeneratorConvert(ParallelizabilityInfoGeneratorInterface):

    # ImageMagick 6 `convert` reads whole image files (not line- or chunk-oriented data),
    # applies the operators in command-line order to the whole image sequence, and writes
    # whole image files.  Standard input, when used, is a single complete image blob that
    # must be read in full before anything can be decoded, and the output is a binary
    # image container that cannot be produced by concatenating partial results.
    # Neither consecutive chunks nor round-robin splitting of the input stream is therefore
    # meaningful, and a per-input-file split would change the result of the many
    # sequence operators (-append, -flatten, -composite, -delete, ...).
    #
    # Hence no parallelizer is offered: the invocation is treated as not parallelisable.

    def generate_info(self) -> None:
        pass
