"""
Benchmark code.
"""

import logging
import time
from enum import Enum
from typing import Dict, Tuple, List

from acres.ngram import finder
from acres.nn import test
from acres.rater import rater
from acres.util import acronym as acro_util
from acres.util import text

logger = logging.getLogger(__name__)


class Strategy(Enum):
    """
    Enum that holds acronym-solving strategies.
    """
    NGRAM = 1
    WORD2VEC = 2


class Level(Enum):
    """
    Enum that holds acronym-solving levels.
    """
    TOKEN = 1
    TYPE = 2


NGRAM_CACHE = {}  # type: Dict[Tuple, List[str]]
WORD2VEC_CACHE = {}  # type: Dict[Tuple, List[str]]


def cached_resolve(acronym: str, left_context: str, right_context: str,
                   strategy: Strategy) -> List[str]:
    """
    Resolve a given acronym + context using the provideed Strategy.
    Leverages a cache of previous resolutions to speed up processing of long files.

    @todo Shorten context by using _bbuild_search_ngrams so that cache is more used

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
        Strategy.NGRAM: finder.robust_find_embeddings,
        Strategy.WORD2VEC: test.find_candidates
    }

    func = switcher.get(strategy)

    # TODO Might not be needed after new gold standard (#35)
    # Get the first acronym of an eventual pair
    acronym = text.clean(acronym).split()[0]

    filtered_expansions = []
    for expansion in func(acronym, left_context, right_context):
        if rater.get_acronym_score(acronym, expansion) > 0:
            filtered_expansions.append(expansion)

    return filtered_expansions


def test_input(true_expansions: List[str], possible_expansions: List[str],
               max_tries: int = 10) -> bool:
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
            # TODO normalize german chars in true_expansions
            if true_expansion.lower().startswith(possible_expansion.lower()):
                logger.debug("FOUND: %s", possible_expansion)
                return True
    return False


def analyze_row(input_row: str, strategy: Strategy, level: Level) -> Dict[str, bool]:
    """
    Analyze a given row of the gold standard.

    :param level:
    :param input_row: A tab-separated string
    :param strategy:
    :return: A dictionary with three keys: 'found', 'correct', and 'ignored', each key pointing to \
    a boolean
    """
    ret = {'found': False, 'correct': False, 'ignored': False}

    if input_row == "":
        ret['ignored'] = True
        return ret

    row = input_row.strip("\n")

    splitted_row = row.split("\t")

    left_context = text.context_ngram(splitted_row[0], 3, True)
    acronym = splitted_row[1]
    right_context = text.context_ngram(splitted_row[2], 3, False)
    true_expansions = splitted_row[3:]

    logger.info("CURRENT: %s [%s] %s => %s", left_context, acronym, right_context, true_expansions)

    # Remove any symbols from the true expansion
    # TODO Might not be needed after new gold standard (#35)
    true_expansions = list(map(text.clean, true_expansions))

    # A gold standard should not contain invalid acronyms
    # This is actually a required check, as some long and invalid acronyms
    # (e.g. "ACE-Hemmerunverträglichkeit") lead to performance issues.
    if not acro_util.is_acronym(acronym):
        ret['ignored'] = True
        return ret

    if level == Level.TYPE:
        left_context = ""
        right_context = ""
        key = (acronym, left_context, right_context)

        # We currently do not support Level.TOKEN for Strategy.NGRAM.
        # This is checked in `do_analysis`.
        if key in WORD2VEC_CACHE:
            ret['ignored'] = True
            return ret


    possible_expansions = cached_resolve(acronym, left_context, right_context, strategy)
    logger.debug(possible_expansions)

    ret['found'] = True if possible_expansions else ret['found']
    ret['correct'] = test_input(true_expansions, possible_expansions)

    return ret


def analyze_file(filename: str, strategy: Strategy, level: Level) -> Tuple[float, float]:
    """
    Analyzes a gold standard with text excerpts centered on an acronym, followed by n valid
    expansions.

    :param level:
    :param filename: A tab-separated file that contains the records from the gold standard. \
    Syntax: \
    left context<TAB>acronym<TAB>right context<TAB>valid expansion 1<TAB>valid expansion 2<TAB>...
    :param strategy:
    :return: A tuple with final_precision and final_recall
    """
    total_acronyms = valid_acronyms = total_correct = total_found = 0

    file = open(filename, "r", encoding="utf-8")

    for row in file:
        total_acronyms += 1
        row_analysis = analyze_row(row, strategy, level)
        if row_analysis['found']:
            total_found += 1

        if row_analysis['correct']:
            total_correct += 1

        if not row_analysis['ignored']:
            valid_acronyms += 1

        # Peeking into results
        if logger.getEffectiveLevel() == logging.DEBUG:
            precision = _calculate_precision(total_correct, total_found)
            recall = _calculate_recall(total_correct, valid_acronyms)
            f1 = calculate_f1(precision, recall)
            logger.debug("P = %f, R = %f, F1 = %f", precision, recall, f1)

    file.close()

    invalid_absolute = total_acronyms - valid_acronyms
    invalid_relative = 100 * invalid_absolute / total_acronyms
    logger.info("%d out of %d (%.2f%%) acronyms were ignored.", invalid_absolute, total_acronyms,
                invalid_relative)

    precision = _calculate_precision(total_correct, total_found)
    recall = _calculate_recall(total_correct, valid_acronyms)

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


def do_analysis(filename: str, strategy: Strategy, level: Level) -> None:
    """
    Analyzes a given reference standard.

    :param level:
    :param filename:
    :param strategy:
    :return:
    """
    if strategy == Strategy.NGRAM and level == Level.TYPE:
        logger.error("N-GRAM strategy does not support TYPE level.")
        return

    start_time = time.time()
    (final_precision, final_recall) = analyze_file(filename, strategy, level)
    end_time = time.time()

    print("Time: (s)", end_time - start_time)

    final_f1 = calculate_f1(final_precision, final_recall)
    print("Precision: ", final_precision)
    print("Recall: ", final_recall)
    print("F1: ", final_f1)


if __name__ == "__main__":
    # XXX Switch as desired
    # do_analysis("resources/gold_standard.tsv", Strategy.NGRAM)
    do_analysis("resources/gold_standard.tsv", Strategy.WORD2VEC, Level.TYPE)
