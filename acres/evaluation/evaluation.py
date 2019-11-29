"""
Benchmark code.
"""

import logging
import time
from enum import Enum
from itertools import islice
from typing import Dict, Tuple, List, Set

import acres.util.acronym
from acres.evaluation import metrics
from acres.model import expansion_standard, detection_standard, topic_list
from acres.resolution import resolver
from acres.stats import senses
from acres.util import text
from acres.util.acronym import Acronym

logger = logging.getLogger(__name__)


class Level(Enum):
    """
    Enum that holds acronym-solving levels.
    """
    TOKEN = 1
    TYPE = 2


def test_input(true_expansions: Set[str], possible_expansions: List[str],
               max_tries: int = 10) -> bool:
    """
    Tests an acronym + context strings against the ngram model

    :param true_expansions:
    :param possible_expansions: An ordered list of possible expansions.
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


def analyze(contextualized_acronym: acres.util.acronym.Acronym, true_expansions: Set[str],
            strategy: resolver.Strategy, max_tries: int) -> Dict[str, bool]:
    """
    Analyze a given row of the gold standard.

    :param contextualized_acronym:
    :param true_expansions:
    :param strategy:
    :param max_tries:
    :return: A dictionary with keys {'found', 'correct', and 'ignored'} pointing to boolean.
    """
    ret = {'found': False, 'correct': False, 'ignored': False}

    # Normalize context so that we can match it to the training data
    left_context = text.clean(contextualized_acronym.left_context)
    acronym = contextualized_acronym.acronym
    right_context = text.clean(contextualized_acronym.right_context)

    # Normalize true expansions so that we can match them to the training data
    true_expansions = set(map(text.clean, true_expansions))

    # Remove context to improve cache hit
    # XXX We currently support context only for n-grams
    if strategy not in [resolver.Strategy.NGRAM, resolver.Strategy.FASTNGRAM]:
        left_context = ""
        right_context = ""

    logger.debug("%s [%s] %s => %s", left_context, acronym, right_context, true_expansions)

    fltered_expansions = resolver.filtered_resolve(acronym, left_context, right_context, strategy)
    possible_expansions = list(islice(fltered_expansions, max_tries))

    if possible_expansions:
        logger.debug("FOUND: %s => %s", acronym, possible_expansions)
        ret['found'] = True

    ret['correct'] = test_input(true_expansions, possible_expansions, max_tries)

    if not ret['found']:
        logger.debug("NOT FOUND: %s", acronym)
    elif not ret['correct']:
        logger.debug("INCORRECT: %s", acronym)

    return ret


def evaluate(topics: List[Acronym], valid: Set[str], standard: Dict[str, Dict[str, int]],
             strategy: resolver.Strategy, level: Level, max_tries: int,
             lenient: bool) -> Tuple[float, float]:
    """
    Analyzes a gold standard with text excerpts centered on an acronym, followed by n valid
    expansions.

    :param topics:
    :param valid:
    :param standard:
    :param strategy:
    :param level:
    :param max_tries:
    :param lenient: Whether to consider partial matches (1) as a valid sense.
    :return: A tuple with final_precision and final_recall
    """
    total_acronyms = valid_acronyms = total_correct = total_found = 0

    acronym_senses = senses.map_senses_acronym(standard, lenient)

    types = set()  # type: Set[str]
    for contextualized_acronym in topics:
        total_acronyms += 1
        acronym = contextualized_acronym.acronym

        # Ignore repeated types
        if level == Level.TYPE and acronym in types:
            # logger.debug("REPEATED {%s}: repeated type.", acronym)
            continue
        types.add(acronym)

        if acronym not in valid:
            logger.debug("IGNORED {%s}: invalid acronym.", acronym)
            continue

        valid_acronyms += 1

        true_expansions = acronym_senses[acronym]
        row_analysis = analyze(contextualized_acronym, true_expansions, strategy, max_tries)

        if row_analysis['found']:
            total_found += 1

        if row_analysis['correct']:
            total_correct += 1

    invalid_absolute = total_acronyms - valid_acronyms
    logger.info("Total: %s", total_acronyms)
    logger.info("Ignored: %d", invalid_absolute)
    logger.info("Valid: %d", valid_acronyms)
    logger.info("Found: %d", total_found)
    logger.info("Correct: %d", total_correct)

    precision = metrics.calculate_precision(total_correct, total_found)
    recall = metrics.calculate_recall(total_correct, valid_acronyms)

    return precision, recall


def do_analysis(topics_file: str, detection_file: str, expansion_file: str,
                strategy: resolver.Strategy, level: Level,
                max_tries: int, lenient: bool) -> Tuple[float, float]:
    """
    Analyzes a given expansion standard

    :param topics_file:
    :param detection_file:
    :param expansion_file:
    :param strategy:
    :param level:
    :param max_tries:
    :param lenient:
    :return:
    """
    topics = topic_list.parse(topics_file)
    valid = detection_standard.parse_valid(detection_file)
    standard = expansion_standard.parse(expansion_file)

    start_time = time.time()
    (final_precision, final_recall) = evaluate(topics, valid, standard, strategy, level, max_tries,
                                               lenient)
    end_time = time.time()

    print("Time: (s)", end_time - start_time)

    final_f1 = metrics.calculate_f1(final_precision, final_recall)
    print("Strategy: ", strategy)
    print("Rank: ", max_tries)
    print("Lenient: ", lenient)
    print("Precision: ", final_precision)
    print("Recall: ", final_recall)
    print("F1: ", final_f1)
    return final_precision, final_recall


if __name__ == "__main__":
    do_analysis("resources/topic_list.tsv",
                "resources/detection_standard.tsv",
                "resources/expansion_standard.tsv",
                resolver.Strategy.WORD2VEC, Level.TYPE, 10, True)
