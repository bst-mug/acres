"""
Model class that represents a detection standard.
"""
import logging
from typing import Dict, Set

from acres.util import acronym as acro_util

logger = logging.getLogger(__name__)


def parse(filename: str) -> Dict[str, bool]:
    """
    Parses a .tsv-formatted detection standard into a dictionary.

    :param filename:
    :return:
    """
    file = open(filename, "r", encoding="utf-8")

    detection_standard = {}  # type: Dict[str, bool]
    for row in file:
        fields = row.split("\t")
        acronym = fields[0].strip()
        valid = fields[1].strip() == 'TRUE'
        # Remaining fields are ignored, because they map into `valid`.

        detection_standard[acronym] = valid

    file.close()
    return detection_standard


def filter_valid(standard: Dict[str, bool]) -> Set[str]:
    """
    Filter out invalid entries from a gold standard. Invalid entries are not proper acronyms
    or repeated types.

    :param standard:
    :return:
    """
    types = set()  # type: Set[str]

    for acronym, valid in standard.items():
        if not valid:
            continue

        # A gold standard should not contain invalid acronyms
        # This is actually a required check, as some long and invalid acronyms
        # (e.g. "ACE-Hemmerunverträglichkeit") lead to performance issues.
        if not acro_util.is_acronym(acronym):
            logger.debug("{%s} does not pass acronym tests.", acronym)
            continue

        if acronym in types:
            logger.debug("{%s} is repeated at least once.", acronym)
            continue

        types.add(acronym)

    return types


if __name__ == "__main__":
    filter_valid(parse("resources/detection_standard.tsv"))
