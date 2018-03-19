# Stefan Schulz 03 Dec 2017

import logging
import math
import random
import re
import time

from acres import functions
from acres import get_synonyms_from_ngrams
from acres import get_web_ngram_stat
from acres import rate_acronym_resolutions
from acres import resource_factory

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG) # Uncomment this to get debug messages

NEWLINE = "¶"
NUMERIC = "Ð"
VERBOSE = False
DIV = 1  # for sampling, if no sampling DIV = 1. Sampling is used for testing


def find_synonyms():
    """
    Finds synonyms using a n-gram frequency list from related corpus.
    TODO: reformatting logfile and filter criteria

    :return:
    """

    # ngrams that contain at least one acronym
    acronym_ngrams = resource_factory.get_acronym_ngrams()

    d_log_corpus = {}  # dictionary from which the logfile is generated
    d_log_web = {}  # dictionary from which the logfile is generated

    logger.debug("Dumps loaded")

    count = 0
    for ngram in acronym_ngrams:  # language model, filtered by ngrams containing acronyms
        count = count + 1
        if count % 1000 == 0:
            time.sleep(10)
        # and ngram.count(" ") < 3:
        if not ngram.isupper() and NEWLINE not in ngram and count % DIV == 0:
            # ngrams with newlines substitutes ("¶") seemed to be useless for
            # this purpose

            logger.debug("-----------------------")
            logger.debug(ngram)
            splits = functions.split_ngram(ngram.strip())
            for s in splits:
                left_string = s[0].strip()
                acronym = s[1].strip()
                right_string = s[2].strip()
                # Parms: min_win_size, minfreq, maxcount, min_number_tokens, max_number_tokens
                # Set Parameters

                if len(acronym) == 2:
                    min_win_size = 7 + len(left_string) + len(right_string)
                    minfreq = 2
                    maxcount = 50
                    min_number_tokens = 1  # + ngram.count(" ")
                    max_number_tokens = 4 + ngram.count(" ")
                else:
                    min_win_size = 10 + len(left_string) + len(right_string)
                    minfreq = 2
                    maxcount = 50
                    min_number_tokens = 2  # + ngram.count(" ")
                    max_number_tokens = 4 + ngram.count(" ")

                # prepare parameters for Web model
                if NUMERIC in ngram:
                    li_web = []
                else:
                    s = left_string + " " + acronym + " " + right_string
                    s = s.replace(".", " ").replace(",", " ")
                    s = s.replace("  ", " ")
                    s = s.replace(" ", "+")
                    str_url = "http://www.bing.de/search?cc=de&q=%22" + s + "%22"
                    time.sleep(random.randint(0, 2000) / 1000)
                    logger.info(".")
                    li_web = get_web_ngram_stat.ngrams_web_dump(str_url, 1, 10)

                # Prepare parameters for corpus model
                if left_string == "":
                    left_string = "*"
                if right_string == "":
                    right_string = "*"
                li_corpus = get_synonyms_from_ngrams.find_embeddings(left_string, acronym, right_string, min_win_size,
                                                                     minfreq, maxcount, min_number_tokens,
                                                                     max_number_tokens)

                process_corpus(li_corpus, acronym, ngram, d_log_corpus)
                process_corpus(li_web, acronym, ngram, d_log_web)

    # "Logs" are files with short form expansions
    # logCorpus: expansions based on ngram model
    # logWebs: expansions from Web mining
    write_log(d_log_corpus, resource_factory.get_log_corpus_filename())
    write_log(d_log_web, resource_factory.get_log_web_filename())


def process_corpus(corpus, acronym, ngram, log):
    """

    :param corpus:
    :param acronym:
    :param ngram:
    :param log:
    :return:
    """
    morphemes = resource_factory.get_morphemes()
    dia = functions.diacritics()  # list of diacritic characters

    for item in corpus:
        old_exp = ""
        exp = item.split("\t")[1]  # Ngram expression
        f = int(item.split("\t")[0])  # Frequency

        first_condition = re.search("^[\s\-A-Za-z0-9" + dia + "]*$", exp) is not None
        second_condition = acronym.lower() != exp.lower()[0:len(acronym.lower())]
        if first_condition and second_condition:
            if exp != old_exp:
                # score_corpus = 0
                score_corpus = rate_acronym_resolutions.get_acronym_score(
                    acronym, exp, morphemes)
                if score_corpus > 0:
                    a = str(round(score_corpus * math.log10(f), 2))
                    b = str(round(score_corpus, 2))
                    result = a + " " + exp + " " + b + " " + str(f) + " " + "\t" + ngram
                    if acronym not in log:
                        log[acronym] = [result]
                    else:
                        log[acronym].append(result)
                old_exp = exp


def write_log(log, filename):
    """
    Writes a log into a file described by the filename.

    :param log:
    :param filename:
    :return:
    """
    file = open(filename, "w", encoding="UTF-8")

    for a in log:
        for r in log[a]:
            file.write(a.rjust(8) + "\t" + r + "\n")

    file.close()
