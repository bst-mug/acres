"""Trainer for word2vec embeddings

@author Michel Oleynik
@thanks Johannes Hellrich (https://github.com/JULIELab/hellrich_dh2016)
"""

import logging
import os.path
import re
from logging.config import fileConfig
from typing import List

logging.config.fileConfig("logging.ini")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# MUST be after logging definition, so that it works properly
from gensim.models import Word2Vec, Phrases
from acres.preprocess import resource_factory


class FilteredNGramStat(object):
    """Filtered NGramStat generator

    This generator generates ngrams of a given size out of a ngramstat.txt file, while respecting
    each ngram frequency.

    @todo ngramstat itself should be a generator
    """
    NGRAM_SEPARATOR = "\t"
    TOKEN_SEPARATOR = " "
    PRINT_INTERVAL = 1000000

    def __init__(self, ngram_size):
        """

        :param ngram_size: The exact size of ngrams to be considered.
        """
        self.ngram_size = ngram_size
        self.NGRAMSTAT = resource_factory.get_ngramstat()

    def __iter__(self):
        logger.debug("Iterating...")

        largest_reduction = 0

        for identifier, freq_ngram in self.NGRAMSTAT.items():
            (freq, ngram) = freq_ngram
            tokens = ngram.split(self.TOKEN_SEPARATOR)
            length_tokens = len(tokens)

            # Only consider ngrams of a given size
            if length_tokens == self.ngram_size:
                logger.debug("%s: %s -> %s", identifier, freq,
                             ngram) if identifier % self.PRINT_INTERVAL == 0 else 0

                #cleaned_tokens = tokens
                cleaned_tokens = preprocess(tokens)

                # FIXME drop empty ngrams...
                # FIXME what happens with word2vec if window > len(cleaned_tokens)?
                # Should we force a smaller window size guaranteed to always fit?
                length_difference = length_tokens - len(cleaned_tokens)
                if (length_difference > 0 and length_difference > largest_reduction):
                    largest_reduction = length_difference
                    logger.debug("New largest reduction is %d (from %d to %d) on ngram '%s'",
                                 largest_reduction, length_tokens, len(cleaned_tokens), ngram)

                # Repeat ngram freq times
                for i in range(int(freq)):
                    yield cleaned_tokens


def preprocess(tokens: List[str]) -> List[str]:
    """
    Pre-process a given list of tokens by removing special characters.

    :param tokens:
    :return:
    """
    ret = []

    regex_disallowed = re.compile("[^a-zA-ZÐ]")

    for token in tokens:
        # TODO normalize case if not acronym?
        # TODO normalize german characters
        # TODO fix ¶ cleaning bug
        cleaned_token = regex_disallowed.sub("", token)
        if len(cleaned_token) > 0:
            ret.append(cleaned_token)

    return ret


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

        # Find common bigram collocations
        bigram_transformer = Phrases(sentences)
        collocations = bigram_transformer[sentences]

        model = Word2Vec(collocations, size=net_size, alpha=alpha, window=ngram_size - 1,
                         min_count=min_count,
                         workers=4, sg=sg, hs=hs, negative=negative)

        # Hellrich
        # model = gensim.models.Word2Vec(size=200, window=4, min_count=5, workers=8, alpha=0.01,
        # sg=1, hs=0, negative=5, sample=1e-3)

        model.save(MODEL_PATH)

    return Word2Vec.load(MODEL_PATH)


if __name__ == "__main__":
    model = get_nn_model(min_count=5)
    model.most_similar(positive="CMP")  # [('Kardiomyopathie', 0.772693395614624), ...]
