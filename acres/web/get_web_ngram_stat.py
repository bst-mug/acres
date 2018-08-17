"""

Gets token ngram statistics from a website
Does some cleaning and then returns ngram list
in decreasing frequency

"""

import logging
from typing import List, Tuple

import html2text

from acres.util import functions

logger = logging.getLogger(__name__)

# Enables logging for under the hood libraries
logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

NEWLINE = "¶"
NUMERIC = "Ð"


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
        .replace("   ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ")
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
        if len(ngram) > 10 and not "( )" in ngram:
            if ngram[0].isalpha():
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
