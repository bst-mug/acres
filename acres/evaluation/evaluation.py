"""
Benchmark code.
"""

import logging
from logging.config import fileConfig
from typing import Dict, Tuple

logging.config.fileConfig("logging.ini")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from acres import get_synonyms_from_ngrams
from acres.nn import test


def test_input(true_expansions: list, possible_expansions: list) -> bool:
    """
    Tests an acronym + context strings against the ngram model

    :param true_expansions:
    :param possible_expansions:
    :return:
    """
    for possible_expansion in possible_expansions:
        logger.debug(possible_expansion)
        for true_expansion in true_expansions:
            if possible_expansion.lower() == true_expansion.lower():
                logger.debug("FOUND: " + possible_expansion)
                return True
    return False


def analyze_row(input_row: str) -> Dict[str, bool]:
    """
    Analyze a given row of the gold standard.

    :param input_row: A tab-separated string
    :return: A dictionary with two keys: 'found' and 'correct', each key pointing to a boolean
    """
    ret = {'found': False, 'correct': False}

    if input_row == "":
        return ret

    row = input_row.strip("\n")
    logger.info("Analyzing: " + row)

    splitted_row = row.split("\t")

    left_context = splitted_row[0]
    acronym = splitted_row[1]
    right_context = splitted_row[2]
    true_expansions = splitted_row[3:]

    # ngram-embeddings
    # possible_expansions = get_synonyms_from_ngrams.robust_find_embeddings(acronym, left_context, right_context)

    # word2vec
    possible_expansions = test.find_candidates(acronym, left_context, right_context)

    ret['found'] = True if len(possible_expansions) > 0 else ret['found']
    ret['correct'] = test_input(true_expansions, possible_expansions)

    return ret


def analyze_file(filename: str) -> Tuple[float, float]:
    """
    Analyzes a gold standard with text excerpts centered on an acronym, followed by n valid
    expansions.

    :param filename: A tab-separated file that contains the records from the gold standard. Syntax:
    left context<TAB>acronym<TAB>right context<TAB>valid expansion 1<TAB>valid expansion 2<TAB>...
    :return: A tuple with precision and recall
    """
    total_acronyms = total_correct = total_found = 0

    f = open(filename, "r", encoding="utf-8")

    for row in f:
        total_acronyms += 1
        row_analysis = analyze_row(row)
        if row_analysis['found']:
            total_found += 1

        if row_analysis['correct']:
            total_correct += 1
            logger.debug("CORRECT")

        # Peeking into results
        if logger.getEffectiveLevel() == logging.DEBUG:
            precision = _calculate_precision(total_correct, total_found)
            recall = _calculate_recall(total_correct, total_acronyms)
            f1 = calculate_f1(precision, recall)
            logger.debug("P = %f, R = %f, F1 = %f", precision, recall, f1)

    f.close()

    precision = _calculate_precision(total_correct, total_found)
    recall = _calculate_recall(total_correct, total_acronyms)

    return precision, recall


def _calculate_precision(total_correct: int, total_found: int) -> float:
    return total_correct / total_found if total_found != 0 else 0


def _calculate_recall(total_correct: int, total_acronyms: int) -> float:
    return total_correct / total_acronyms if total_acronyms != 0 else 0


def calculate_f1(precision: float, recall: float) -> float:
    """
    Calculates the F1-score.

    :param precision:
    :param recall:
    :return:
    """
    return (2 * precision * recall) / (precision + recall) if (precision + recall) != 0 else 0


if __name__ == "__main__":
    (precision, recall) = analyze_file("resources/Workbench.txt")

    f1 = calculate_f1(precision, recall)
    print("Precision: ", precision)
    print("Recall: ", recall)
    print("F1: ", f1)
