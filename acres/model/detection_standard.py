"""
Model class that represents a detection standard.
"""
import logging
from typing import Dict, Set, List

from acres.model import topic_list
from acres.model.topic_list import Acronym
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


def parse_valid(filename: str) -> Set[str]:
    """
    Wrapper method for both `parse` and `filter_valid`.

    :param filename:
    :return:
    """
    return filter_valid(parse(filename))


def update(previous: Dict[str, bool], acronyms: List[Acronym]) -> Dict[str, bool]:
    """
    Update a previous detection standard with new acronyms from a topic list, preserving order.

    :param previous:
    :param acronyms:
    :return:
    """
    ret = previous
    for acronym in acronyms:
        if acronym.acronym not in ret:
            ret[acronym.acronym] = True
    return ret


def write(filename: str, standard: Dict[str, bool]) -> None:
    """
    Write a detection standard into a file.

    :param filename:
    :param standard:
    :return:
    """
    file = open(filename, "w+", encoding="utf-8")
    for acronym, valid in standard.items():
        file.write(acronym)
        file.write("\t")
        file.write(str(valid).upper())
        file.write("\n")
    file.close()


if __name__ == "__main__":
    detection_standard = "resources/detection_standard.tsv"
    write(detection_standard,
          update(parse(detection_standard), topic_list.parse("resources/topic_list.tsv")))
