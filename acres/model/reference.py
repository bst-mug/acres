"""
Model class that represents a reference standard.
"""
from typing import List

from acres.util import acronym as acro_util


class ReferenceRow:
    """
    Class that helds data for each row in the reference standard.
    """

    def __init__(self, row: str):
        fields = row.split("\t")

        # TODO https://github.com/bst-mug/acres/issues/21
        self.left_context = fields[0].strip()
        self.acronym = fields[1].strip()
        self.right_contect = fields[2].strip()

        self.first_expansion = fields[3].strip()
        self.second_expansion = fields[4].strip()
        self.third_expansion = fields[5].strip()

        self.acronym_type = fields[6].strip()
        self.expansion = fields[7].strip()


def parse(filename: str) -> List[ReferenceRow]:
    """
    Parses a .tsv-formatted reference file into a list of ReferenceRow's.

    :param filename:
    :return:
    """
    file = open(filename, "r", encoding="utf-8")

    gold_standard = []  # type: List[ReferenceRow]
    for row in file:
        gold_standard.append(ReferenceRow(row))

    file.close()
    return gold_standard


def filter_valid(standard: List[ReferenceRow]) -> List[ReferenceRow]:
    """
    Filter out invalid entries from a gold standard. Invalid entries are not proper acronyms,
    not common acronyms, or repeated types.

    :param standard:
    :return:
    """
    filtered_standard = []

    types = set()

    for row in standard:
        if not acro_util.is_acronym(row.acronym):
            continue
        if row.acronym_type != "acro":
            continue
        if row.expansion != "common":
            continue
        if row.acronym in types:
            continue

        types.add(row.acronym)
        filtered_standard.append(row)

    return filtered_standard
