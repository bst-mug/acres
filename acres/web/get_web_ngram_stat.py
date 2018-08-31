"""

Gets token ngram statistics from a website
Does some cleaning and then returns ngram list
in decreasing frequency

"""

import logging
from typing import List, Tuple

import html2text

from acres import rater
from acres.util import functions
from acres.util import text

logger = logging.getLogger(__name__)

# Enables logging for under the hood libraries
logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

NEWLINE = "¶"
NUMERIC = "Ð"


def get_best_acronym_web_resolution(left: str, acro: str, right: str, minimum_len,
                                    maximum_word_count):
    """
    This is the main file to be used to leverage Bing search for resolving acronyms

    :param left: left context of acronym to be expanded (any length)
    :param acro: acronym to be expanded
    :param right: right context of acronym to be expanded (any length)
    :param minimum_len: the minimum length of the context words to be considered (e.g. to exclude
    short articles etc.)
    :param maximum_word_count: the maximum of context words that are put into the query
    :return: best expansion of acronym, rating
    """
    ngrams = get_web_dump_from_acro_with_context(
        left, acro, right, minimum_len, maximum_word_count)
    old_weight = 0
    out = ""
    for (freq, ngram) in ngrams:
        (full, score, reason) = rater.get_acronym_score(acro, ngram, language="de")
        if score > 0.0:
            print(score, full)
        if score > 0:
            weight = freq * score
            if weight > old_weight:
                out = full
            old_weight = weight
    return (out, weight)


def get_web_dump_from_acro_with_context(left, acro, right, min_word_len, n_context, digit_placehoder="Ð",
                                        newline_placeholder="¶", max_tokens_in_ngram=8):
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
    query = acro + " " + " ".join(proper_context[:n_context])
    return ngrams_web_dump("http://www.bing.de/search?cc=de&q=" + query, 1,
                                              max_tokens_in_ngram)


def ngrams_web_dump(url, min_num_tokens, max_num_tokens) -> List[Tuple[int,str]]:
    """
    Produces an n gram statistics from a Web Query, parsing the first return page
    Upper bound of ngram length may be set according to acronym length
    Rule of thumb: acronym length + 4, in order to safely retrieve acronym / definition
    pairs. Not that also quotes, dashes and parentheses count as single tokens


    Should be used carefully, with delay.

    :param url:
    :param min_num_tokens:
    :param max_num_tokens:
    :return:
    """

    logger.info("Sending HTTP request to %s...", url)
    response = functions.get_url(url)
    rt = response.text
    #logger.debug(rt)
    #
    # html2text removes diacritics, therefore substitutions!
    #
    rt = rt.replace("&#196;", "Ä").replace("&#228;", "ä") \
        .replace("&#214;", "Ö").replace("&#246;", "ö").replace("&#223;", "ß") \
        .replace("&#220;", "Ü").replace("&#252;", "ü").replace("&quot;", 'QUOTQUOT')
    out_l = []
    txt = html2text.html2text(rt)
    #
    # segmentation of text into smaller chunks; thus obtaining
    # more concise ngram lists
    # also detaching parentheses and quotes from enclosed text
    #
    txt = txt.replace("\n", " ").replace("*", "\n").replace('"', ' " ').replace('QUOTQUOT', ' " ').replace("[", "\n") \
        .replace("]", "\n").replace(")", " ) ").replace("!", "\n").replace("(", " ( ") \
        .replace(", ", " , ").replace(". ", "\n").replace("#", "\n").replace(";", "\n") \
        .replace("?", "\n").replace(": ", "\n").replace("|", "\n").replace("..", "\n") \
        .replace("   ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace(" ( ) ", " ")
    out = ""
    # logger.debug(txt)
    words = txt.split(" ")
    for word in words:
        word = word.strip()
        if len(word) < 50:
            if not ('\\' in word or '/' in word or '=' in word
                    or "www." in word or "%" in word):
                out = out + " " + word
    #logger.debug(out)

    output = functions.create_ngram_statistics(out, min_num_tokens, max_num_tokens)
    for ngram in output:
        out_l.append((output[ngram], ngram))
    out_l.sort(reverse=True)

    return out_l

# if logger.getEffectiveLevel() == logging.DEBUG:
#     ACRO = "AV"
#     QUERY = "AV Blocks"
#     import pickle
#     from acres import functions
#     from acres import resource_factory
#
#     MORPHEMES = resource_factory.get_morphemes()
#     # p = ngrams_web_dump("https://www.google.at/search?q=EKG+Herz", 1, 10)
#     # p = ngrams_web_dump("http://www.bing.de/search?cc=de&q=ekg+Herz", 1, 10)
#     p = ngrams_web_dump('http://www.bing.de/search?cc=de&q="' + QUERY + '"', 1, 10)
#     # p = ngrams_web_dump('http://www.bing.de/search?cc=de&q=' + q , 1, 10)
#     # f = open("c:\\Users\\schulz\\Nextcloud\\Terminology\\Corpora\\staging\\out.txt", 'wt')
#     # f.write("\n".join(p))
#     # f.close()
#     # logger.debug(p)
#
#     for line in p:
#         full = line.split("\t")[1]
#         cnt = line.split("\t")[0]
#         s = rate_acronym_resolutions.get_acronym_score(ACRO, full, MORPHEMES)
#         if s > 0.01:
#             logger.debug(str(s * int(cnt)) + "\t" + line)
