"""
Benchmark code.
"""

import logging
from logging.config import fileConfig

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import time
from enum import Enum
from typing import Dict, Tuple, List

from acres import get_synonyms_from_ngrams
from acres.nn import test


class Strategy(Enum):
    NGRAM = 1
    WORD2VEC = 2


NGRAM_CACHE = {}  # type: Dict[Tuple, List[str]]
WORD2VEC_CACHE = {}  # type: Dict[Tuple, List[str]]


def cached_resolve(acronym: str, left_context: str, right_context: str, strategy: Strategy) -> List[
    str]:
    """
    Resolve a given acronym + context using the provideed Strategy.
    Leverages a cache of previous resolutions to speed up processing of long files.

    @todo Shorten context by using _build_search_ngrams so that cache is more used

    :param acronym:
    :param left_context:
    :param right_context:
    :param strategy:
    :return:
    """
    switcher = {
        Strategy.NGRAM: NGRAM_CACHE,
        Strategy.WORD2VEC: WORD2VEC_CACHE
    }

    cache = switcher.get(strategy)
    key = (acronym, left_context, right_context)

    # Check cache entry
    if key not in cache:
        cache[key] = _resolve(acronym, left_context, right_context, strategy)

    return cache[key]


def _resolve(acronym: str, left_context: str, right_context: str, strategy: Strategy) -> List[str]:
    """
    Resolve a given acronym + context using the provideed Strategy.

    :param acronym:
    :param left_context:
    :param right_context:
    :param strategy:
    :return:
    """
    switcher = {
        Strategy.NGRAM: get_synonyms_from_ngrams.robust_find_embeddings,
        Strategy.WORD2VEC: test.find_candidates
    }

    func = switcher.get(strategy)
    return func(acronym, left_context, right_context)


def test_input(true_expansions: list, possible_expansions: list, max_tries: int = 10) -> bool:
    """
    Tests an acronym + context strings against the ngram model

    :param true_expansions:
    :param possible_expansions:
    :param max_tries: Maxinum number of tries
    :return:
    """
    i = 0
    for possible_expansion in possible_expansions:
        i += 1
        if i > max_tries:
            break
        # logger.debug(possible_expansion)
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

    ngram_expansions = cached_resolve(acronym, left_context, right_context, Strategy.NGRAM)
    logger.debug(ngram_expansions)

    word2vec_expansions = cached_resolve(acronym, left_context, right_context, Strategy.WORD2VEC)
    logger.debug(word2vec_expansions)

    # XXX Switch as desired
    possible_expansions = word2vec_expansions

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
    start_time = time.time()
    (precision, recall) = analyze_file("resources/Workbench.txt")
    end_time = time.time()

    print("Time: (s)", end_time - start_time)

    f1 = calculate_f1(precision, recall)
    print("Precision: ", precision)
    print("Recall: ", recall)
    print("F1: ", f1)
