"""Trainer for word2vec embeddings

@author Michel Oleynik
@thanks Johannes Hellrich (https://github.com/JULIELab/hellrich_dh2016)
"""

import logging
import os.path
from logging.config import fileConfig

logging.config.fileConfig("logging.ini")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# MUST be after logging definition, so that it works properly
from gensim.models import Word2Vec
from acres import resource_factory


class FilteredNGramStat(object):
    """Filtered NGramStat generator

    This generator generates ngrams of a given size out of a ngramstat.txt file, while respecting
    each ngram frequency.

    @todo ngramstat itself should be a generator
    """
    NGRAMSTAT = resource_factory.get_ngramstat()
    NGRAM_SEPARATOR = "\t"
    TOKEN_SEPARATOR = " "
    PRINT_INTERVAL = 1000000

    def __init__(self, ngram_size):
        """

        :param ngram_size: The exact size of ngrams to be considered.
        """
        self.ngram_size = ngram_size

    def __iter__(self):
        logger.debug("Iterating...")
        for identifier, freq_ngram in self.NGRAMSTAT.items():
            freq, ngram = freq_ngram.split("\t")
            tokens = ngram.split(self.TOKEN_SEPARATOR)

            # Only consider ngrams of a given size
            if len(tokens) == self.ngram_size:
                logger.debug("%s: %s -> %s", identifier, freq,
                             ngram) if identifier % self.PRINT_INTERVAL == 0 else 0
                # Repeat ngram freq times
                for i in range(int(freq)):
                    yield tokens


def get_nn_model(ngram_size=6, min_count=1, net_size=100, alpha=0.025, sg=1, hs=0, negative=5):
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
    MODEL_PATH = "models/nn/{}-{}-{}-{}-{}-{}-{}.model".format(ngram_size, min_count, net_size,
                                                               alpha, sg, hs, negative)

    if not os.path.isfile(MODEL_PATH):
        logger.info("Training the model...")

        sentences = FilteredNGramStat(ngram_size)

        model = Word2Vec(sentences, size=net_size, alpha=alpha, window=ngram_size - 1,
                         min_count=min_count,
                         workers=4, sg=sg, hs=hs, negative=negative)

        # Hellrich
        # model = gensim.models.Word2Vec(size=200, window=4, min_count=5, workers=8, alpha=0.01, sg=1, hs=0, negative=5, sample=1e-3)

        model.save(MODEL_PATH)

    return Word2Vec.load(MODEL_PATH)


if __name__ == "__main__":
    model = get_nn_model(min_count=5)
    model.most_similar(positive="CMP")  # [('Kardiomyopathie', 0.772693395614624), ...]
