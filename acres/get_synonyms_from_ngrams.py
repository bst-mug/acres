# Stefan Schulz 21 August 2017
"""
Finds synonyms using a n-gram frequency list from related corpus
"""

import pickle
import re
import logging

from acres import functions

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG) # Uncomment this to get debug messages


def findEmbeddings(strLeft,
                   strMiddle,
                   strRight,
                   ngramstat,
                   index,
                   minWinSize,
                   minfreq,
                   maxcount,
                   minNumTokens,
                   maxNumTokens,
                   verbose):
    """
    Input strMiddle, together with a series of filter parameters
    Three cases of embeddings: 1. bilateral, 2.left, 3.right

    :param strLeft: string left of unknown ("*" if to be retrieved ; "" if empty")
    :param strMiddle: input nonlex form (with or without context words) for which synonym is sought
    :param strRight: string right uf unknown ("*" if to be retrieved ; "" if empty")
    :param ngramstat: ngram model
    :param index: word index to ngram model
    :param minWinSize: minimum window size
    :param minfreq: minimum ngram frequency
    :param maxcount: maximum count in list
    :param minNumTokens:
    :param maxNumTokens:
    :param verbose:
    :return:
    """
    if verbose:
        logger.setLevel(logging.DEBUG)

    MAXLIST = 100
    DIGIT = "Ð"
    outL = []
    allBeds = []
    allSets = []
    selRows = []
    count = 0

    # Construction of regular expression
    #                       Left             Middle              Right
    # Empty	            "^"                                   "$"
    # Specified ("abc")	    "^abc\ "	      "abc"            "\ abc$"
    # Arbitrary, nonempty   "^.*\ "                            "\ .*$"
    # Build regular expression for matching ngram  

    if strLeft == "*":
        strLeftEsc = "^.*\ "
    elif strLeft == "":
        strLeftEsc = "^"
    else:
        strLeftEsc = "^" + re.escape(strLeft.strip()) + "\ "
    strMiddleEsc = re.escape(strMiddle.strip())
    if strRight == "*":
        strRightEsc = "\ .*$"
    elif strRight == "":
        strRightEsc = "$"
    else:
        strRightEsc = "\ " + re.escape(strRight.strip()) + "$"
    regexEmbed = strLeftEsc + strMiddleEsc + strRightEsc

    logger.debug('Unknown expression: "' + strMiddleEsc + '"')
    logger.debug('Left context: "' + strLeftEsc + '"')
    logger.debug('Right context: "' + strRightEsc + '"')
    logger.debug("Minimum n-gram frequency " + str(minfreq))
    logger.debug("Maximum count of iterations " + str(maxcount))
    logger.debug("N-gram cardinality between " + str(minNumTokens) + " and " + str(maxNumTokens))
    logger.debug("Regular expression: " + regexEmbed)

    logger.debug("press key!")

    # set of selected ngrams for filtering 
    if strLeft == "" and strRight == "":
        logger.debug("No filter. Return empty list")
        return []
    else:
        # Generate list of words for limiting the search space via word index
        strComplete = strLeft.strip() + " " + strMiddle.strip() + " " + strRight.strip()
        allTokensL = strComplete.split(" ")
        for t in allTokensL:
            if t != "*": allSets.append(index[t])
        nGramSelectionS = set.intersection(*allSets)
        for r in nGramSelectionS:
            selRows.append(ngramstat[r])

        logger.debug("Number of matching ngrams by word index: " + str(len(selRows)))

        logger.debug("press key!")

    for row in sorted(selRows, reverse=True):  # iteration through all matching ngrams  
        logger.debug(row)
        # input("press key!)
        ngram = row.split("\t")[1]
        ngramCard = ngram.count(" ") + 1  # cardinality of the nGram
        # Filter by ngram cardinality
        if ngramCard <= maxNumTokens and ngramCard >= minNumTokens:  # -1
            # watch out for multiword input strMiddle
            if int(row.split("\t")[0]) >= minfreq:
                # might suppress low n-gram frequencies
                ngram = row.split("\t")[1].strip()
                m = re.search(regexEmbed, ngram, re.IGNORECASE)
                if m != None and not row in allBeds:
                    allBeds.append(row)
                    logger.debug(row)
                    count += 1
                    if count >= maxcount:
                        logger.debug("List cut at " + str(count))
                        break

        logger.debug("press key!")

    selBeds = functions.random_sub_list(allBeds, count)
    # print(selBeds)
    # random selection of hits, to avoid explosion
    logger.debug("Embeddings:")
    if logger.getEffectiveLevel() == logging.DEBUG:
        for item in allBeds: print(item)

    # print(len(selBeds), selBeds)
        logger.debug("Generated list of " + str(count) + " matching n-grams")
        logger.debug("strike key")

    if count > 0:
        iMaxNum = (maxcount // count) + 3
        logger.debug("Per matching n-gram " + str(iMaxNum) + " surroundings")

        # print("----------------------------------------------")
        for row in selBeds:  # iterate through extract
            bed = row.split("\t")[1].strip()

            newSets = []
            regexBed = "^" + re.escape(bed) + "$"
            regexBed = regexBed.replace(strMiddleEsc, "(.*)")
            surroundingsL = bed.replace(strMiddle + " ", "").split(" ")
            for w in surroundingsL:
                logger.debug("Surrounding strMiddle: " + w)
                newSets.append(index[w])
            ngramsWithSurroundings = list(set.intersection(*newSets))
            logger.debug("Size of list that includes surrounding elements: " + str(len(ngramsWithSurroundings)))
            ngramsWithSurroundings.sort(reverse=True)
            # Surrounding list sorted
            c = 0
            for r in ngramsWithSurroundings:
                if c > iMaxNum: break
                row = ngramstat[r]
                ngram = row.split("\t")[1].strip()
                freq = row.split("\t")[0]
                m = re.search(regexBed, ngram, re.IGNORECASE)
                if m != None:
                    # print(regexBed)
                    # print(row)
                    out = m.group(1).strip()
                    if (not strMiddle in out) and \
                            len(out) > minWinSize and \
                            not "¶" in out and (not DIGIT in out):
                        # print(ngramfrequency, out, "   [" + ngram + "]")
                        c = c + 1
                        outL.append(freq + "\t" + out)

        outL.sort(reverse=True)
    if logger.getEffectiveLevel() == logging.DEBUG:
        for item in outL: logger.debug(item)
    return outL


if logger.getEffectiveLevel() == logging.DEBUG:
    normalisedTokens = pickle.load(open("pickle//tokens.p", "rb"))
    ngramstat = pickle.load(open("pickle//ngramstat.p", "rb"))
    index = pickle.load(open("pickle//index.p", "rb"))
    logger.debug("Dumps loaded")
    # li = findEmbeddings("", "morph.", "", ngramstat, index, 10, 3, 1000, 1, 7)
    # li = findEmbeddings("Mitralklappe", "morph.", "*", ngramstat, index, 10, 3, 1000, 1, 7)
    # li = findEmbeddings("", "morph.", "", ngramstat, index, 18, 3, 1000, 1, 1)
    # li = findEmbeddings("", "morph.", "unauff.", ngramstat, index, 18, 3, 1000, 3, 7)
    # li = findEmbeddings("*", "ms", "*", ngramstat, index, 8, 30, 500, 1, 5)
    # li = findEmbeddings("Ð,Ð", "ms", "", ngramstat, index, 8, 3, 500, 1, 7)
    # out = (Filters.bestAcronymResolution("OL", li, normalisedTokens, "AA", ""))

    # Parms: minWinSize, minfreq, maxcount, minNumberTokens, maxNumberTokens
    # print(findEmbeddings("TRINS", ngramstat, index, 1, 3, 10, 6))
    # print(findEmbeddings("HRST", ngramstat, index, 15, 3, 20, 6)) # wird nicht gefunden!
    # print(findEmbeddings("ACVB", ngramstat, index, 15, 3, 10, 9))# wird nicht gefunden!

    # print(findEmbeddings("Rö-Thorax", ngramstat, index, 10, 1, 20, 3)) # wird gefunden!

    # print(findEmbeddings("TRINS", ngramstat, index, 15, 1, 50, 3))
    # print(findEmbeddings("TRINS", ngramstat, index, 15, 1, 100, 3))
    # print(findEmbeddings("koronare Herzkrankheit", ngramstat, index, 20, 1, 100, 5))
    # print(findEmbeddings("re OL", ngramstat, index, 5, 1, 100, 6)) # OL kommt nur 4 mal vor !

    # print(findEmbeddings("Herz- und", ngramstat, index, 20, 1, 100, 5))
    # print(findEmbeddings("lab. maj", ngramstat, index, 20, 3, 100, 5, 6))

    # print(findEmbeddings("gutem", "AZ", "nach Hause", ngramstat, index, 10, 3, 100, 3, 7, False))

    logger.debug(findEmbeddings("*", "PDU", "*", ngramstat, index, 10, 3, 50, 1, 5, False))
