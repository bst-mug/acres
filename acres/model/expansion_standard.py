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


def _write_expansions(acronym: str, expansions: Dict[str, int], file: TextIO) -> None:
    for expansion, relevance in expansions.items():
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
        filtered_expansions = resolver.filtered_resolve(acronym, "", "", strategy)
        expansions = resolver.resolve(acronym, "", "", strategy)

        # Write all old expansions
        _write_expansions(acronym, old_expansions, file)
        previous_expansions = old_expansions.keys()

        # Write all expansions in the dictionary
        dictionary = resolver.resolve(acronym, "", "", resolver.Strategy.DICTIONARY)
        dictionary = [exp for exp in dictionary if exp not in previous_expansions]
        _write_expansions(acronym, dict.fromkeys(dictionary, -1), file)
        previous_expansions |= set(dictionary)

        k = 5

        # Write up to k filtered expansions not in old
        filtered_expansions = [exp for exp in filtered_expansions[:k]
                               if exp not in previous_expansions]
        _write_expansions(acronym, dict.fromkeys(filtered_expansions, -2), file)
        previous_expansions |= set(filtered_expansions)

        # Write up to k remaining expansions
        expansions = [exp for exp in expansions[:k] if exp not in previous_expansions]
        _write_expansions(acronym, dict.fromkeys(expansions, -3), file)

    file.close()


if __name__ == "__main__":
    write_results("resources/results.tsv", parse("resources/expansion_standard.tsv"))
