# Stefan Schulz 03 Dec 2017

import math
import pickle
import random
import re
import time
import logging

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
    acronymNgrams = pickle.load(open("pickle//acronymNgrams.p", "rb"))  # ngrams that contain at least one acronym
    morphemes = pickle.load(open("pickle//morphemes.p", "rb"))

    dia = functions.diacritics()  # list of diacritic characters
    dLogCorpus = {}  # dictionary from which the logfile is generated
    dLogWeb = {}  # dictionary from which the logfile is generated

    logger.debug("Dumps loaded")

    # "Logs" are files with short form expansions
    # logCorpus: expansions based on ngram model
    # logWebs: expansions from Web mining
    lfCorpus = open("log//logCorpus.txt", "w", encoding="UTF-8")
    lfWeb = open("log//logWebs.txt", "w", encoding="UTF-8")
    count = 0
    for ngram in acronymNgrams:  # language model, filtered by ngrams containing acronyms
        count = count + 1
        if count % 1000 == 0: time.sleep(10)
        if not ngram.isupper() and not NEWLINE in ngram and count % div == 0:  # and ngram.count(" ") < 3:
            # ngrams with newlines substitutes ("¶") seemed to be useless for this purpose

            logger.debug("-----------------------")
            logger.debug(ngram)
            splits = functions.split_gram(ngram.strip())
            for s in splits:
                leftString = s[0].strip()
                acronym = s[1].strip()
                rightString = s[2].strip()
                # Parms: minWinSize, minfreq, maxcount, minNumberTokens, maxNumberTokens
                # Set Parameters

                if len(acronym) == 2:
                    minWinSize = 7 + len(leftString) + len(rightString)
                    minfreq = 2
                    maxcount = 50
                    minNumberTokens = 1  # + ngram.count(" ")
                    maxNumberTokens = 4 + ngram.count(" ")
                else:
                    minWinSize = 10 + len(leftString) + len(rightString)
                    minfreq = 2
                    maxcount = 50
                    minNumberTokens = 2  # + ngram.count(" ")
                    maxNumberTokens = 4 + ngram.count(" ")

                # prepare parameters for Web model
                if NUMERIC in ngram:
                    liWeb = []
                else:
                    s = leftString + " " + acronym + " " + rightString
                    s = s.replace(".", " ").replace(",", " ")
                    s = s.replace("  ", " ")
                    s = s.replace(" ", "+")
                    strURL = "http://www.bing.de/search?cc=de&q=%22" + s + "%22"
                    time.sleep(random.randint(0, 2000) / 1000)
                    logger.info(".")
                    liWeb = get_acronyms_from_web.ngramsWebDump(strURL, 1, 10)

                # Prepare parameters for corpus model
                if leftString == "": leftString = "*"
                if rightString == "": rightString = "*"
                liCorpus = get_synonyms_from_ngrams.findEmbeddings(leftString, acronym, rightString, ngramstat, index,
                                                                   minWinSize, minfreq, maxcount, minNumberTokens,
                                                                   maxNumberTokens, False)

                for item in liCorpus:
                    oldExp = ""
                    exp = item.split("\t")[1]  # Ngram expression
                    f = int(item.split("\t")[0])  # Frequency
                    if re.search("^[\ \-A-Za-z0-9" + dia + "]*$", exp) != None and acronym.lower() != exp.lower()[0:len(
                            acronym.lower())]:
                        if exp != oldExp:
                            scoreCorpus = 0
                            scoreCorpus = rate_acronym_resolutions.GetAcronymScore(acronym, exp, morphemes)
                            if scoreCorpus > 0:
                                result = str(round(scoreCorpus * math.log10(f), 2)) + " " + exp + " " + str(
                                    round(scoreCorpus, 2)) + " " + str(f) + " " + "\t" + ngram
                                if not acronym in dLogCorpus:
                                    dLogCorpus[acronym] = [result]
                                else:
                                    dLogCorpus[acronym].append(result)
                            oldExp = exp

                for item in liWeb:
                    oldExp = ""
                    exp = item.split("\t")[1]  # Ngram expression
                    f = int(item.split("\t")[0])  # Frequency
                    if re.search("^[\ \-A-Za-z0-9" + dia + "]*$", exp) != None and acronym.lower() != exp.lower()[0:len(
                            acronym.lower())]:
                        if exp != oldExp:
                            scoreWeb = 0
                            scoreWeb = rate_acronym_resolutions.GetAcronymScore(acronym, exp, morphemes)
                            if scoreWeb > 0:
                                result = str(round(scoreWeb * math.log10(f), 2)) + " " + exp + " " + str(
                                    round(scoreWeb, 2)) + " " + str(f) + " " + "\t" + ngram
                                if not acronym in dLogWeb:
                                    dLogWeb[acronym] = [result]
                                else:
                                    dLogWeb[acronym].append(result)
                            oldExp = exp

    for a in dLogCorpus:
        for r in dLogCorpus[a]:
            lfCorpus.write(a.rjust(8) + "\t" + r + "\n")

    for a in dLogWeb:
        for r in dLogWeb[a]:
            lfWeb.write(a.rjust(8) + "\t" + r + "\n")

    lfCorpus.close()
    lfWeb.close()
