"""
Model class that represents an expansion standard.
"""
from typing import Dict, TextIO

from acres.resolution import resolver


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


def _write_expansions(acronym: str, expansions: Dict[str, int], file: TextIO, k: int = 10) -> None:
    i = 0
    for expansion, relevance in expansions.items():
        # Print only top-k results
        i = i + 1
        if i > k:
            break

        row = [acronym, "Q0", expansion, str(relevance)]
        file.write("\t".join(row) + "\n")


def write_results(filename: str, acronyms: Dict[str, Dict[str, int]]) -> None:
    """
    Write results in the TREC format, one candidate expansion per line.

    :param filename:
    :param acronyms: A dictionary of acronyms mapped to their senses and assesments (if any).
    :return:Ø
    """
    file = open(filename, "w+", encoding="utf-8")

    for acronym, old_expansions in acronyms.items():
        strategy = resolver.Strategy.WORD2VEC
        filtered_expansions = resolver.cached_resolve(acronym, "", "", strategy)
        expansions = resolver.resolve(acronym, "", "", strategy)

        # Write all old expansions
        _write_expansions(acronym, old_expansions, file, 1000)

        # Write 5 filtered expansions not in old
        # TODO we want actually only from the top-5, otherwise we keep growing the GS
        filtered_expansions = [exp for exp in filtered_expansions if
                               exp not in old_expansions.keys()]
        _write_expansions(acronym, dict.fromkeys(filtered_expansions, -1), file, 5)

        # Write 5 remaining expansions
        expansions = [exp for exp in expansions if
                      exp not in set(old_expansions) and exp not in set(filtered_expansions)]
        _write_expansions(acronym, dict.fromkeys(expansions, -2), file, 5)

    file.close()


if __name__ == "__main__":
    write_results("resources/results.tsv", parse("resources/expansion_standard.tsv"))
