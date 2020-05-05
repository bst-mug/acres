"""
A faster version of n-gram matching that uses dictionaries for speed-up.
"""

import logging
import sys
from collections import OrderedDict
from typing import Dict, Set, Tuple, Iterator, List, Union

import acres.util.acronym
from acres.model import topic_list
from acres.preprocess import resource_factory
from acres.util import functions
from acres.util.functions import import_conf

logger = logging.getLogger(__name__)

# Maximum difference in size between left and right context.
MAX_DIFF = 1

PARTITIONS = int(import_conf("FastNgramPartitions"))


class ContextMap:
    """
    A map of contexts to center words.
    """

    def __init__(self) -> None:
        self.map = {}  # type: Dict[Tuple[str, str], OrderedDict[int, Set[str]]]

    def add(self, center: str, left_context: str, right_context: str, freq: int) -> None:
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


class CenterMap:
    """
    A map of center words to contexts.
    """

    def __init__(self) -> None:
        self.map = {}  # type: Dict[str, OrderedDict[int, Set[Tuple[str, str]]]]

    def add(self, center: str, left_context: str, right_context: str, freq: int) -> None:
        """
        Add a center n-gram with a context.

        :param center:
        :param left_context:
        :param right_context:
        :param freq:
        :return:
        """
        context = (left_context, right_context)
        self.map.setdefault(center, OrderedDict())
        self.map[center].setdefault(freq, set())
        self.map[center][freq].add(context)

    def contexts(self, center: str) -> 'OrderedDict[int, Set[Tuple[str, str]]]':
        """
        Find contexts for a given center word.

        :param center:
        :return:
        """
        if center not in self.map:
            return OrderedDict()
        return self.map[center]


def baseline(acronym: str, left_context: str = "", right_context: str = "") -> Iterator[str]:
    """
    A baseline method that expands only with unigrams.

    :param acronym:
    :param left_context:
    :param right_context:
    :return:
    """
    return fastngram(acronym, "", "")


def fastngram(acronym: str, left_context: str = "", right_context: str = "",
              min_freq: int = 2, max_rank: int = 100000) -> Iterator[str]:
    """
    Find an unlimited set of expansion candidates for an acronym given its left and right context. \
    Note that no filtering is done here, except from the acronym initial partioning.

    :param acronym:
    :param left_context:
    :param right_context:
    :param min_freq:
    :param max_rank:
    :return:
    """
    contextualized_acronym = acres.util.acronym.Acronym(acronym=acronym, left_context=left_context,
                                                        right_context=right_context)
    contexts = _generate_acronym_contexts(contextualized_acronym)

    for ngram in _center_provider(contexts, min_freq, max_rank):
        yield ngram


def fasttype(acronym: str, left_context: str = "", right_context: str = "",
             min_freq: int = 2, max_rank: int = 100000) -> Iterator[str]:
    """
    Find an unlimited set of expansion candidates given the training contexts of the acronym. \
    Note that no filtering is done here, except from the acronym initial partioning.

    :param acronym:
    :param left_context: Not used.
    :param right_context: Not used.
    :param min_freq:
    :param max_rank:
    :return:
    """
    contexts = _find_contexts(acronym, min_freq)

    for ngram in _center_provider(contexts, min_freq, max_rank):
        yield ngram


def _find_contexts(acronym: str, min_freq: int) -> 'List[topic_list.Acronym]':
    """
    Find contexts in the training data where this acronym appears.

    :param acronym:
    :param min_freq:
    :return:
    """
    model = resource_factory.get_center_map(functions.partition(acronym, PARTITIONS))

    all_contexts = []  # type: List[topic_list.Acronym]
    for out_freq, contexts in model.contexts(acronym).items():
        for left, right in contexts:
            # Do not allow empty contexts.
            if left == '' and right == '':
                continue
            if out_freq < min_freq:
                break
            contextualized_acronym = acres.util.acronym.Acronym(acronym=acronym, left_context=left,
                                                                right_context=right)
            all_contexts.append(contextualized_acronym)

    return all_contexts


def _center_provider(contexts: 'List[topic_list.Acronym]', min_freq: int,
                     max_rank: int) -> Iterator[str]:
    """
    Provide unlimited center words for a given list of contexts.

    :param contexts:
    :param min_freq:
    :param max_rank:
    :return:
    """
    # Save previous expansions to avoid the same n-gram to be retrieve from different contexts.
    previous_ngrams = set()  # type: Set[str]

    rank = 0
    for contextualized_acronym in contexts:
        partition = functions.partition(contextualized_acronym.acronym, PARTITIONS)
        model = resource_factory.get_context_map(partition)

        left = contextualized_acronym.left_context
        right = contextualized_acronym.right_context
        count_map = model.centers(left, right)
        for freq, center_ngrams in count_map.items():
            if freq < min_freq:
                break
            for ngram in center_ngrams:
                if rank > max_rank:
                    return ""
                if ngram not in previous_ngrams:
                    previous_ngrams.add(ngram)
                    rank += 1
                    yield ngram


def create_map(ngrams: Dict[str, int], model: Union[ContextMap, CenterMap],
               partition: int = 0) -> Union[ContextMap, CenterMap]:
    """
    Create a search-optimized represenation of an ngram-list.

    :param ngrams:
    :param model:
    :param partition:
    :return:
    """
    logger.info("Creating model for fastngram with partition = %d...", partition)

    # Ensure ngrams are ordered by decreasing frequency.
    sorted_ngrams = sorted(ngrams.items(), key=lambda x: x[1], reverse=True)

    for ngram, freq in sorted_ngrams:
        for context in _generate_ngram_contexts(ngram):
            if functions.partition(context.acronym, PARTITIONS) == partition:
                model.add(context.acronym, context.left_context, context.right_context, freq)

    logger.info("Fastngram model created.")
    return model


def _generate_ngram_contexts(ngram: str) -> 'List[topic_list.Acronym]':
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
            contexts.append(acres.util.acronym.Acronym(acronym=center, left_context=left,
                                                       right_context=right))
    return contexts


def _generate_acronym_contexts(contextualized_acronym: 'topic_list.Acronym') -> 'List[topic_list.Acronym]':
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

    contexts = []  # type: List[topic_list.Acronym]
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
            contexts.append(acres.util.acronym.Acronym(acronym=contextualized_acronym.acronym,
                                                       left_context=left_context,
                                                       right_context=right_context))
    return contexts
