"""
Module to collect metrics from a sense inventory. This module can be used to debug the sense
inventory e.g. by detecting extreme expansions. It can also be used to debug methods that relies on
real data.
"""
from typing import List, Tuple, Optional, Dict

import Levenshtein

from acres.preprocess import resource_factory
from acres.rater import expansion
from acres.rater import rater
from acres.util import acronym as acro_util


def expand(acronym: str, left_context: str = "", right_context: str = "") -> List[str]:
    """

    :param acronym:
    :param left_context:
    :param right_context:
    :return:
    """
    dictionary = resource_factory.get_dictionary()
    if acronym not in dictionary:
        return []
    return dictionary[acronym]


def _tuple2dictionary(senses: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    """
    Convert the sense inventory as a list of tuples to a Python dictionary for better search \
    performance.

    :param senses:
    :return:
    """
    dictionary = {}  # type: Dict[str, List[str]]
    for acro, full in senses:
        # Initialize sub-list
        if acro not in dictionary:
            dictionary[acro] = []
        dictionary[acro].append(full)
    return dictionary


def parse(filename: str) -> Dict[str, List[str]]:
    """
    Parse a tab-separated sense inventory as a Python dictionary.

    :param filename:
    :return:
    """
    return _tuple2dictionary(_dump_sample(filename))


def _dump_sample(filename: str, max_len: int = 15, min_len: int = 1) -> List[Tuple[str, str]]:
    """

    :param filename:
    :param min_len:
    :param max_len:
    :return:
    """
    ret = []
    file = open(filename, "r", encoding="utf-8")
    for line in file:
        acronym = line.split("\t")[0].strip()
        full_form = line.split("\t")[1].strip()
        if min_len <= len(acronym) <= max_len:
            ret.append((acronym, full_form))
    file.close()
    return ret


def show_extremes(txt: str, lst: List, lowest_n: int = 10, highest_n: int = 10) -> None:
    """

    :param txt:
    :param lst:
    :param lowest_n:
    :param highest_n:
    :return:
    """
    if len(lst) <= lowest_n + highest_n:
        print("List too small")
    else:
        print("\n==========================================")
        print(txt)
        print("==========================================\n")
        counter = 0
        for i in sorted(lst):
            print(i)
            counter += 1
            if counter >= lowest_n:
                break
        print("(...)")
        counter = 0
        for i in sorted(lst, reverse=True):
            print(i)
            counter += 1
            if counter >= lowest_n:
                break


def ratio_acro_words(acro: str, full: str) -> Tuple:
    """
    Calculates the ratio of acronym lenfth to the number of words in the full form.

    :param acro:
    :param full:
    :return:
    """
    full_norm = full.replace("/", " ").replace("-", " ").replace("  ", " ").strip()
    c_words_full = full_norm.count(" ") + 1
    c_chars_acro = len(acro)
    rat = round(c_chars_acro / c_words_full, 2)
    return rat, acro, full


def edit_distance_generated_acro(acro: str, full: str) -> Optional[Tuple]:
    """
    Calculates the edit distance between the original acronym and the generated acronym out of the
    full form.

    :param acro:
    :param full:
    :return:
    """
    ret = None
    if abs(len(acro) - full.count(" ") - 1) <= 2:
        n_acro = acro_util.create_german_acronym(full)
        lev = Levenshtein.distance(acro.upper(), n_acro)
        ret = (lev, acro, full)
    return ret


def analyze_file(filename: str) -> None:
    """
    Analyzes a given dictionary file for extreme cases.

    :param filename:
    :return:
    """
    senses = _dump_sample(filename, 3, 3)
    for (acro, full) in senses:
        if not acro_util.is_acronym(acro):
            print(acro + " is not an acronym according to our definition")
        if not expansion._is_schwarzt_hearst_valid(acro, full):
            print(acro + " contradicts Schwartz / Hearst rule")

    analyzed_senses = []  # ratio acro / words
    for (acro, full) in senses:
        analyzed_senses.append(ratio_acro_words(acro, full))
    show_extremes("Ratio acronym length / words in full form", analyzed_senses)

    analyzed_senses = []  # edit distance with generated acronym
    for (acro, full) in senses:
        distance = edit_distance_generated_acro(acro, full)
        if distance:
            analyzed_senses.append(distance)
    show_extremes("edit distance with generated acronym", analyzed_senses)

    analyzed_senses = []  # get_acronym_score
    for (acro, full) in senses:
        score = (rater.get_acronym_score(acro, full), acro, full)
        analyzed_senses.append(score)
    show_extremes("get_acronym_score", analyzed_senses)

    analyzed_senses = []  # _compute_expansion_valid
    for (acro, full) in senses:
        compute = (expansion._compute_expansion_valid(acro, full), acro, full)
        analyzed_senses.append(compute)
    show_extremes("_compute_expansion_valid", analyzed_senses)


if __name__ == "__main__":
    analyze_file("resources/acro_full_reference.txt")
