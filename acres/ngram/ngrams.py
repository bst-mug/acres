"""
Module to handle n-gram lists.
"""
import logging
from typing import Generator, List, Iterator

from acres.preprocess import resource_factory
from acres.util import acronym

logger = logging.getLogger(__name__)


class FilteredNGramStat:
    """Filtered NGramStat generator

    This generator generates ngrams of a given size out of a ngramstat.txt file, while respecting
    each ngram frequency.

    @todo ngramstat itself should be a generator
    """
    NGRAM_SEPARATOR = "\t"
    TOKEN_SEPARATOR = " "
    PRINT_INTERVAL = 1000000

    def __init__(self, ngram_size: int) -> None:
        """

        :param ngram_size: The exact size of ngrams to be considered.
        """
        self.ngram_size = ngram_size
        self.ngramstat = resource_factory.get_ngramstat()

    def __iter__(self) -> Generator[List[str], None, None]:
        logger.debug("Iterating...")

        for identifier, freq_ngram in self.ngramstat.items():
            (freq, ngram) = freq_ngram
            tokens = ngram.split(self.TOKEN_SEPARATOR)
            length_tokens = len(tokens)

            # Only consider ngrams of a given size, so that we work with a non-overlapping list
            # If window > len(tokens), word2vec still works
            if length_tokens == self.ngram_size:
                if identifier % self.PRINT_INTERVAL == 0:
                    logger.debug("%s: %s -> %s", identifier, freq, ngram)

                # Repeat ngram freq times
                for _ in range(int(freq)):
                    yield tokens


def filter_acronym_contexts(ngrams: Iterator[List[str]]) -> 'Iterator[acronym.Acronym]':
    """
    Filter an iterable of tokens by the ones containing an acronym in the middle and convert them \
    to Acronym tuples.

    :param ngrams:
    :return:
    """
    for tokens in ngrams:
        ngram_size = len(tokens)
        middle = int(len(tokens) / 2)
        if acronym.is_acronym(tokens[middle]):
            yield acronym.Acronym(acronym=tokens[middle],
                                  left_context=' '.join(tokens[0:middle]),
                                  right_context=' '.join(tokens[middle + 1:ngram_size]))
