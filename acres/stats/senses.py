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
    for key, value in acronyms.items():
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
        senses[acronym].add(row.first_expansion)  # TODO consider other expansions
    return senses


def get_sense_buckets(filename: str) -> Dict[str, Set[str]]:
    """

    :param filename:
    :return:
    """
    standard = reference.parse(filename)
    return map_senses_acronym(standard)


def print_ambiguous(filename: str) -> None:
    acronyms = get_sense_buckets(filename)
    for key, value in acronyms.items():
        if len(value) > 1:
            print(key, value, sep="\t")


def print_senses(filename: str) -> None:
    buckets = bucketize(get_sense_buckets(filename))
    for key, value in sorted(buckets.items()):
        print(key, value, sep="\t")


if __name__ == "__main__":
    filename = "resources/Workbench_All.txt"
    print_senses(filename)
    print_ambiguous(filename)
