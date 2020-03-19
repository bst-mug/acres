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


def _valid(topics: List[Acronym], valid_standard: Set[str], level: Level) -> List[Acronym]:
    """

    :param topics:
    :param valid_standard:
    :param level:
    :return:
    """
    valid = []  # type: List[Acronym]
    types = set()  # type: Set[str]

    for contextualized_acronym in topics:
        acronym = contextualized_acronym.acronym

        # Ignore repeated types
        if level == Level.TYPE and acronym in types:
            # logger.debug("REPEATED {%s}: repeated type.", acronym)
            continue
        types.add(acronym)

        if acronym not in valid_standard:
            logger.debug("IGNORED {%s}: invalid acronym.", acronym)
            continue

        valid.append(contextualized_acronym)

    return valid


def evaluate(topics: List[Acronym], valid_standard: Set[str], standard: Dict[str, Dict[str, int]],
             strategy: resolver.Strategy, level: Level, max_tries: int,
             lenient: bool) -> Tuple[List[Acronym], List[Acronym], List[Acronym]]:
    """
    Analyzes a gold standard with text excerpts centered on an acronym, followed by n valid
    expansions.

    :param topics:
    :param valid_standard:
    :param standard:
    :param strategy:
    :param level:
    :param max_tries:
    :param lenient: Whether to consider partial matches (1) as a valid sense.
    :return: A tuple with lists containing correct, found, and valid contextualized acronyms
    """
    found = []   # type: List[Acronym]
    correct = []    # type: List[Acronym]

    acronym_senses = senses.map_senses_acronym(standard, lenient)

    valid = _valid(topics, valid_standard, level)

    for contextualized_acronym in valid:
        acronym = contextualized_acronym.acronym

        true_expansions = acronym_senses[acronym]
        row_analysis = analyze(contextualized_acronym, true_expansions, strategy, max_tries)

        if row_analysis['found']:
            found.append(contextualized_acronym)

        if row_analysis['correct']:
            correct.append(contextualized_acronym)

    invalid_absolute = len(topics) - len(valid)
    logger.info("Total: %s", len(topics))
    logger.info("Ignored: %d", invalid_absolute)
    logger.info("Valid: %d", len(valid))
    logger.info("Found: %d", len(found))
    logger.info("Correct: %d", len(correct))

    return correct, found, valid


def do_analysis(topics_file: str, detection_file: str, expansion_file: str,
                strategy: resolver.Strategy, level: Level,
                max_tries: int, lenient: bool) -> Tuple[List[Acronym], List[Acronym], List[Acronym]]:
    """
    Analyzes a given expansion standard

    :param topics_file:
    :param detection_file:
    :param expansion_file:
    :param strategy:
    :param level:
    :param max_tries:
    :param lenient:
    :return: A tuple with lists containing correct, found, and valid contextualized acronyms
    """
    topics = topic_list.parse(topics_file)
    valid_standard = detection_standard.parse_valid(detection_file)
    standard = expansion_standard.parse(expansion_file)

    start_time = time.time()
    (correct, found, valid) = evaluate(topics, valid_standard, standard, strategy, level, max_tries,
                                       lenient)
    end_time = time.time()

    print("Time: (s)", end_time - start_time)

    final_precision = metrics.calculate_precision(len(correct), len(found))
    final_recall = metrics.calculate_recall(len(correct), len(valid))
    final_f1 = metrics.calculate_f1(final_precision, final_recall)

    print("Strategy: ", strategy)
    print("Rank: ", max_tries)
    print("Lenient: ", lenient)
    print("Precision: ", final_precision)
    print("Recall: ", final_recall)
    print("F1: ", final_f1)
    return correct, found, valid


def plot_data(topics_file: str, detection_file: str, expansion_file: str):
    """
    Run all strategies using different ranks and lenient approaches and generate a TSV file to be \
    used as input for the plots.R script.

    :param topics_file:
    :param detection_file:
    :param expansion_file:
    :return:
    """
    output = open("stats.tsv", "w+", encoding="utf-8")
    output.write("k\tMajority\tSI\tfastType\tword2vec\n")
    for lenient in [True, False]:
        for rank in range(1, 21):
            output.write(str(rank) + "\t")
            for strategy in [resolver.Strategy.BASELINE, resolver.Strategy.DICTIONARY,
                             resolver.Strategy.FASTTYPE, resolver.Strategy.WORD2VEC]:
                correct, found, valid = do_analysis(topics_file, detection_file, expansion_file,
                                                    strategy, Level.TYPE, rank, lenient)
                precision = metrics.calculate_precision(len(correct), len(found))
                recall = metrics.calculate_recall(len(correct), len(valid))
                fone = metrics.calculate_f1(precision, recall)
                output.write(str(fone) + "\t")
            output.write("\n")
            output.flush()
    output.close()


def summary(topics_file: str, detection_file: str, expansion_file: str, level: Level,
            max_tries: int, lenient: bool):
    """
    Save a summary table in TSV format that can be used to run statistical tests (e.g. McNemar Test)

    :param topics_file:
    :param detection_file:
    :param expansion_file:
    :param level:
    :param max_tries:
    :param lenient:
    :return:
    """
    strategies = [resolver.Strategy.BASELINE, resolver.Strategy.DICTIONARY,
                  resolver.Strategy.FASTTYPE, resolver.Strategy.WORD2VEC]

    topics = topic_list.parse(topics_file)
    valid_standard = detection_standard.parse_valid(detection_file)
    valid = _valid(topics, valid_standard, level)

    # Most methods are optimized to run in alphabetic order by storing a large chunk in memory.
    # Therefore, it's more efficient to run first each method so that results can be transposed.
    results = {}    # type: Dict[resolver.Strategy, Set[Acronym]]
    for strategy in strategies:
        logger.info("Strategy: %s", strategy)
        correct, _, _ = do_analysis(topics_file, detection_file, expansion_file,strategy,
                                    level, max_tries, lenient)
        results[strategy] = set(correct)

    output = open("summary.tsv", "w+", encoding="utf-8")
    output.write("instance\tMajority\tSI\tfastType\tword2vec\n")

    for contextualized_acronym in valid:
        output.write(contextualized_acronym.acronym + "\t")
        assessments = []
        for strategy in strategies:
            assessment = "T" if contextualized_acronym in results[strategy] else "F"
            assessments.append(assessment)
        output.write("\t".join(assessments))
        output.write("\n")

    output.close()


if __name__ == "__main__":
    do_analysis("resources/topic_list.tsv",
                "resources/detection_standard.tsv",
                "resources/expansion_standard.tsv",
                resolver.Strategy.WORD2VEC, Level.TYPE, 1, True)
