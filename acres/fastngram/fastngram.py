"""
A faster version of n-gram matching that uses dictionaries for speed-up.
"""

from collections import OrderedDict
from typing import List, Dict, Set, Tuple, Iterator

from acres.preprocess import resource_factory


class ContextMap:
    """
    A map of contexts to center words.
    """

    def __init__(self) -> None:
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


def expandn(acronym: str, left_context: str = "", right_context: str = "") -> Iterator[str]:
    """
    Find an unlimited set of expansion candidates for an acronym given its left and right context. \
    Note that no filtering is done here.

    :param acronym: Not used.
    :param left_context:
    :param right_context:
    :return:
    """
    model = resource_factory.get_fastngram()

    # TODO support for n-grams (n > 1). May need an OrderedDict.
    count_map = model[1]
    for freq, context_map in count_map.items():
        # TODO require a min_freq?
        center_ngrams = context_map.centers(left_context, right_context)
        for ngram in center_ngrams:
            yield ngram


def expand(acronym: str, left_context: str = "", right_context: str = "") -> List[str]:
    """
    Find a limited set of expansion candidates for an acronym given its left and right context.

    :param acronym:
    :param left_context:
    :param right_context:
    :return:
    """
    # Limit expansions while we don't use generators downstream
    # TODO 1k may not be enough if we're not doing ANY filtering here (e.g. initial).
    # https://github.com/bst-mug/acres/issues/28
    limit = 1000
    i = 0
    ret = []  # type: List[str]
    for ngram in expandn(acronym, left_context, right_context):
        ret.append(ngram)
        i += 1
        if i > limit:
            break
    return ret


def optimizer(ngrams: Dict[str, int]) -> 'Dict[int, OrderedDict[int, ContextMap]]':
    """
    Create a search-optimized represenation of an ngram-list.

    :param ngrams:
    :return:
    """
    model = {}  # type: Dict[int, OrderedDict[int, ContextMap]]

    # Ensure ngrams are ordered by decreasing frequency.
    sorted_ngrams = sorted(ngrams.items(), key=lambda x: x[1], reverse=True)

    for ngram, freq in sorted_ngrams:
        # Add n-gram "as-is" with empty context.
        _update_model(model, 1, freq, ngram, "", "")

        # tokens = ngram.split(" ")
        # size = len(tokens)

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

    context.add_context(center, left_context, right_context)
    model.setdefault(size, OrderedDict())  # initialize dictionary count -> ContextMap if needed
    model[size][freq] = context
