# Stefan Schulz 21 August 2017
"""
Finds synonyms using a n-gram frequency list from related corpus
"""

import logging
import re

from acres import functions
from acres import resource_factory

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def find_embeddings(str_left, str_middle, str_right, min_win_size, minfreq, maxcount, min_num_tokens, max_num_tokens):
    """
    Input str_middle, together with a series of filter parameters
    Three cases of embeddings: 1. bilateral, 2.left, 3.right

    :param str_left: string left of unknown ("*" if to be retrieved ; "" if empty")
    :param str_middle: input nonlex form (with or without context words) for which synonym is sought
    :param str_right: string right uf unknown ("*" if to be retrieved ; "" if empty")
    :param min_win_size: minimum window size
    :param minfreq: minimum ngram frequency
    :param maxcount: maximum count in list
    :param min_num_tokens:
    :param max_num_tokens:
    :return:
    """
    ngramstat = resource_factory.get_ngramstat()
    index = resource_factory.get_index()

    # MAXLIST = 100
    digit = "Ð"
    out = []
    all_beds = []
    all_sets = []
    sel_rows = []
    count = 0

    # Construction of regular expression
    #                       Left             Middle              Right
    # Empty	            "^"                                   "$"
    # Specified ("abc")	    "^abc\ "	      "abc"            "\ abc$"
    # Arbitrary, nonempty   "^.*\ "                            "\ .*$"
    # Build regular expression for matching ngram

    if str_left == "*":
        str_left_esc = "^.*\ "
    elif str_left == "":
        str_left_esc = "^"
    else:
        str_left_esc = "^" + re.escape(str_left.strip()) + "\ "
    str_middle_esc = re.escape(str_middle.strip())
    if str_right == "*":
        str_right_esc = "\ .*$"
    elif str_right == "":
        str_right_esc = "$"
    else:
        str_right_esc = "\ " + re.escape(str_right.strip()) + "$"
    regex_embed = str_left_esc + str_middle_esc + str_right_esc

    logger.debug("Unknown expression: '%s'", str_middle_esc)
    logger.debug("Left context: '%s'", str_left_esc)
    logger.debug("Right context: '%s'", str_right_esc)
    logger.debug("Minimum n-gram frequency: %d", minfreq)
    logger.debug("Maximum count of iterations: %d", maxcount)
    logger.debug("N-gram cardinality between %d and %d",
                 min_num_tokens, max_num_tokens)
    logger.debug("Regular expression: %s", regex_embed)

    logger.debug("press key!")

    # set of selected ngrams for filtering
    if str_left == "" and str_right == "":
        logger.debug("No filter. Return empty list")
        return []
    else:
        # Generate list of words for limiting the search space via word index
        str_complete = str_left.strip() + " " + str_middle.strip() + " " + str_right.strip()
        all_tokens = str_complete.split(" ")
        for token in all_tokens:
            if token != "*":
                all_sets.append(index[token])
        ngram_selection = set.intersection(*all_sets)
        for r in ngram_selection:
            sel_rows.append(ngramstat[r])

        logger.debug(
            "Number of matching ngrams by word index: %d", len(sel_rows))

        logger.debug("press key!")

    for row in sorted(
            sel_rows, reverse=True):  # iteration through all matching ngrams
        logger.debug(row)
        # input("press key!)
        ngram = row.split("\t")[1]
        ngram_card = ngram.count(" ") + 1  # cardinality of the nGram
        # Filter by ngram cardinality
        if max_num_tokens >= ngram_card >= min_num_tokens:  # -1
            # watch out for multiword input str_middle
            if int(row.split("\t")[0]) >= minfreq:
                # might suppress low n-gram frequencies
                ngram = row.split("\t")[1].strip()
                m = re.search(regex_embed, ngram, re.IGNORECASE)
                if m is not None and row not in all_beds:
                    all_beds.append(row)
                    logger.debug(row)
                    count += 1
                    if count >= maxcount:
                        logger.debug("List cut at %d", count)
                        break

        logger.debug("press key!")

    sel_beds = functions.random_sub_list(all_beds, count)
    # print(sel_beds)
    # random selection of hits, to avoid explosion
    logger.debug("Embeddings:")
    if logger.getEffectiveLevel() == logging.DEBUG:
        for item in all_beds:
            print(item)

        # print(len(sel_beds), sel_beds)
        logger.debug("Generated list of %d matching n-grams", count)
        logger.debug("strike key")

    if count > 0:
        max_num = (maxcount // count) + 3
        logger.debug("Per matching n-gram %d surroundings", max_num)

        # print("----------------------------------------------")
        for row in sel_beds:  # iterate through extract
            bed = row.split("\t")[1].strip()

            new_sets = []
            regex_bed = "^" + re.escape(bed) + "$"
            regex_bed = regex_bed.replace(str_middle_esc, "(.*)")
            surroundings = bed.replace(str_middle + " ", "").split(" ")
            for word in surroundings:
                logger.debug("Surrounding str_middle: %s", word)
                new_sets.append(index[word])
            ngrams_with_surroundings = list(set.intersection(*new_sets))
            logger.debug(
                "Size of list that includes surrounding elements: %d",
                len(ngrams_with_surroundings))
            ngrams_with_surroundings.sort(reverse=True)
            # Surrounding list sorted
            counter = 0
            for r in ngrams_with_surroundings:
                if counter > max_num:
                    break
                row = ngramstat[r]
                ngram = row.split("\t")[1].strip()
                freq = row.split("\t")[0]
                m = re.search(regex_bed, ngram, re.IGNORECASE)
                if m is not None:
                    # logger.debug(regex_bed)
                    # logger.debug(row)
                    out = m.group(1).strip()
                    if (str_middle not in out) and \
                            len(out) > min_win_size and \
                            "¶" not in out and (digit not in out):
                        # logger.debug(ngramfrequency, out, "   [" + ngram + "]")
                        counter += 1
                        out.append(freq + "\t" + out)

        out.sort(reverse=True)
    if logger.getEffectiveLevel() == logging.DEBUG:
        for item in out:
            logger.debug(item)
    return out


if logger.getEffectiveLevel() == logging.DEBUG:
    normalisedTokens = resource_factory.get_tokens()
    logger.debug("Dumps loaded")
    # li = find_embeddings("", "morph.", "", ngramstat, index, 10, 3, 1000, 1, 7)
    # li = find_embeddings("Mitralklappe", "morph.", "*", ngramstat, index, 10, 3, 1000, 1, 7)
    # li = find_embeddings("", "morph.", "", ngramstat, index, 18, 3, 1000, 1, 1)
    # li = find_embeddings("", "morph.", "unauff.", ngramstat, index, 18, 3, 1000, 3, 7)
    # li = find_embeddings("*", "ms", "*", ngramstat, index, 8, 30, 500, 1, 5)
    # li = find_embeddings("Ð,Ð", "ms", "", ngramstat, index, 8, 3, 500, 1, 7)
    # out = (Filters.bestAcronymResolution("OL", li, normalisedTokens, "AA", ""))

    # Parms: minWinSize, minfreq, maxcount, minNumberTokens, maxNumberTokens
    # logger.debug(find_embeddings("TRINS", ngramstat, index, 1, 3, 10, 6))
    # logger.debug(find_embeddings("HRST", ngramstat, index, 15, 3, 20, 6)) # wird nicht gefunden!
    # logger.debug(find_embeddings("ACVB", ngramstat, index, 15, 3, 10, 9))# wird
    # nicht gefunden!

    # logger.debug(find_embeddings("Rö-Thorax", ngramstat, index, 10, 1, 20, 3)) #
    # wird gefunden!

    # logger.debug(find_embeddings("TRINS", ngramstat, index, 15, 1, 50, 3))
    # logger.debug(find_embeddings("TRINS", ngramstat, index, 15, 1, 100, 3))
    # logger.debug(find_embeddings("koronare Herzkrankheit", ngramstat, index, 20, 1, 100, 5))
    # logger.debug(find_embeddings("re OL", ngramstat, index, 5, 1, 100, 6)) # OL
    # kommt nur 4 mal vor !

    # logger.debug(find_embeddings("Herz- und", ngramstat, index, 20, 1, 100, 5))
    # logger.debug(find_embeddings("lab. maj", ngramstat, index, 20, 3, 100, 5, 6))

    # logger.debug(find_embeddings("gutem", "AZ", "nach Hause", ngramstat, index, 10, 3, 100, 3, 7))

    logger.debug(find_embeddings("*", "PDU", "*", 10, 3, 50, 1, 5))
