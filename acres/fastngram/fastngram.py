"""
A faster version of n-gram matching that uses dictionaries for speed-up.
"""

import logging
import sys
from collections import OrderedDict
from typing import Dict, Set, Tuple, Iterator, List

from acres.model.topic_list import Acronym
from acres.preprocess import resource_factory

logger = logging.getLogger(__name__)

# Maximum difference in size between left and right context.
MAX_DIFF = 1


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
        context = (left_context, right_context)
        self.map.setdefault(context, OrderedDict())
        self.map[context].setdefault(freq, set())
        self.map[context][freq].add(center)

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
    model = resource_factory.get_context_map()

    # Save previous expansions to avoid the same n-gram to be retrieve from different contexts.
    previous_ngrams = set()  # type: Set[str]

    acronym = Acronym(acronym=acronym, left_context=left_context, right_context=right_context)

    rank = 0
    for contextualized_acronym in _generate_acronym_contexts(acronym):
        left = contextualized_acronym.left_context
        right = contextualized_acronym.right_context
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


def create_context_map(ngrams: Dict[str, int]) -> ContextMap:
    """
    Create a search-optimized represenation of an ngram-list.

    @todo Support training contexts from the acronym.

    :param ngrams:
    :return:
    """
    logger.info("Creating model for fastngram...")

    model = ContextMap()

    # Ensure ngrams are ordered by decreasing frequency.
    sorted_ngrams = sorted(ngrams.items(), key=lambda x: x[1], reverse=True)

    for ngram, freq in sorted_ngrams:
        for context in _generate_ngram_contexts(ngram):
            model.add_context(context.acronym, context.left_context, context.right_context, freq)

    logger.info("Fastngram model created.")
    return model


def _generate_ngram_contexts(ngram: str) -> List[Acronym]:
    """
    Generate a list of contextualized n-grams with a decreasing central n-gram and increasing \
    lateral context.

    :param ngram:
    :return: 
    """
    tokens = ngram.split(" ")
    ngram_size = len(tokens)

    contexts = []
    # Walk only until half and `max_diff` more.
    for i in range(0, int((ngram_size + 1 + MAX_DIFF) / 2)):
        # Allow up to `max_diff` difference in size.
        for j in range(ngram_size - i + MAX_DIFF, ngram_size - i - MAX_DIFF - 1, -1):
            # Do not allow empty acronym.
            if i >= j:
                break
            # Do not walk past the n-gram.
            if j > ngram_size:
                continue
            left = sys.intern(" ".join(tokens[0:i]))
            right = sys.intern(" ".join(tokens[j:ngram_size]))
            center = sys.intern(" ".join(tokens[i:j]))
            contexts.append(Acronym(acronym=center, left_context=left, right_context=right))
    return contexts


def _generate_acronym_contexts(contextualized_acronym: Acronym) -> List[Acronym]:
    """
    Generate a list of contextualized acronyms with decreasing lateral context.

    Right context is deemed more important than left context, e.g. EF 00%, HF 000/min,
    so we generate first longer right n-grams, e.g. (left_bigram, right_trigram).

    @todo default parameter min_length = 0, so that we avoid empty contexts if we want.

    :param contextualized_acronym:
    :return:
    """
    left = contextualized_acronym.left_context.split()
    right = contextualized_acronym.right_context.split()
    left_length = len(left)
    right_length = len(right)

    # We allow up to MAX_DIFF difference in context size iff the right context is larger than left.
    max_length = min(left_length, right_length)
    if right_length > left_length:
        max_length += min(MAX_DIFF, right_length - left_length)

    contexts = []
    for j in range(max_length, -1, -1):
        # Left size > right size
        if j > right_length:
            continue
        for i in range(left_length - j - MAX_DIFF, left_length - j + MAX_DIFF + 1):
            # Prevents double empty context on last iteration
            if i > left_length:
                break
            # Left size < right size
            if i < 0:
                continue
            left_context = " ".join(left[i:left_length])
            right_context = " ".join(right[0:j])
            contexts.append(Acronym(acronym=contextualized_acronym.acronym,
                                    left_context=left_context, right_context=right_context))
    return contexts
