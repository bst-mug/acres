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


def find_embeddings(str_left,
                    str_middle,
                    str_right,
                    ngramstat,
                    index,
                    min_window_size,
                    min_freq,
                    maxcount,
                    min_num_tokens,
                    max_num_tokens,
                    verbose):
    """
    Input strMiddle, together with a series of filter parameters
    Three cases of embeddings: 1. bilateral, 2.left, 3.right

    :param str_left: string left of unknown ("*" if to be retrieved ; "" if empty")
    :param str_middle: input nonlex form (with or without context words) for which synonym is sought
    :param str_right: string right uf unknown ("*" if to be retrieved ; "" if empty")
    :param ngramstat: ngram model
    :param index: word index to ngram model
    :param min_window_size: minimum window size
    :param min_freq: minimum ngram frequency
    :param maxcount: maximum count in list
    :param min_num_tokens:
    :param max_num_tokens:
    :param verbose:
    :return:
    """
    if verbose:
        logger.setLevel(logging.DEBUG)

    # MAXLIST = 100
    digit = "Ð"
    lst_out = []
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
        str_left_escape = "^.*\ "
    elif str_left == "":
        str_left_escape = "^"
    else:
        str_left_escape = "^" + re.escape(str_left.strip()) + "\ "
    str_middle_escape = re.escape(str_middle.strip())
    if str_right == "*":
        str_right_escape = "\ .*$"
    elif str_right == "":
        str_right_escape = "$"
    else:
        str_right_escape = "\ " + re.escape(str_right.strip()) + "$"
    regex_embed = str_left_escape + str_middle_escape + str_right_escape

    logger.debug("Unknown expression: '%s'", str_middle_escape)
    logger.debug("Left context: '%s'", str_left_escape)
    logger.debug("Right context: '%s'", str_right_escape)
    logger.debug("Minimum n-gram frequency: %d", min_freq)
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
        lst_all_tokens = str_complete.split(" ")
        for t in lst_all_tokens:
            if t != "*":
                all_sets.append(index[t])
        n_gram_selection_s = set.intersection(*all_sets)
        for r in n_gram_selection_s:
            sel_rows.append(ngramstat[r])

        logger.debug(
            "Number of matching ngrams by word index: %d", len(sel_rows))

        logger.debug("press key!")

    for row in sorted(
            sel_rows, reverse=True):  # iteration through all matching ngrams
        logger.debug(row)
        # input("press key!)
        ngram = row.split("\t")[1]
        ngram_cardinality = ngram.count(" ") + 1  # cardinality of the nGram
        # Filter by ngram cardinality
        if max_num_tokens >= ngram_cardinality >= min_num_tokens:  # -1
            # watch out for multiword input strMiddle
            if int(row.split("\t")[0]) >= min_freq:
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

    selected_beds = functions.random_sub_list(all_beds, count)
    # print(selBeds)
    # random selection of hits, to avoid explosion
    logger.debug("Embeddings:")
    if logger.getEffectiveLevel() == logging.DEBUG:
        for item in all_beds:
            print(item)

    # print(len(selBeds), selBeds)
        logger.debug("Generated list of %d matching n-grams", count)
        logger.debug("strike key")

    if count > 0:
        i_max_num = (maxcount // count) + 3
        logger.debug("Per matching n-gram %d surroundings", i_max_num)

        # print("----------------------------------------------")
        for row in selected_beds:  # iterate through extract
            bed = row.split("\t")[1].strip()

            new_sets = []
            regex_bed = "^" + re.escape(bed) + "$"
            regex_bed = regex_bed.replace(str_middle_escape, "(.*)")
            lst_surroundings = bed.replace(str_middle + " ", "").split(" ")
            for w in lst_surroundings:
                logger.debug("Surrounding strMiddle: %s", w)
                new_sets.append(index[w])
            lst_ngrams_with_surroundings = list(set.intersection(*new_sets))
            logger.debug(
                "Size of list that includes surrounding elements: %d",
                len(lst_ngrams_with_surroundings))
            lst_ngrams_with_surroundings.sort(reverse=True)
            # Surrounding list sorted
            c = 0
            for r in lst_ngrams_with_surroundings:
                if c > i_max_num:
                    break
                row = ngramstat[r]
                ngram = row.split("\t")[1].strip()
                freq = row.split("\t")[0]
                m = re.search(regex_bed, ngram, re.IGNORECASE)
                if m is not None:
                    # print(regex_bed)
                    # print(row)
                    out = m.group(1).strip()
                    if (str_middle not in out) and \
                            len(out) > min_window_size and \
                            "¶" not in out and (digit not in out):
                        # print(ngramfrequency, out, "   [" + ngram + "]")
                        c = c + 1
                        lst_out.append(freq + "\t" + out)

        lst_out.sort(reverse=True)
    if logger.getEffectiveLevel() == logging.DEBUG:
        for item in lst_out:
            logger.debug(item)
    return lst_out


if logger.getEffectiveLevel() == logging.DEBUG:
    normalisedTokens = pickle.load(open("pickle//tokens.p", "rb"))
    ngramstat = pickle.load(open("pickle//ngramstat.p", "rb"))
    index = pickle.load(open("pickle//index.p", "rb"))
    logger.debug("Dumps loaded")
    # li = find_embeddings("", "morph.", "", ngramstat, index, 10, 3, 1000, 1, 7)
    # li = find_embeddings("Mitralklappe", "morph.", "*", ngramstat, index, 10, 3, 1000, 1, 7)
    # li = find_embeddings("", "morph.", "", ngramstat, index, 18, 3, 1000, 1, 1)
    # li = find_embeddings("", "morph.", "unauff.", ngramstat, index, 18, 3, 1000, 3, 7)
    # li = find_embeddings("*", "ms", "*", ngramstat, index, 8, 30, 500, 1, 5)
    # li = find_embeddings("Ð,Ð", "ms", "", ngramstat, index, 8, 3, 500, 1, 7)
    # out = (Filters.bestAcronymResolution("OL", li, normalisedTokens, "AA", ""))

    # Parms: minWinSize, minfreq, maxcount, minNumberTokens, maxNumberTokens
    # print(find_embeddings("TRINS", ngramstat, index, 1, 3, 10, 6))
    # print(find_embeddings("HRST", ngramstat, index, 15, 3, 20, 6)) # wird nicht gefunden!
    # print(find_embeddings("ACVB", ngramstat, index, 15, 3, 10, 9))# wird
    # nicht gefunden!

    # print(find_embeddings("Rö-Thorax", ngramstat, index, 10, 1, 20, 3)) #
    # wird gefunden!

    # print(find_embeddings("TRINS", ngramstat, index, 15, 1, 50, 3))
    # print(find_embeddings("TRINS", ngramstat, index, 15, 1, 100, 3))
    # print(find_embeddings("koronare Herzkrankheit", ngramstat, index, 20, 1, 100, 5))
    # print(find_embeddings("re OL", ngramstat, index, 5, 1, 100, 6)) # OL
    # kommt nur 4 mal vor !

    # print(find_embeddings("Herz- und", ngramstat, index, 20, 1, 100, 5))
    # print(find_embeddings("lab. maj", ngramstat, index, 20, 3, 100, 5, 6))

    # print(find_embeddings("gutem", "AZ", "nach Hause", ngramstat, index, 10, 3, 100, 3, 7, False))

    logger.debug(find_embeddings("*", "PDU", "*",
                                 ngramstat, index, 10, 3, 50, 1, 5, False))
