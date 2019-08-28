"""
Module to estimate acronym ambiguity.
"""
from typing import Dict, Set

from acres.model import expansion_standard


def bucketize(acronyms: Dict[str, Set[str]]) -> Dict[int, int]:
    """
    Reduce: calculate the number of different acronyms for each degree of ambiguity.

    :param acronyms:
    :return:
    """
    buckets = {}  # type: Dict[int, int]
    for _, value in acronyms.items():
        senses = len(value)
        buckets.setdefault(senses, 0)
        buckets[senses] += 1
    return buckets


def map_senses_acronym(standard: Dict[str, Dict[str, int]],
                       lenient: bool = False) -> Dict[str, Set[str]]:
    """
    Map: collect senses for each acronym.

    :param standard:
    :param lenient: Whether to consider partial matches (1) as a valid sense.
    :return:
    """
    senses = {}  # type: Dict[str, Set[str]]
    for acronym, expansions in standard.items():
        senses.setdefault(acronym, set())
        for expansion, relevance in expansions.items():
            if relevance == 2 or relevance == 1 and lenient:
                senses[acronym].add(expansion)
    return senses


def get_sense_buckets(filename: str) -> Dict[str, Set[str]]:
    """
    Parses a reference standard and get a map of senses per acronym.

    :param filename:
    :return:
    """
    standard = expansion_standard.parse(filename)
    return map_senses_acronym(standard)


def print_ambiguous(filename: str) -> None:
    """
    Print ambiguous acronyms, the ones with more than one sense according to the reference standard.

    :param filename:
    :return:
    """
    acronyms = get_sense_buckets(filename)
    for key, value in acronyms.items():
        if len(value) > 1:
            print(key, sorted(value), sep="\t")


def print_undefined(filename: str) -> None:
    """
    Print undefined acronyms, the ones with no valid sense according to the reference standard.

    :param filename:
    :return:
    """
    acronyms = get_sense_buckets(filename)
    for key, value in acronyms.items():
        if not value:
            print(key, sorted(value), sep="\t")


def print_senses(filename: str) -> None:
    """
    Print the distribution of senses per acronym.

    :param filename:
    :return:
    """
    buckets = bucketize(get_sense_buckets(filename))
    for key, value in sorted(buckets.items()):
        print(key, value, sep="\t")


if __name__ == "__main__":
    WORKBENCH = "resources/expansion_standard.tsv"
    print_senses(WORKBENCH)
    print_ambiguous(WORKBENCH)
    print_undefined(WORKBENCH)
