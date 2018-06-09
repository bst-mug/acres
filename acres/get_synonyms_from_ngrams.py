# Stefan Schulz 21 August 2017
"""
Finds synonyms using a n-gram frequency list from related corpus
"""

import logging
import re

from acres import functions
from acres import resource_factory

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def test_input(l_probe, left, middle, right):
    # tests an acronym + context strings against the ngram model
    lstExp = find_embeddings(left, middle, right, 1, 1, 500, 2, 10)
    for term in lstExp:
        logger.info(term)
        for probe in l_probe:
            if term.split("\t")[1].lower() == probe.lower():
                logger.info("FOUND: " + term)
                return True
    return False


def find_embeddings(str_left, str_middle, str_right, min_win_size, minfreq, maxcount,
                    min_num_tokens, max_num_tokens):
    """
    Input str_middle, together with a series of filter parameters
    Three cases of embeddings: 1. bilateral, 2.left, 3.right

    :param str_left: string left of unknown ("<SEL>" if to be retrieved ; "<VOID>" if empty)
    :param str_middle: input nonlex form (with or without context words) for which synonym is sought
    :param str_right: string right uf unknown ("<SEL>" if to be retrieved ; "<VOID>" if empty")
    :param min_win_size: minimum window size
    :param minfreq: minimum ngram frequency
    :param maxcount: maximum count in list
    :param min_num_tokens:
    :param max_num_tokens:
    :return:
    """
    # dependency injection
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
    #                         Left             Middle              Right
    # VOID	                  "^"                                   "$"
    # Specified ("abc")	     "^abc\ "	      "abc"            "\ abc$"
    # SELCETED                "^.*\ "                            "\ .*$"
    # Build regular expression for matching ngram

    # Three

    if str_left == "<SEL>":
        str_left_esc = "^.*\ "
    elif str_left == "<VOID>":
        str_left_esc = "^"
    else:
        str_left_esc = "^" + re.escape(str_left.strip()) + "\ "

    str_middle_esc = re.escape(str_middle.strip())
    if str_right == "<SEL>":
        str_right_esc = "\ .*$"
    elif str_right == "<VOID>":
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

    # set of selected ngrams for filtering
    if str_left == "<VOID>" and str_right == "<VOID>":
        logger.debug("No filter. Return empty list")
        return []
    else:
        # Generate list of words for limiting the search space via word index
        str_complete = str_left.strip() + " " + str_middle.strip() + " " + str_right.strip()
        all_tokens = str_complete.split(" ")
        for token in all_tokens:
            if token != "<VOID>" and token != "<SEL>":
                all_sets.append(index[token])
        ngram_selection = set.intersection(*all_sets)
        for ngram in ngram_selection:
            sel_rows.append(ngramstat[ngram])

        logger.debug("Number of matching ngrams by word index: %d", len(sel_rows))

    for row in sorted(sel_rows, reverse=True):  # iteration through all matching ngrams
        logger.debug(row)
        # input("press key!)
        ngram = row.split("\t")[1]
        ngram_card = ngram.count(" ") + 1  # cardinality of the nGram
        # Filter by ngram cardinality
        if max_num_tokens >= ngram_card >= min_num_tokens:  # -1
            # watch out for multiword input str_middle
            # TODO: min should be at least 1 plus cardinality of middle term
            if int(row.split("\t")[0]) >= minfreq:
                # might suppress low n-gram frequencies
                # TODO: probably best 1, could be increased for performance
                # TODO: the current ngram dump and index were created on a lower
                # TODO: frequency bound of 2
                # TODO: This is the reason, some acronyms cannot be resolved
                # TODO: recommendation: recreate
                ngram = row.split("\t")[1].strip()
                match = re.search(regex_embed, ngram, re.IGNORECASE)
                # all_beds collects all contexts in which the unknown string
                # is embedded.
                # the length of right and left part of "bed" is only
                # limited by the length of the ngram
                if match is not None and row not in all_beds:
                    all_beds.append(row)
                    logger.debug(row)
                    count += 1
                    if count >= maxcount:
                        logger.debug("List cut at %d", count)
                        break
    logger.info("COUNT: " + str(count))

    sel_beds = functions.random_sub_list(all_beds, count)
    # print(sel_beds)
    # random selection of hits, to avoid explosion
    logger.debug("Embeddings:")
    if logger.getEffectiveLevel() == logging.DEBUG:
        for item in all_beds:
            logger.debug(item)

        # print(len(sel_beds), sel_beds)
        logger.debug("Generated list of %d matching n-grams", count)

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
            for ngram in ngrams_with_surroundings:
                if counter > max_num:
                    break
                row = ngramstat[ngram]
                ngram = row.split("\t")[1].strip()
                freq = row.split("\t")[0]
                match = re.search(regex_bed, ngram, re.IGNORECASE)
                if match is not None:
                    # logger.debug(regex_bed)
                    # logger.debug(row)
                    long_form = match.group(1).strip()
                    if len(long_form) > len(str_middle) and \
                            "¶" not in long_form and \
                            digit not in long_form:
                        # logger.debug(ngramfrequency, long_form, "   [" + ngram + "]")
                        counter += 1
                        rec = freq + "\t" + long_form.strip()
                        if not rec in out:
                            out.append(rec)

        out.sort(reverse=True)

    if logger.getEffectiveLevel() == logging.DEBUG:
        for item in out:
            logger.debug(item)
    return out
