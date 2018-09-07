"""
Gets token ngram statistics from a website
Does some cleaning and then returns ngram list
in decreasing frequency
"""
import logging
import time
import random
from typing import List, Tuple

import html2text

from acres.util import functions

logger = logging.getLogger(__name__)


def get_web_corpus(query: str) -> str:
    """
    Manually queries Bing for a given query to obtain a web corpus from the first return page.

    Should be used carefully, with delay.

    :param query:
    :return:
    """
    query = query.replace("  ", " ")

    # Escape HTML
    query = query.replace(" ", "+")
    query = query.replace("\"", "%22")

    time.sleep(random.randint(0, 2000) / 1000)
    return get_url_corpus("http://www.bing.de/search?cc=de&q=" + query)


def get_url_corpus(url: str) -> str:
    """
    Generates a pseudo-corpus out of a given URL.

    :param url:
    :return:
    """
    logger.info("Sending HTTP request to %s...", url)
    response = functions.get_url(url)
    if not response:
        logger.warning("Got empty response from %s.", url)
        return ""

    response_text = response.text
    #logger.debug(response_text)
    #
    # html2text removes diacritics, therefore substitutions!
    #
    response_text = response_text.replace("&#196;", "Ä").replace("&#228;", "ä") \
        .replace("&#214;", "Ö").replace("&#246;", "ö").replace("&#223;", "ß") \
        .replace("&#220;", "Ü").replace("&#252;", "ü").replace("&quot;", 'QUOTQUOT')
    txt = html2text.html2text(response_text)
    #
    # segmentation of text into smaller chunks; thus obtaining
    # more concise ngram lists
    # also detaching parentheses and quotes from enclosed text
    #
    txt = txt.replace("\n", " ").replace("*", "\n").replace('"', ' " ').replace('QUOTQUOT', ' " ')\
        .replace("[", "\n").replace("]", "\n").replace(")", " ) ").replace("!", "\n")\
        .replace("(", " ( ").replace(", ", " , ").replace(". ", "\n").replace("#", "\n")\
        .replace(";", "\n").replace("?", "\n").replace(": ", "\n").replace("|", "\n")\
        .replace("..", "\n").replace("   ", " ").replace("  ", " ").replace("  ", " ")\
        .replace("  ", " ").replace(" ( ) ", " ")
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
    return out


def ngrams_url_dump(url: str, min_num_tokens: int, max_num_tokens: int) -> List[Tuple[int, str]]:
    """
    Produces n-gram statistics from a given URL.

    If querying Bing, prefer ngrams_web_dump, which uses the Bing API if available.

    :param url:
    :param min_num_tokens:
    :param max_num_tokens:
    :return:
    """
    corpus = get_url_corpus(url)
    return functions.corpus_to_ngram_list(corpus, min_num_tokens, max_num_tokens)


# if logger.getEffectiveLevel() == logging.DEBUG:
#     ACRO = "AV"
#     QUERY = "AV Blocks"
#     import pickle
#     from acres import functions
#     from acres import resource_factory
#
#     MORPHEMES = resource_factory.get_morphemes()
#     # p = ngrams_url_dump("https://www.google.at/search?q=EKG+Herz", 1, 10)
#     # p = ngrams_url_dump("http://www.bing.de/search?cc=de&q=ekg+Herz", 1, 10)
#     p = ngrams_url_dump('http://www.bing.de/search?cc=de&q="' + QUERY + '"', 1, 10)
#     # p = ngrams_url_dump('http://www.bing.de/search?cc=de&q=' + q , 1, 10)
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
