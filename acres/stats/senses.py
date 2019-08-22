"""
Module to estimate acronym ambiguity.
"""
from typing import Dict, List, Set

from acres.model import reference
from acres.model.reference import ReferenceRow


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


def map_senses_acronym(standard: List[ReferenceRow]) -> Dict[str, Set[str]]:
    """
    Map: collect senses for each acronym.

    :param standard:
    :return:
    """
    senses = {}  # type: Dict[str, Set[str]]
    for row in standard:
        acronym = row.acronym
        senses.setdefault(acronym, set())
        senses[acronym].add(row.first_expansion)
        if row.second_expansion:
            senses[acronym].add(row.second_expansion)
        if row.third_expansion:
            senses[acronym].add(row.third_expansion)
    return senses


def get_sense_buckets(filename: str) -> Dict[str, Set[str]]:
    """
    Parses a reference standard and get a map of senses per acronym.

    :param filename:
    :return:
    """
    standard = reference.parse(filename)
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
    WORKBENCH = "resources/gold_standard.tsv"
    print_senses(WORKBENCH)
    print_ambiguous(WORKBENCH)
