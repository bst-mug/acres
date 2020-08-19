"""
Facade to the several expansion strategies.

.. codeauthor:: Michel Oleynik
"""
from enum import IntEnum
from typing import List, Iterator

from acres.fastngram import fastngram
from acres.nn import test
from acres.rater import rater
from acres.stats import dictionary
from acres.util import text


class Strategy(IntEnum):
    """
    Enum that holds acronym-solving strategies.
    """
    WORD2VEC = 2
    DICTIONARY = 3
    FASTNGRAM = 4
    BASELINE = 5
    FASTTYPE = 6


def filtered_resolve(acronym: str, left_context: str, right_context: str,
                     strategy: Strategy) -> Iterator[str]:
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

    for expansion in expansions:
        if rater.get_acronym_score(acronym, expansion) > 0:
            yield expansion


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
        Strategy.WORD2VEC: test.find_candidates,
        Strategy.DICTIONARY: dictionary.expand,
        Strategy.FASTNGRAM: fastngram.fastngram,
        Strategy.BASELINE: fastngram.baseline,
        Strategy.FASTTYPE: fastngram.fasttype
    }

    func = switcher.get(strategy)
    return func(acronym, left_context, right_context)
