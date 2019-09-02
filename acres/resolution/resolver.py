from enum import Enum
from typing import List, Dict, Tuple

from acres.fastngram import fastngram
from acres.ngram import finder
from acres.nn import test
from acres.rater import rater
from acres.stats import dictionary
from acres.util import text


class Strategy(Enum):
    """
    Enum that holds acronym-solving strategies.
    """
    NGRAM = 1
    WORD2VEC = 2
    DICTIONARY = 3
    FASTNGRAM = 4
    BASELINE = 5


NGRAM_CACHE = {}  # type: Dict[Tuple, List[str]]
WORD2VEC_CACHE = {}  # type: Dict[Tuple, List[str]]
DICTIONARY_CACHE = {}  # type: Dict[Tuple, List[str]]
FASTNGRAM_CACHE = {}  # type: Dict[Tuple, List[str]]
BASELINE_CACHE = {}  # type: Dict[Tuple, List[str]]


def cached_resolve(acronym: str, left_context: str, right_context: str,
                   strategy: Strategy) -> List[str]:
    """
    Resolve a given acronym + context using the provideed Strategy.
    Leverages a cache of previous resolutions to speed up processing of long files.

    @todo Shorten context by using _bbuild_search_ngrams so that cache is more used

    :param acronym:
    :param left_context:
    :param right_context:
    :param strategy:
    :return:
    """
    switcher = {
        Strategy.NGRAM: NGRAM_CACHE,
        Strategy.WORD2VEC: WORD2VEC_CACHE,
        Strategy.DICTIONARY: DICTIONARY_CACHE,
        Strategy.FASTNGRAM: FASTNGRAM_CACHE,
        Strategy.BASELINE: BASELINE_CACHE
    }

    cache = switcher.get(strategy)
    key = (acronym, left_context, right_context)

    # Check cache entry
    if key not in cache:
        cache[key] = _filter_resolve(acronym, left_context, right_context, strategy)

    return cache[key]


def _filter_resolve(acronym: str, left_context: str, right_context: str, strategy: Strategy) -> \
List[str]:
    """
    Resolve a given acronym + context using the provided Strategy and filter out invalid expansions.

    :param acronym:
    :param left_context:
    :param right_context:
    :param strategy:
    :return:
    """
    # TODO Might not be needed after new gold standard (#35)
    # Get the first acronym of an eventual pair
    acronym = text.clean(acronym).split()[0]

    expansions = resolve(acronym, left_context, right_context, strategy)

    filtered_expansions = []
    for expansion in expansions:
        if rater.get_acronym_score(acronym, expansion) > 0:
            filtered_expansions.append(expansion)

    return filtered_expansions


def resolve(acronym: str, left_context: str, right_context: str, strategy: Strategy) -> List[str]:
    """
    Resolve a given acronym + context using the provided Strategy.

    :param acronym:
    :param left_context:
    :param right_context:
    :param strategy:
    :return:
    """
    switcher = {
        Strategy.NGRAM: finder.robust_find_embeddings,
        Strategy.WORD2VEC: test.find_candidates,
        Strategy.DICTIONARY: dictionary.expand,
        Strategy.FASTNGRAM: fastngram.expand,
        Strategy.BASELINE: fastngram.baseline
    }

    func = switcher.get(strategy)
    return func(acronym, left_context, right_context)
