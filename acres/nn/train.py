"""Trainer for word2vec embeddings

@author Michel Oleynik
@thanks Johannes Hellrich (https://github.com/JULIELab/hellrich_dh2016)
"""

import logging
from typing import List, Generator

from gensim.models import Word2Vec, Phrases
from gensim.models.phrases import Phraser

from acres.preprocess import resource_factory
from acres.nn import base

logger = logging.getLogger(__name__)


class FilteredNGramStat(object):
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

        largest_reduction = 0

        for identifier, freq_ngram in self.ngramstat.items():
            (freq, ngram) = freq_ngram
            tokens = ngram.split(self.TOKEN_SEPARATOR)
            length_tokens = len(tokens)

            # Only consider ngrams of a given size, so that we work with a non-overlapping list
            if length_tokens == self.ngram_size:
                if identifier % self.PRINT_INTERVAL == 0:
                    logger.debug("%s: %s -> %s", identifier, freq, ngram)

                cleaned_tokens = base.preprocess(tokens)

                # If window > len(cleaned_tokens), word2vec still works
                length_difference = length_tokens - len(cleaned_tokens)
                if length_difference > 0 and length_difference > largest_reduction:
                    largest_reduction = length_difference
                    logger.debug("New largest reduction is %d (from %d to %d) on ngram '%s'",
                                 largest_reduction, length_tokens, len(cleaned_tokens), ngram)

                # Repeat ngram freq times
                for _ in range(int(freq)):
                    yield cleaned_tokens


def train(ngram_size: int = 6, min_count: int = 1, net_size: int = 100, alpha: float = 0.025,
          sg: int = 1, hs: int = 0, negative: int = 5) -> Word2Vec:
    """
    Lazy load a word2vec model.

    :param ngram_size:
    :param min_count:
    :param net_size:
    :param alpha:
    :param sg:
    :param hs:
    :param negative:
    :return:
    """
    sentences = FilteredNGramStat(ngram_size)

    # Find common bigram collocations.
    # Trigrams led to a 2% drop in F1 caused by a 2% drop in recall (though precision increased 2%).
    # TODO debug why "Rechter_Ventrikel" is not generated
    phrases = Phrases(sentences)
    bigram_transformer = Phraser(phrases)
    collocations = bigram_transformer[sentences]

    return Word2Vec(collocations, size=net_size, alpha=alpha, window=ngram_size - 1,
                    min_count=min_count, workers=4, sg=sg, hs=hs, negative=negative)

    # Hellrich
    # model = gensim.models.Word2Vec(size=200, window=4, min_count=5, workers=8, alpha=0.01,
    # sg=1, hs=0, negative=5, sample=1e-3)


if __name__ == "__main__":
    MODEL = train(min_count=5)
