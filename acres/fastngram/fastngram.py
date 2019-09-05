"""
A faster version of n-gram matching that uses dictionaries for speed-up.
"""

import logging
import sys
from collections import OrderedDict
from typing import Dict, Set, Tuple, Iterator

from acres.preprocess import resource_factory
from acres.util import text

logger = logging.getLogger(__name__)


class ContextMap:
    """
    A map of contexts to center words.
    """

    def __init__(self) -> None:
        self.map = {}  # type: Dict[Tuple[str, str], OrderedDict[int, Set[str]]]

    def add_context(self, center: str, left_context: str, right_context: str, freq: int) -> None:
        """
        Add a center n-gram with a context.

        :param center:
        :param left_context:
        :param right_context:
        :param freq:
        :return:
        """
        context = (sys.intern(left_context), sys.intern(right_context))
        self.map.setdefault(context, OrderedDict())
        self.map[context].setdefault(freq, set())
        self.map[context][freq].add(sys.intern(center))

    def centers(self, left_context: str, right_context: str) -> 'OrderedDict[int, Set[str]]':
        """
        Find center n-grams that happen on a given context.

        :param left_context:
        :param right_context:
        :return:
        """
        context = (left_context, right_context)
        if context not in self.map:
            return OrderedDict()
        return self.map[context]


def expandn(acronym: str, left_context: str = "", right_context: str = "",
            min_freq: int = 2, max_rank: int = 100000) -> Iterator[str]:
    """
    Find an unlimited set of expansion candidates for an acronym given its left and right context. \
    Note that no filtering is done here.

    :param acronym: Not used.
    :param left_context:
    :param right_context:
    :param min_freq:
    :param max_rank:
    :return:
    """
    model = resource_factory.get_fastngram()

    # Save previous expansions to avoid the same n-gram to be retrieve from different contexts.
    previous_ngrams = set()  # type: Set[str]

    # Largest given context.
    context_size = max(len(left_context.split()), len(right_context.split()))

    rank = 0
    for size in range(context_size, -1, -1):
        left = text.context_ngram(left_context, size, True)
        right = text.context_ngram(right_context, size, False)

        count_map = model.centers(left, right)
        for freq, center_ngrams in count_map.items():
            if freq < min_freq:
                break
            for ngram in center_ngrams:
                if rank > max_rank:
                    logger.debug("Exausthed generator for %s", acronym)
                    return ""
                if ngram not in previous_ngrams:
                    previous_ngrams.add(ngram)
                    rank += 1
                    yield ngram


def baseline(acronym: str, left_context: str = "", right_context: str = "") -> Iterator[str]:
    """
    A baseline method that expands only with unigrams.

    :param acronym:
    :param left_context:
    :param right_context:
    :return:
    """
    return expandn(acronym, "", "")


def optimizer(ngrams: Dict[str, int]) -> ContextMap:
    """
    Create a search-optimized represenation of an ngram-list.

    @todo Support assymetric n-grams.
    @todo Support training contexts from the acronym.

    :param ngrams:
    :return:
    """
    logger.info("Creating model for fastngram...")

    model = ContextMap()

    # Ensure ngrams are ordered by decreasing frequency.
    sorted_ngrams = sorted(ngrams.items(), key=lambda x: x[1], reverse=True)

    for ngram, freq in sorted_ngrams:
        tokens = ngram.split(" ")
        ngram_size = len(tokens)

        # Add n-grams with a decreasing central n-gram and increasing lateral context.
        for i in range(ngram_size):
            j = ngram_size - i
            # Walk only until half.
            if i >= j:
                break
            left = " ".join(tokens[0:i])
            right = " ".join(tokens[j:ngram_size])
            center = " ".join(tokens[i:j])
            model.add_context(center, left, right, freq)

    logger.info("Fastngram model created.")
    return model
