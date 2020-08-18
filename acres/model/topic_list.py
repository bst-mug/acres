"""
Model class that represents a topic list. A topic list is used as main input (a la TREC) and thus
can control which acronyms (together with their contexts) are to be considered for evaluation. A
topic list can be used, e.g., to quickly switch between different evaluation scenarios such as
acronyms collected from either the training or test dataset.
"""
from operator import attrgetter
from typing import List, Set

from acres.ngram import ngrams
from acres.util import acronym as acro_util
from acres.util import functions


def parse(filename: str) -> 'List[acro_util.Acronym]':
    """
    Parses a TSV-formatted topic list into a list of acronyms (with context).

    :param filename:
    :return:
    """
    file = open(filename, "r", encoding="utf-8")

    topic_list = []  # type: List[acro_util.Acronym]
    for row in file:
        fields = row.split("\t")
        left_context = fields[0].strip()
        acronym = fields[1].strip()
        right_context = fields[2].strip()

        contextualized_acronym = acro_util.Acronym(acronym=acronym, left_context=left_context,
                                                   right_context=right_context)
        topic_list.append(contextualized_acronym)

    return topic_list


def unique_types(topics: 'List[acro_util.Acronym]') -> Set[str]:
    """
    Extract types from a topic list.

    :param topics:
    :return:
    """
    types = set()   # type: Set[str]
    for contextualized_acronym in topics:
        types.add(contextualized_acronym.acronym)
    return types


def create(filename: str, chance: float, ngram_size: int = 7):
    """
    Create a topic list out of random n-grams with a given chance and size.

    :param filename:
    :param chance:
    :param ngram_size:
    :return:
    """
    filtered_ngrams = ngrams.FilteredNGramStat(ngram_size)
    acronyms = ngrams.filter_acronym_contexts(iter(filtered_ngrams))
    sampled = functions.sample(acronyms, chance)

    # Sort by the acronym
    sorted_acronyms = sorted(sampled, key=attrgetter('acronym'))

    file = open(filename, "w+", encoding="utf-8")
    for acronym in sorted_acronyms:
        file.write(acronym.left_context)
        file.write("\t")
        file.write(acronym.acronym)
        file.write("\t")
        file.write(acronym.right_context)
        file.write("\n")
    file.close()


if __name__ == "__main__":
    create("resources/topic_list.tsv", 0.003)
