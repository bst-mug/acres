# Stefan Schulz 03 Dec 2017

import logging
import math
import pickle
import random
import re
import time

from acres import functions
from acres import get_acronyms_from_web
from acres import get_synonyms_from_ngrams
from acres import rate_acronym_resolutions

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG) # Uncomment this to get debug messages

NEWLINE = "¶"
NUMERIC = "Ð"
VERBOSE = False
div = 1  # for sampling, if no sampling div = 1. Sampling is used for testing


def find_synonyms():
    """
    Finds synonyms using a n-gram frequency list from related corpus.

    :return:
    """
    # load data

    ngramstat = pickle.load(open("pickle//ngramstat.p", "rb"))
    index = pickle.load(open("pickle//index.p", "rb"))
    # ngrams that contain at least one acronym
    acronym_ngrams = pickle.load(open("pickle//acronymNgrams.p", "rb"))
    morphemes = pickle.load(open("pickle//morphemes.p", "rb"))

    dia = functions.diacritics()  # list of diacritic characters
    d_log_corpus = {}  # dictionary from which the logfile is generated
    d_log_web = {}  # dictionary from which the logfile is generated

    logger.debug("Dumps loaded")

    # "Logs" are files with short form expansions
    # logCorpus: expansions based on ngram model
    # logWebs: expansions from Web mining
    lf_corpus = open("log//logCorpus.txt", "w", encoding="UTF-8")
    lf_web = open("log//logWebs.txt", "w", encoding="UTF-8")
    count = 0
    for ngram in acronym_ngrams:  # language model, filtered by ngrams containing acronyms
        count = count + 1
        if count % 1000 == 0:
            time.sleep(10)
        # and ngram.count(" ") < 3:
        if not ngram.isupper() and NEWLINE not in ngram and count % div == 0:
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
                    li_web = get_acronyms_from_web.ngrams_web_dump(str_url, 1, 10)

                # Prepare parameters for corpus model
                if left_string == "":
                    left_string = "*"
                if right_string == "":
                    right_string = "*"
                li_corpus = get_synonyms_from_ngrams.find_embeddings(
                    left_string,
                    acronym,
                    right_string,
                    ngramstat,
                    index,
                    min_win_size,
                    minfreq,
                    maxcount,
                    min_number_tokens,
                    max_number_tokens)

                for item in li_corpus:
                    old_exp = ""
                    exp = item.split("\t")[1]  # Ngram expression
                    f = int(item.split("\t")[0])  # Frequency
                    if re.search(
                            "^[\ \-A-Za-z0-9" + dia + "]*$",
                            exp) is not None and acronym.lower() != exp.lower()[
                                                                    0:len(
                                                                        acronym.lower())]:
                        if exp != old_exp:
                            # score_corpus = 0
                            score_corpus = rate_acronym_resolutions.get_acronym_score(
                                acronym, exp, morphemes)
                            if score_corpus > 0:
                                result = str(
                                    round(
                                        score_corpus * math.log10(f),
                                        2)) + " " + exp + " " + str(
                                    round(
                                        score_corpus,
                                        2)) + " " + str(f) + " " + "\t" + ngram
                                if acronym not in d_log_corpus:
                                    d_log_corpus[acronym] = [result]
                                else:
                                    d_log_corpus[acronym].append(result)
                            old_exp = exp

                for item in li_web:
                    old_exp = ""
                    exp = item.split("\t")[1]  # Ngram expression
                    f = int(item.split("\t")[0])  # Frequency
                    if re.search(
                            "^[\ \-A-Za-z0-9" + dia + "]*$",
                            exp) is not None and acronym.lower() != exp.lower()[
                                                                    0:len(
                                                                        acronym.lower())]:
                        if exp != old_exp:
                            # score_web = 0
                            score_web = rate_acronym_resolutions.get_acronym_score(
                                acronym, exp, morphemes)
                            if score_web > 0:
                                a = str(round(score_web * math.log10(f), 2))
                                b = str(round(score_web, 2))
                                result = a + " " + exp + " " + b + " " + str(f) + " " + "\t" + ngram
                                if acronym not in d_log_web:
                                    d_log_web[acronym] = [result]
                                else:
                                    d_log_web[acronym].append(result)
                            old_exp = exp

    for a in d_log_corpus:
        for r in d_log_corpus[a]:
            lf_corpus.write(a.rjust(8) + "\t" + r + "\n")

    for a in d_log_web:
        for r in d_log_web[a]:
            lf_web.write(a.rjust(8) + "\t" + r + "\n")

    lf_corpus.close()
    lf_web.close()
