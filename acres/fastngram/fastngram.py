"""
A faster version of n-gram matching that uses dictionaries for speed-up.
"""

import logging
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
        # TODO Refactor as Dict[Tuple[str, str], Dict[int, Set[str]]], with int = freq
        self.map = {}  # type: Dict[Tuple[str, str], Set[str]]

    def add_context(self, center: str, left_context: str, right_context: str) -> None:
        """
        Add a center n-gram with a context.

        :param center:
        :param left_context:
        :param right_context:
        :return:
        """
        context = (left_context, right_context)
        self.map.setdefault(context, set())
        self.map[context].add(center)

    def centers(self, left_context: str, right_context: str) -> Set[str]:
        """
        Find center n-grams that happen on a given context.

        :param left_context:
        :param right_context:
        :return:
        """
        context = (left_context, right_context)
        if context not in self.map:
            return set()
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
    previous_ngrams = set()

    rank = 0
    for size in range(7, 0, -2):
        if size not in model:
            continue

        left = text.context_ngram(left_context, int(size / 2), True)
        right = text.context_ngram(right_context, int(size / 2), False)

        count_map = model[size]
        for freq, context_map in count_map.items():
            if freq < min_freq:
                break
            center_ngrams = context_map.centers(left, right)
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


def optimizer(ngrams: Dict[str, int]) -> 'Dict[int, OrderedDict[int, ContextMap]]':
    """
    Create a search-optimized represenation of an ngram-list.

    @todo Support assymetric n-grams.
    @todo Support training contexts from the acronym.

    :param ngrams:
    :return:
    """
    logger.info("Creating model for fastngram...")

    model = {}  # type: Dict[int, OrderedDict[int, ContextMap]]

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
            # TODO preserve list and intern strings
            center = " ".join(tokens[i:j])
            size = 1 + 2 * i  # n-gram size
            _update_model(model, size, freq, center, left, right)

    logger.info("Fastngram model created.")
    return model


def _update_model(model, size, freq, center, left_context, right_context):
    """
    Update the model with the given ngram.

    :param model:
    :param size:
    :param freq:
    :param center:
    :param left_context:
    :param right_context:
    :return:
    """
    # Initialize context map if needed
    if size in model and freq in model[size]:
        context = model[size][freq]
    else:
        context = ContextMap()

    # TODO Remove size dict, which is redundant with the context length.

    context.add_context(center, left_context, right_context)
    model.setdefault(size, OrderedDict())  # initialize dictionary count -> ContextMap if needed
    model[size][freq] = context
