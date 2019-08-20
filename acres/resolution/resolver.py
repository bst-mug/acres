from enum import Enum
from typing import List, Dict, Tuple

from acres.ngram import finder
from acres.nn import test
from acres.rater import rater
from acres.util import text


class Strategy(Enum):
    """
    Enum that holds acronym-solving strategies.
    """
    NGRAM = 1
    WORD2VEC = 2


class Level(Enum):
    """
    Enum that holds acronym-solving levels.
    """
    TOKEN = 1
    TYPE = 2


NGRAM_CACHE = {}  # type: Dict[Tuple, List[str]]
WORD2VEC_CACHE = {}  # type: Dict[Tuple, List[str]]


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
        Strategy.WORD2VEC: WORD2VEC_CACHE
    }

    cache = switcher.get(strategy)
    key = (acronym, left_context, right_context)

    # Check cache entry
    if key not in cache:
        cache[key] = _resolve(acronym, left_context, right_context, strategy)

    return cache[key]


def _resolve(acronym: str, left_context: str, right_context: str, strategy: Strategy) -> List[str]:
    """
    Resolve a given acronym + context using the provideed Strategy.

    :param acronym:
    :param left_context:
    :param right_context:
    :param strategy:
    :return:
    """
    switcher = {
        Strategy.NGRAM: finder.robust_find_embeddings,
        Strategy.WORD2VEC: test.find_candidates
    }

    func = switcher.get(strategy)

    # TODO Might not be needed after new gold standard (#35)
    # Get the first acronym of an eventual pair
    acronym = text.clean(acronym).split()[0]

    filtered_expansions = []
    for expansion in func(acronym, left_context, right_context):
        if rater.get_acronym_score(acronym, expansion) > 0:
            filtered_expansions.append(expansion)

    return filtered_expansions
