"""
Stefan Schulz 03 Dec 2017
"""

import logging
import math
import random
import re
import time
from typing import Dict, List, Tuple

import acres.util.acronym
from acres import rater
from acres.ngram import finder
from acres.preprocess import resource_factory
from acres.util import text
from acres.web import bing

logger = logging.getLogger(__name__)

NEWLINE = "¶"
NUMERIC = "Ð"
VERBOSE = False
DIV = 1  # for sampling, if no sampling DIV = 1. Sampling is used for testing


def find_synonyms() -> None:
    """
    TODO: this routine was originally intended to process a large list of acronyms + contexts
    Finds synonyms using a n-gram frequency list from related corpus.
    TODO: reformatting logfile and filter criteria

    :return:
    """

    # ngrams that contain at least one acronym
    acronym_ngrams = resource_factory.get_acronym_ngrams()

    # dictionary from which the logfile is generated
    d_log_corpus = {}  # type: Dict[str, List[str]]

    # dictionary from which the logfile is generated
    d_log_web = {}  # type: Dict[str, List[str]]

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
            splits = acres.util.acronym.split_ngram(ngram.strip())
            for split in splits:
                left_string = split[0].strip()
                acronym = split[1].strip()
                right_string = split[2].strip()
                # Parms: min_win_size, minfreq, maxcount, min_number_tokens, max_number_tokens
                # Set Parameters

                if len(acronym) == 2:
                    constraints = finder.FinderConstraints(min_freq=2, max_count=50,
                                                           min_num_tokens=1,
                                                           max_num_tokens=4 + ngram.count(" "))
                else:
                    constraints = finder.FinderConstraints(min_freq=2, max_count=50,
                                                           min_num_tokens=2,
                                                           max_num_tokens=4 + ngram.count(" "))

                # prepare parameters for Web model
                if NUMERIC in ngram:
                    li_web = []  # type: List[Tuple[int, str]]
                else:
                    query = left_string + " " + acronym + " " + right_string
                    query = query.replace(".", " ").replace(",", " ")
                    query = query.replace("  ", " ")
                    query = query.replace(" ", "+")
                    str_url = "http://www.bing.de/search?cc=de&q=%22" + query + "%22"
                    time.sleep(random.randint(0, 2000) / 1000)
                    print(str_url)
                    li_web = bing.ngrams_web_dump(str_url, 1, 10)

                # Prepare parameters for corpus model
                if left_string == "":
                    left_string = "*"
                if right_string == "":
                    right_string = "*"
                li_corpus = finder.find_embeddings(left_string, acronym, right_string, constraints)

                _process_corpus(li_corpus, acronym, ngram, d_log_corpus)
                _process_corpus(li_web, acronym, ngram, d_log_web)

    # "Logs" are files with short form expansions
    # logCorpus: expansions based on ngram model
    # logWebs: expansions from Web mining
    _write_log(d_log_corpus, resource_factory.get_log_corpus_filename())
    _write_log(d_log_web, resource_factory.get_log_web_filename())


def _process_corpus(corpus: List[Tuple[int, str]], acronym: str, ngram: str,
                    log: Dict[str, List[str]]) -> None:
    """

    :param corpus:
    :param acronym:
    :param ngram:
    :param log:
    :return:
    """
    # morphemes = resource_factory.get_morphemes()
    # TODO: as morphemes are not a public resource, maybe ignore them at least in our experiments
    dia = text.diacritics()  # list of diacritic characters

    for item in corpus:
        old_exp = ""
        (freq, exp) = item  # Frequency, Ngram expression

        first_condition = re.search(r"^[\s\-A-Za-z0-9" + dia + "]*$", exp) is not None
        second_condition = acronym.lower() != exp.lower()[0:len(acronym.lower())]
        if first_condition and second_condition:
            if exp != old_exp:
                # score_corpus = 0
                score_corpus = rater.get_acronym_score(acronym, exp)[1]
                if score_corpus > 0:
                    a = str(round(score_corpus * math.log10(freq), 2))
                    b = str(round(score_corpus, 2))
                    result = a + " " + exp + " " + b + " " + str(freq) + " " + "\t" + ngram
                    if acronym not in log:
                        log[acronym] = [result]
                    else:
                        log[acronym].append(result)
                old_exp = exp


def _write_log(log: Dict[str, List[str]], filename: str) -> None:
    """
    Writes a log into a file described by the filename.

    :param log:
    :param filename:
    :return:
    """
    file = open(filename, "w", encoding="UTF-8")

    for acronym in log:
        for result in log[acronym]:
            file.write(acronym.rjust(8) + "\t" + result + "\n")

    file.close()
