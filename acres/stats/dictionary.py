"""
Metrics from large German acronym / definition list
"""
from typing import List

import acres.util.acronym
import acres.util.functions


def dump_sample(min_len: int = 1, max_len: int = 15) -> List[str]:
    """

    :param min_len:
    :param max_len:
    :return:
    """
    ret = []
    file = open("resources/acro_full_reference.txt", "r", encoding="utf-8")
    for line in file:
        acro = line.split("\t")[0]
        if min_len <= len(acro) <= max_len:
            ret.append(line.strip())
    file.close()
    return ret


def show_extremes(txt: str, lst: List, lowest_n: int, highest_n: int) -> None:
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


if __name__ == "__main__":
    senses = dump_sample(3, 3)
    for line in senses:
        acro = line.split("\t")[0].strip()
        full = line.split("\t")[1].strip()
        if not acres.util.acronym.is_acronym(acro):
            print(acro + " is not an acronym according to our definition")
        if full.count(" ") + 1 > len(acro) * 2:
            print(acro + " contradicts Schwartz / Hearst rule")
        if full.count(" ") + 1 > len(acro) + 5:
            print(acro + " contradicts Schwartz / Hearst rule")

    analyzed_senses = []  ## ratio acro / words
    for line in senses:
        acro = line.split("\t")[0]
        full = line.split("\t")[1]
        full_norm = full.replace("/", " ").replace("-", " ").replace("  ", " ").strip()
        c_words_full = full_norm.count(" ") + 1
        c_chars_acro = len(acro)
        rat = round(c_chars_acro / c_words_full, 2)
        analyzed_senses.append((rat, acro, full))

    show_extremes("Ratio acronym length / words in full form", analyzed_senses, 10, 10)

    analyzed_senses = []  ## edit distance with generated acronym
    for line in senses:
        acro = line.split("\t")[0]
        full = line.split("\t")[1]
        if abs(len(acro) - full.count(" ") - 1) <= 2:
            n_acro = acres.util.acronym.create_german_acronym(full)
            lev = acres.util.functions.levenshtein(acro.upper(), n_acro)
            analyzed_senses.append((lev, acro, full))

    show_extremes("edit distance with generated acronym", analyzed_senses, 10, 10)
