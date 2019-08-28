"""
Model class that represents a topic list.
"""
from collections import namedtuple
from typing import List, Set

Acronym = namedtuple('Acronym', ['acronym', 'left_context', 'right_context'])


def parse(filename: str) -> List[Acronym]:
    """
    Parses a TSV-formatted topic list into a list of acronyms (with context).

    :param filename:
    :return:
    """
    file = open(filename, "r", encoding="utf-8")

    topic_list = [] # type: List[Acronym]
    for row in file:
        fields = row.split("\t")
        left_context = fields[0].strip()
        acronym = fields[1].strip()
        right_context = fields[2].strip()

        contextualized_acronym = Acronym(acronym=acronym, left_context=left_context,
                                         right_context=right_context)
        topic_list.append(contextualized_acronym)

    return topic_list


def unique_types(topics: List[Acronym]) -> Set[str]:
    """
    Extract types from a topic list.

    :param topics:
    :return:
    """
    types = set()   # type: Set[str]
    for contextualized_acronym in topics:
        types.add(contextualized_acronym.acronym)
    return types
