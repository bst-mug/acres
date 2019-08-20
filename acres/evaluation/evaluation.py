"""
Benchmark code.
"""

import logging
import time
from typing import Dict, Tuple, List, Union

from acres.resolution import resolver
from acres.util import acronym as acro_util, text

logger = logging.getLogger(__name__)


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
                logger.debug("CORRECT: %s", possible_expansion)
                return True
    return False


def analyze_row(input_row: str, strategy: resolver.Strategy, level: resolver.Level) -> Dict[
    str, Union[bool, str]]:
    """
    Analyze a given row of the gold standard.

    :param level:
    :param input_row: A tab-separated string
    :param strategy:
    :return: A dictionary with keys {'found', 'correct', and 'ignored'} pointing to boolean and a \
    a key 'row' with the original row and the possible expansions.
    """
    ret = {'found': False, 'correct': False, 'ignored': False, 'row': input_row}

    if input_row == "":
        ret['ignored'] = True
        return ret

    row = input_row.strip("\n")

    splitted_row = row.split("\t")

    left_context = text.context_ngram(splitted_row[0], 3, True)
    acronym = splitted_row[1]
    right_context = text.context_ngram(splitted_row[2], 3, False)
    true_expansions = splitted_row[3:5]
    category = splitted_row[6]
    common = splitted_row[7]

    logger.info("%s [%s] %s => %s (%s - %s)", left_context, acronym, right_context,
                true_expansions, category, common)

    # Remove any symbols from the true expansion
    # TODO Might not be needed after new gold standard (#35)
    true_expansions = list(map(text.clean, true_expansions))

    # A gold standard should not contain invalid acronyms
    # This is actually a required check, as some long and invalid acronyms
    # (e.g. "ACE-Hemmerunverträglichkeit") lead to performance issues.
    if not acro_util.is_acronym(acronym):
        logger.debug("IGNORED: not is_acronym")
        ret['ignored'] = True
        return ret

    if category != "acro":
        logger.debug("IGNORED: not 'acro'")
        ret['ignored'] = True
        return ret

    if common != "common":
        logger.debug("IGNORED: not 'common'")
        ret['ignored'] = True
        return ret

    if level == resolver.Level.TYPE:
        left_context = ""
        right_context = ""
        key = (acronym, left_context, right_context)

        # We currently do not support Level.TOKEN for Strategy.NGRAM.
        # This is checked in `do_analysis`.
        if key in resolver.WORD2VEC_CACHE:
            logger.debug("IGNORED: repeated type")
            ret['ignored'] = True
            return ret

    possible_expansions = resolver.cached_resolve(acronym, left_context, right_context, strategy)

    if possible_expansions:
        logger.debug("FOUND: %s", possible_expansions)
        ret['found'] = True
    else:
        logger.debug("NOT FOUND")

    ret['correct'] = test_input(true_expansions, possible_expansions)

    splitted_row = splitted_row + [str(ret['found']), str(ret['correct'])] + possible_expansions
    ret['row'] = "\t".join(splitted_row) + "\n"

    return ret


def analyze_file(filename: str, strategy: resolver.Strategy, level: resolver.Level) -> Tuple[
    float, float]:
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

    input_file = open(filename, "r", encoding="utf-8")
    output_file = open(filename + "-analysis.tsv", "w+", encoding="utf-8")

    for input_row in input_file:
        total_acronyms += 1
        row_analysis = analyze_row(input_row, strategy, level)
        if row_analysis['found']:
            total_found += 1

        if row_analysis['correct']:
            total_correct += 1

        if not row_analysis['ignored']:
            valid_acronyms += 1

        output_file.write(row_analysis['row'])

        # Peeking into results
        # if logger.getEffectiveLevel() == logging.DEBUG:
        #     precision = _calculate_precision(total_correct, total_found)
        #     recall = _calculate_recall(total_correct, valid_acronyms)
        #     f1 = calculate_f1(precision, recall)
        #     logger.debug("P = %f, R = %f, F1 = %f", precision, recall, f1)

    input_file.close()
    output_file.close()

    invalid_absolute = total_acronyms - valid_acronyms
    logger.info("Total: %s", total_acronyms)
    logger.info("Ignored: %d", invalid_absolute)
    logger.info("Valid: %d", valid_acronyms)
    logger.info("Found: %d", total_found)
    logger.info("Correct: %d", total_correct)

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


def do_analysis(filename: str, strategy: resolver.Strategy, level: resolver.Level) -> None:
    """
    Analyzes a given reference standard.

    :param level:
    :param filename:
    :param strategy:
    :return:
    """
    if strategy == resolver.Strategy.NGRAM and level == resolver.Level.TYPE:
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
    do_analysis("resources/gold_standard.tsv", resolver.Strategy.WORD2VEC, resolver.Level.TYPE)
