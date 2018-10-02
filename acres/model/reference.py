"""
Model class that represents a reference standard.
"""
from typing import List


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
        # self.second_expansion = fields[4].strip()
        # self.third_expansion = fields[6].strip()


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