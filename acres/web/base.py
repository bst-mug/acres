"""
Base module for web-based acronym resolution.
"""

import logging
from typing import List, Tuple

from acres import rater
from acres.util import functions
from acres.util import text
from acres.web import azure, bing

logger = logging.getLogger(__name__)

# Enables logging for under the hood libraries
logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

NEWLINE = "¶"
NUMERIC = "Ð"


def get_best_acronym_web_resolution(left: str, acro: str, right: str, minimum_len: int,
                                    maximum_word_count: int) -> Tuple[str, float]:
    """
    This is the main file to be used to leverage Bing search for resolving acronyms

    :param left: left context of acronym to be expanded (any length)
    :param acro: acronym to be expanded
    :param right: right context of acronym to be expanded (any length)
    :param minimum_len: the minimum length of the context words to be considered (e.g. to exclude \
    short articles etc.)
    :param maximum_word_count: the maximum of context words that are put into the query
    :return: best expansion of acronym, rating
    """
    ngrams = get_web_dump_from_acro_with_context(left, acro, right, minimum_len, maximum_word_count)

    old_weight = 0.0
    weight = 0.0
    out = ""

    for (freq, ngram) in ngrams:
        score = rater.get_acronym_score(acro, ngram, language="de")
        if score > 0.0:
            logger.debug("%.2f %s", score, ngram)
            weight = freq * score
            if weight > old_weight:
                out = ngram
                old_weight = weight

    return out, weight


def get_web_dump_from_acro_with_context(left: str, acro: str, right: str, min_word_len: int,
                                        n_context: int, digit_placehoder: str = "Ð",
                                        newline_placeholder: str = "¶",
                                        max_tokens_in_ngram: int = 8) -> List[Tuple[int,str]]:
    """
    This routine throws acronyms with left and right context (like in Excel table) to Bing and
    generates an n-gram statistic

    :param acro: acronym
    :param left: left context
    :param right: right context
    :param: min_word_len: minimal length of a context word
    :return: token ngram list with possible acronym expansion
    """

    cleaned_left_context = []
    cleaned_right_context = []
    proper_context = []
    # reduce right and left context to words of minimal length min_word_len
    # writing into the same tuple, alternating
    left = text.replace_punctuation(left)
    right = text.replace_punctuation(right)
    left_context = left.split(" ")
    # left_context = left_context.reverse()
    right_context = right.split(" ")
    for word in reversed(left_context):
        if len(word) >= min_word_len:
            if not (digit_placehoder in word or newline_placeholder in word):
                cleaned_left_context.append(word)
    for word in right_context:
        if len(word) >= min_word_len:
            if not (digit_placehoder in word or newline_placeholder in word):
                cleaned_right_context.append(word)
    i = 0
    while True:
        if i < len(cleaned_left_context):
            proper_context.append(cleaned_left_context[i])
        if i < len(cleaned_right_context):
            proper_context.append(cleaned_right_context[i])
        i = i + 1
        if i >= len(cleaned_left_context) and i >= len(cleaned_right_context):
            break
    # now we have a list with the context words starting with the ones closest to the acronym
    # in Bing the order of tokens in a query matters. Therefore the query must start with the
    # acronym
    query_tokens = [acro] + proper_context[:n_context]
    query = " ".join(query_tokens)
    return ngrams_web_dump(query, 1, max_tokens_in_ngram)


def ngrams_web_dump(query: str, min_num_tokens: int, max_num_tokens: int) -> List[Tuple[int,str]]:
    """

    :param query:
    :param min_num_tokens:
    :param max_num_tokens:
    :return:
    """
    if azure.is_valid_key():
        corpus = azure.get_web_corpus(query)
    else:
        corpus = bing.get_web_corpus(query)
    return functions.corpus_to_ngram_list(corpus, min_num_tokens, max_num_tokens)
