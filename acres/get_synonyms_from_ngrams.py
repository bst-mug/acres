# Stefan Schulz 21 August 2017
"""
Finds synonyms using a n-gram frequency list from related corpus
"""

import logging
from logging.config import fileConfig

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import re
from typing import List, Tuple, Set
from acres.util import functions
from acres.preprocess import resource_factory


def _build_search_ngrams(context: str, reverse=False) -> Tuple[str, str, str]:
    """
    Builds a context tuple containing 1 to n-grams

    :param context: A string with the context
    :param reverse: Takes the context in reverse (e.g. left context)
    :return: A tuple with 1 to n-gram
    """
    # TODO tentative
    unigram = bigram = trigram = "<SEL>"
    if context != "":
        tokens = context.split(" ")
        unigram = " ".join(tokens[-1:]) if reverse else " ".join(tokens[:1])
        bigram = " ".join(tokens[-2:]) if reverse else " ".join(tokens[:2])
        trigram = " ".join(tokens[-3:]) if reverse else " ".join(tokens[:3])
    return unigram, bigram, trigram


def _strip_frequencies(embeddings: List[Tuple[int,str]], min_freq: int = 0) -> List[str]:
    """
    Strip out frequencies from a given embedding list obtained via find_embeddings.

    :param embeddings: A list of embeddings in the format freq\tembedding.
    :param min_freq: Minimum frequency to be used (defaults to 0).
    :return: A list of embeddings containing only strings with a minimum frequency.
    """
    ret = []
    for embedding in embeddings:
        (freq, ngram) = embedding
        if freq >= min_freq:
            ret.append(ngram)
    return ret


def robust_find_embeddings(acronym: str, left_context: str, right_context: str) -> List[str]:
    """
    Generates several search patterns and returns the first found embeddings.

    @todo integrate with logic from find_synonyms()?

    :param acronym:
    :param left_context:
    :param right_context:
    :return:
    """
    (left_unigram, left_bigram, left_trigram) = _build_search_ngrams(left_context, True)
    (right_unigram, right_bigram, right_trigram) = _build_search_ngrams(right_context)

    # Order is important for the quality of the retrieved expansion
    patterns = [(left_trigram, right_trigram),  # trigrams
                (left_bigram, right_trigram), (left_trigram, right_bigram),  # bigram + trigram
                (left_bigram, right_bigram),  # bigrams
                (left_unigram, right_bigram), (left_bigram, right_unigram),  # bigram + unigram
                (left_unigram, right_unigram),  # unigrams
                (left_bigram, "<SEL>"), (left_unigram, "<SEL>"),  # bigram/unigram + <SEL>
                ("<SEL>", right_bigram), ("<SEL>", right_unigram),  # <SEL> + bigram/unigram
                ("<SEL>", "<SEL>"),  # <SEL> + <SEL>
                ("<SEL>", "<VOID>"), ("<VOID>", "<SEL>")  # <SEL> + <VOID>
                ]

    previous_left_pattern = previous_right_pattern = ""
    for pattern in patterns:
        (left_pattern, right_pattern) = pattern
        logger.debug("%s | %s", left_pattern, right_pattern)

        # Quick optimization: don't search for patterns that happens to be the same as last one
        if left_pattern != previous_left_pattern or right_pattern != previous_right_pattern:
            embeddings = find_embeddings(left_pattern, acronym, right_pattern, 1, 1, 500, 2, 10)
            if len(embeddings) > 0:
                return _strip_frequencies(embeddings)

            previous_left_pattern = left_pattern
            previous_right_pattern = right_pattern

    return []


