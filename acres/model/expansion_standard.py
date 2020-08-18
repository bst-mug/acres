"""
Model class that represents an expansion standard. An expansion standard is the main reference
standard containing acronyms-expansion pairs and their evaluation following the TREC standard
(2/1/0).

It is designed as an append-only list (i.e., entries do not need to be updated with variable
inputs).
"""
import logging
from itertools import islice
from typing import Dict, TextIO, Set, List

from acres.model import detection_standard, topic_list
from acres.resolution import resolver
from acres.util import acronym as acro_util

logger = logging.getLogger(__name__)


def parse(filename: str) -> Dict[str, Dict[str, int]]:
    """
    Parse a TSV-separated expansion standard into a dictionary.

    :param filename:
    :return: A dictionary with acronyms pointing to expansions and an assessment value.
    """
    file = open(filename, "r", encoding="utf-8")

    expansion_standard = {}  # type: Dict[str, Dict[str, int]]
    for row in file:
        fields = row.split("\t")
        acronym = fields[0].strip()
        # fields[0] = "Q0" (NOOP)
        expansion = fields[2].strip()
        relevance = int(fields[3].strip())

        # Initialize sub-dict
        if acronym not in expansion_standard:
            expansion_standard[acronym] = {}

        expansion_standard[acronym].update({expansion: relevance})

    file.close()
    return expansion_standard


def _write_expansions(acronym: str, expansions: Dict[str, int], file: TextIO) -> None:
    for expansion, relevance in expansions.items():
        row = [acronym, "Q0", expansion, str(relevance)]
        file.write("\t".join(row) + "\n")
    file.flush()


def write(filename: str, previous: Dict[str, Dict[str, int]], valid: Set[str],
          topics: List[acro_util.Acronym]) -> None:
    """
    Write results in the TREC format, one candidate expansion per line.

    :param filename:
    :param previous: A dictionary of acronyms mapped to their senses and assesments (if any).
    :param valid: A set of valid acronyms, normally parsed from a detection standard.
    :param topics: A topic list.
    :return:Ø
    """
    file = open(filename, "w+", encoding="utf-8")

    # Write all old expansions.
    for acronym, old_expansions in previous.items():
        _write_expansions(acronym, old_expansions, file)

    types = set()
    for contextualized_acronym in topics:
        acronym = contextualized_acronym.acronym

        # Skip invalid acronyms.
        if acronym not in valid:
            continue

        # Do not repeat acronyms.
        if acronym in types:
            continue
        types.add(acronym)

        # Collect old expansions for this acronym.
        previous_expansions = set()
        if acronym in previous:
            previous_expansions = previous[acronym].keys()

        # Write all expansions in the dictionary without filtering.
        dictionary = resolver.resolve(acronym, "", "", resolver.Strategy.DICTIONARY)
        dictionary = [exp for exp in dictionary if exp not in previous_expansions]
        _write_expansions(acronym, dict.fromkeys(dictionary, -int(resolver.Strategy.DICTIONARY)),
                          file)
        previous_expansions |= set(dictionary)

        # Write up to k remaining expansions provided by all strategies.
        k = 10
        for strategy in resolver.Strategy:
            logger.info("Strategy: %s", strategy)
            filtered_expansions = resolver.filtered_resolve(acronym, "", "", strategy)

            filtered_expansions = [exp for exp in list(islice(filtered_expansions, k))
                                   if exp not in previous_expansions]
            _write_expansions(acronym, dict.fromkeys(filtered_expansions, -int(strategy.value)),
                              file)
            previous_expansions |= set(filtered_expansions)

    file.close()


if __name__ == "__main__":
    standard = "resources/expansion_standard.tsv"
    write(standard, parse(standard),
          detection_standard.parse_valid("resources/detection_standard.tsv"),
          topic_list.parse("resources/topic_list.tsv"))
