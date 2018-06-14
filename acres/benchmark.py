"""
Benchmark code.
"""

import logging
from logging.config import fileConfig

from acres import get_synonyms_from_ngrams

logging.config.fileConfig("logging.ini")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def build_search_ngrams(context, reverse=False):
    """
    Builds a context tuple containing 1 to n-grams

    :param context: A string with the context
    :param reverse: Takes the context in reverse (e.g. left context)
    :return: A tuple with 1 to n-gram
    """
    # TODO tentative
    unigram = bigram = trigram = "<SEL>"
    if context != "":
        tokens = context.split(" ")
        tokens = tokens[::-1] if reverse else tokens
        unigram = " ".join(tokens[:1])
        bigram = " ".join(tokens[:2])
        trigram = " ".join(tokens[:3])
    return unigram, bigram, trigram


def test_input(l_probe, lstExp):
    """
    Tests an acronym + context strings against the ngram model

    :param l_probe:
    :param lstExp:
    :return:
    """
    for term in lstExp:
        logger.info(term)
        for probe in l_probe:
            if term.split("\t")[1].lower() == probe.lower():
                logger.info("FOUND: " + term)
                return True
    return False


def analyze_row(input_row):
    """
    Analyze a given row of the gold standard.

    :param input_row:
    :return:
    """
    if input_row == "":
        return

    row = input_row.strip("\n")
    logger.info("=======================")
    logger.info("Analyzing: " + row)
    logger.info("=======================")

    splitted_row = row.split("\t")

    left_context = splitted_row[0]
    acronym = splitted_row[1]
    right_context = splitted_row[2]
    true_expansions = splitted_row[3:]

    (left_unigram, left_bigram, left_trigram) = build_search_ngrams(left_context, True)
    (right_unigram, right_bigram, right_trigram) = build_search_ngrams(right_context)

    # Order is important for the quality of the retrieved expansion
    patterns = [(left_trigram, right_trigram),  # trigrams
                (left_bigram, right_trigram), (left_trigram, right_bigram),  # bigram + trigram
                (left_bigram, right_bigram),  # bigrams
                (left_unigram, right_bigram), (left_bigram, right_unigram),  # bigram + unigram
                (left_unigram, right_unigram),  # unigrams
                (left_bigram, "<SEL>"), (left_unigram, "<SEL>"),  # bigram/unigram + <SEL>
                ("<SEL>", right_bigram), ("<SEL>", right_unigram),  # <SEL> + bigram/unigram
                ("<SEL>", "<SEL>"),  # <SEL> + <SEL>
                ("<SEL>", "<VOID>"), ("<VOID>", "<SEL>")  # <SEL> + <VOID>
                ]

    previous_left_pattern = previous_right_pattern = ""
    for pattern in patterns:
        left_pattern = pattern[0]
        right_pattern = pattern[1]

        # Quick optimization: don't search for patterns that happens to be the same as last one
        if left_pattern != previous_left_pattern or right_pattern != previous_right_pattern:
            lstExp = get_synonyms_from_ngrams.find_embeddings(left_pattern, acronym, right_pattern, 1, 1, 500, 2, 10)
            ngram_found = test_input(true_expansions, lstExp)
            print(pattern)
            if ngram_found:
                return True

            previous_left_pattern = left_pattern
            previous_right_pattern = right_pattern

    return False


def analyze_file(file):
    """
    Analyzes a gold standard with text excerpts centered on an acronym, followed by n valid
    expansions.

    :param file: A tab-separated file that contains the records from the gold standard. Syntax:
    left context<TAB>acronym<TAB>right context<TAB>valid expansion 1<TAB>valid expansion 2<TAB>...
    :return: A tuple with precision and recall
    """
    total_acronyms = total_correct = total_found = 0
    # FIXME calculate total_found

    f = open(file, "r", encoding="utf-8")

    for row in f:
        total_acronyms += 1
        found = analyze_row(row)
        if found:
            total_correct += 1
            print("FOUND")

    f.close()

    precision = total_correct / total_found if total_found != 0 else 0
    recall = total_correct / total_acronyms if total_acronyms != 0 else 0

    return precision, recall


def calculate_f1(precision, recall):
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