def find_embeddings(str_left: str, str_middle: str, str_right: str, min_win_size: int, minfreq: int,
                    maxcount: int, min_num_tokens: int, max_num_tokens: int) -> List[Tuple[int,str]]:
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
    out = []        # type: List[Tuple[int,str]]
    all_beds = []   # type: List[Tuple[int,str]]
    all_sets = []   # type: List[Set[int]]
    sel_rows = []   # type: List[Tuple[int,str]]
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
        for ngram_id in ngram_selection:
            sel_rows.append(ngramstat[ngram_id])

        logger.debug("Number of matching ngrams by word index: %d", len(sel_rows))

    for row in sorted(sel_rows, reverse=True):  # iteration through all matching ngrams
        # input("press key!)
        (freq, ngram) = row
        logger.debug("%d => %s", freq, ngram)

        ngram_card = ngram.count(" ") + 1  # cardinality of the nGram
        # Filter by ngram cardinality
        if max_num_tokens >= ngram_card >= min_num_tokens:  # -1
            # watch out for multiword input str_middle
            # TODO: min should be at least 1 plus cardinality of middle term
            if freq >= minfreq:
                # might suppress low n-gram frequencies
                # TODO: probably best 1, could be increased for performance
                # TODO: the current ngram dump and index were created on a lower
                # TODO: frequency bound of 2
                # TODO: This is the reason, some acronyms cannot be resolved
                # TODO: recommendation: recreate
                stripped_ngram = ngram.strip()
                match = re.search(regex_embed, stripped_ngram, re.IGNORECASE)
                # all_beds collects all contexts in which the unknown string
                # is embedded.
                # the length of right and left part of "bed" is only
                # limited by the length of the ngram
                if match is not None and row not in all_beds:
                    all_beds.append(row)
                    logger.debug("%d: %s", freq, ngram)
                    count += 1
                    if count >= maxcount:
                        logger.debug("List cut at %d", count)
                        break
    logger.debug("COUNT: " + str(count))

    sel_beds = functions.random_sub_list(all_beds, count)
    # print(sel_beds)
    # random selection of hits, to avoid explosion
    logger.debug("Embeddings:")
    if logger.getEffectiveLevel() == logging.DEBUG:
        for (freq, ngram) in all_beds:
            logger.debug("%d\t%s", freq, ngram)

        # print(len(sel_beds), sel_beds)
        logger.debug("Generated list of %d matching n-grams", count)

    if count > 0:
        max_num = (maxcount // count) + 3
        logger.debug("Per matching n-gram %d surroundings", max_num)

        # print("----------------------------------------------")
        for row in sel_beds:  # iterate through extract
            (freq, ngram) = row
            bed = ngram.strip()

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
            for ngram_id in ngrams_with_surroundings:
                if counter > max_num:
                    break
                (freq, ngram) = ngramstat[ngram_id]
                stripped_ngram = ngram.strip()
                match = re.search(regex_bed, stripped_ngram, re.IGNORECASE)
                if match is not None:
                    # logger.debug(regex_bed)
                    # logger.debug(row)
                    long_form = match.group(1).strip()
                    if len(long_form) > len(str_middle) and \
                            "¶" not in long_form and \
                            digit not in long_form:
                        # logger.debug(ngramfrequency, long_form, "   [" + ngram + "]")
                        counter += 1
                        rec = (freq, long_form.strip())
                        if not rec in out:
                            out.append(rec)

        out.sort(reverse=True)

    return out


if __name__ == "__main__":
    # FIXME "*" does not work anymore
    find_embeddings("nach", "ICD", "Implantation", 1, 2, 500, 1, 10)
    find_embeddings("*", "HF-Anstieg", "von", 1, 2, 500, 1, 10)
    find_embeddings("*", "HT", "rein", 1, 2, 500, 1, 10)
    # viele Treffer, die mit Ht anfangen
    find_embeddings("geplanten", "EPU", "*", 1, 2, 500, 1, 10)
    find_embeddings("einem", "EDP", "von", 1, 2, 500, 1, 10)
    # wird nicht gefunden
    find_embeddings("gutem", "AZ", "nach", 1, 2, 100, 1, 10)
    find_embeddings("die", "VCS.", "*", 1, 2, 500, 1, 10)
    find_embeddings("*", "DG's", "*", 1, 2, 500, 1, 10)
    # only without restricted context the resolution is found
    # only DG's resolved, not DGs
    find_embeddings("die", "VCS.", "*", 1, 2, 500, 1, 10)
    # only works with final dot!
    find_embeddings("re", "OL", "*", 1, 2, 500, 1, 10)
    find_embeddings("die", "VCS", "", 3, 1, 100, 1, 10)

    find_embeddings("gutem", "AZ", "nach", 1, 2, 100, 1, 10)

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
    # logger.debug(find_embeddings("ACVB", ngramstat, index, 15, 3, 10, 9))# wird nicht gefunden!

    # logger.debug(find_embeddings("Rö-Thorax", ngramstat, index, 10, 1, 20, 3)) # wird gefunden!

    # logger.debug(find_embeddings("TRINS", ngramstat, index, 15, 1, 50, 3))
    # logger.debug(find_embeddings("TRINS", ngramstat, index, 15, 1, 100, 3))
    # logger.debug(find_embeddings("koronare Herzkrankheit", ngramstat, index, 20, 1, 100, 5))
    # logger.debug(find_embeddings("re OL", ngramstat, index, 5, 1, 100, 6)) # OL
    # kommt nur 4 mal vor !

    # logger.debug(find_embeddings("Herz- und", ngramstat, index, 20, 1, 100, 5))
    # logger.debug(find_embeddings("lab. maj", ngramstat, index, 20, 3, 100, 5, 6))

    # logger.debug(find_embeddings("gutem", "AZ", "nach Hause", ngramstat, index, 10, 3, 100, 3, 7))

    # logger.debug(find_embeddings("*", "PDU", "*", 10, 3, 50, 1, 5))
