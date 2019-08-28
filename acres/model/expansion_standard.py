from typing import List, Dict, Set, TextIO

from acres.model import detection_standard
from acres.resolution import resolver
from acres.stats import senses


def _from_old_gs(filename: str) -> Dict[str, Set[str]]:
    """
    Backwards compatibility method. Extract a list of acronyms previously selected to build a GS \
    in the non-TREC format.

    :param filename:
    :return: A dictionary of acronyms mapped to their senses.
    """
    standard = detection_standard.parse(filename)
    filtered_standard = detection_standard.filter_valid(standard)
    return senses.map_senses_acronym(filtered_standard)


def _write_expansions(acronym: str, expansions: List[str], file: TextIO,
                      k: int = 10, assessment: int = -1) -> None:
    i = 0
    for expansion in expansions:
        # Print only top-k results
        i = i + 1
        if i > k:
            break

        row = [acronym, "Q0", '"' + expansion + '"', str(assessment)]
        file.write("\t".join(row) + "\n")


def write_results(filename: str, acronyms: Dict[str, Set[str]]) -> None:
    """
    Write results in the TREC format, one candidate expansion per line.

    :param filename:
    :param acronyms: A dictionary of acronyms mapped to their senses (if any).
    :return:Ø
    """
    file = open(filename, "w+", encoding="utf-8")

    for acronym, old_expansions in acronyms.items():
        strategy = resolver.Strategy.WORD2VEC
        filtered_expansions = resolver.cached_resolve(acronym, "", "", strategy)
        expansions = resolver._resolve(acronym, "", "", strategy)

        # Write all old expansions
        _write_expansions(acronym, list(old_expansions), file, 1000, 2)

        # Write 5 filtered expansions not in old
        filtered_expansions = [exp for exp in filtered_expansions if exp not in set(old_expansions)]
        _write_expansions(acronym, filtered_expansions, file, 5)

        # Write 5 remaining expansions
        expansions = [exp for exp in expansions if
                      exp not in set(old_expansions) and exp not in set(filtered_expansions)]
        _write_expansions(acronym, expansions, file, 5)

    file.close()


if __name__ == "__main__":
    write_results("resources/results.tsv", _from_old_gs("resources/gold_standard.tsv"))
