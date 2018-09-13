# Stefan Schulz 21 August 2017
"""
Finds synonyms using a n-gram frequency list from related corpus
"""

import logging
import re
from collections import namedtuple
from typing import List, Tuple, Set, Pattern, AnyStr

from acres.preprocess import resource_factory
from acres.util import functions
from acres.util import text

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

FinderConstraints = namedtuple('FinderConstraints', ['min_freq', 'max_count', 'min_num_tokens',
                                                     'max_num_tokens'])


def _build_search_ngrams(context: str, reverse: bool = False) -> Tuple[str, str, str]:
    """
    Builds a context tuple containing 1 to n-grams

    :param context: A string with the context
    :param reverse: Takes the context in reverse (e.g. left context)
    :return: A tuple with 1 to n-gram
    """
    unigram = bigram = trigram = "<SEL>"
    if context != "":
        unigram = text.context_ngram(context, 1, reverse)
        bigram = text.context_ngram(context, 2, reverse)
        trigram = text.context_ngram(context, 3, reverse)
    return unigram, bigram, trigram


def _strip_frequencies(embeddings: List[Tuple[int, str]], min_freq: int = 0) -> List[str]:
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

    finder_constraints = FinderConstraints(min_freq=1, max_count=500, min_num_tokens=2,
                                           max_num_tokens=10)
    previous_left_pattern = previous_right_pattern = ""
    for pattern in patterns:
        (left_pattern, right_pattern) = pattern
        logger.debug("%s | %s", left_pattern, right_pattern)

        # Quick optimization: don't search for patterns that happens to be the same as last one
        if left_pattern != previous_left_pattern or right_pattern != previous_right_pattern:
            embeddings = find_embeddings(left_pattern, acronym, right_pattern, finder_constraints)
            if embeddings:
                return _strip_frequencies(embeddings)

            previous_left_pattern = left_pattern
            previous_right_pattern = right_pattern

    return []


def find_embeddings(str_left: str, str_middle: str, str_right: str,
                    finder_constraints: FinderConstraints) -> List[Tuple[int, str]]:
    """
    Input str_middle, together with a series of filter parameters
    Three cases of embeddings: 1. bilateral, 2.left, 3.right

    :param str_left: string left of unknown ("<SEL>" if to be retrieved ; "<VOID>" if empty)
    :param str_middle: input nonlex form (with or without context words) for which synonym is sought
    :param str_right: string right uf unknown ("<SEL>" if to be retrieved ; "<VOID>" if empty")
    :param finder_constraints:
    :return:
    """
    logger.debug("Minimum n-gram frequency: %d", finder_constraints.min_freq)
    logger.debug("Maximum count of iterations: %d", finder_constraints.max_count)
    logger.debug("N-gram cardinality between %d and %d",
                 finder_constraints.min_num_tokens, finder_constraints.max_num_tokens)

    # set of selected ngrams for filtering
    if str_left == "<VOID>" and str_right == "<VOID>":
        logger.debug("No filter. Return empty list")
        return []

    sel_rows = _build_sel_rows(str_left, str_middle, str_right)

    regex_embed = _build_regex(str_left, str_middle, str_right)

    all_beds = _build_all_beds(sel_rows, regex_embed, finder_constraints)

    count = len(all_beds)

    # random selection of hits, to avoid explosion
    sel_beds = functions.random_sub_list(all_beds, count)

    # if logger.getEffectiveLevel() == logging.DEBUG:
    #     _debug_embeddings(all_beds)

    if count <= 0:
        return []

    max_num = (finder_constraints.max_count // count) + 3
    logger.debug("Per matching n-gram %d surroundings", max_num)
    return _find_middle(str_middle, sel_beds, max_num)


def _build_regex(str_left: str, str_middle: str, str_right: str) -> Pattern[AnyStr]:
    """

    :param str_left:
    :param str_middle:
    :param str_right:
    :return:
    """
    # Construction of regular expression
    #                         Left             Middle              Right
    # VOID	                  "^"                                   "$"
    # Specified ("abc")	     "^abc\ "	      "abc"            "\ abc$"
    # SELECTED                "^.*\ "                            "\ .*$"
    # Build regular expression for matching ngram

    # Three

    str_middle_esc = re.escape(str_middle.strip())

    if str_left == "<SEL>":
        str_left_esc = r"^.*\ "
    elif str_left == "<VOID>":
        str_left_esc = "^"
    else:
        str_left_esc = "^" + re.escape(str_left.strip()) + r"\ "

    if str_right == "<SEL>":
        str_right_esc = r"\ .*$"
    elif str_right == "<VOID>":
        str_right_esc = "$"
    else:
        str_right_esc = r"\ " + re.escape(str_right.strip()) + "$"
    regex_embed = str_left_esc + str_middle_esc + str_right_esc

    # logger.debug("Unknown expression: '%s'", str_middle_esc)
    # logger.debug("Left context: '%s'", str_left_esc)
    # logger.debug("Right context: '%s'", str_right_esc)
    logger.debug("Regular expression: %s", regex_embed)

    return re.compile(regex_embed, re.IGNORECASE)


def _build_sel_rows(str_left: str, str_middle: str, str_right: str) -> List[Tuple[int, str]]:
    """
    Generate list of words for limiting the search space via word index

    :param str_left:
    :param str_middle:
    :param str_right:
    :return:
    """
    ngramstat = resource_factory.get_ngramstat()
    index = resource_factory.get_index()

    sel_rows = []  # type: List[Tuple[int,str]]
    all_sets = []  # type: List[Set[int]]

    str_complete = str_left.strip() + " " + str_middle.strip() + " " + str_right.strip()
    all_tokens = str_complete.split(" ")
    for token in all_tokens:
        if token != "<VOID>" and token != "<SEL>":
            all_sets.append(index[token])
    ngram_selection = set.intersection(*all_sets)
    for ngram_id in ngram_selection:
        sel_rows.append(ngramstat[ngram_id])

    logger.debug("Number of matching ngrams by word index: %d", len(sel_rows))

    return sel_rows


def _build_all_beds(sel_rows: List[Tuple[int, str]], regex_embed: Pattern[AnyStr],
                    finder_constraints: FinderConstraints) -> List[Tuple[int, str]]:
    """

    #max_num_tokens: int, min_num_tokens: int, minfreq: int, maxcount: int

    :param sel_rows:
    :param regex_embed:
    :param finder_constraints:
    :return:
    """
    all_beds = []  # type: List[Tuple[int,str]]

    count = 0

    for row in sorted(sel_rows, reverse=True):  # iteration through all matching ngrams
        # input("press key!)
        (freq, ngram) = row
        #logger.debug("%d => %s", freq, ngram)

        ngram_card = ngram.count(" ") + 1  # cardinality of the nGram
        # Filter by ngram cardinality
        if finder_constraints.max_num_tokens >= ngram_card >= finder_constraints.min_num_tokens:
            # watch out for multiword input str_middle
            # TODO: min should be at least 1 plus cardinality of middle term
            if freq >= finder_constraints.min_freq:
                # might suppress low n-gram frequencies
                # TODO: probably best 1, could be increased for performance
                # the current ngram dump and index were created on a lower frequency bound of 2
                # This is the reason, some acronyms cannot be resolved
                # recommendation: recreate
                stripped_ngram = ngram.strip()
                match = regex_embed.search(stripped_ngram)
                # all_beds collects all contexts in which the unknown string
                # is embedded.
                # the length of right and left part of "bed" is only
                # limited by the length of the ngram
                if match is not None and row not in all_beds:
                    all_beds.append(row)
                    # logger.debug("%d: %s", freq, ngram)
                    count += 1
                    if count >= finder_constraints.max_count:
                        logger.debug("List cut at %d", count)
                        break

    # logger.debug("COUNT: %d", count)

    return all_beds


def _debug_embeddings(all_beds: List[Tuple[int, str]]) -> None:
    logger.debug("Embeddings:")
    for (freq, ngram) in all_beds:
        logger.debug("%d\t%s", freq, ngram)
    logger.debug("Generated list of %d matching n-grams", len(all_beds))


def _find_middle(str_middle: str, sel_beds: List[Tuple[int, str]], max_num: int) -> List[
    Tuple[int, str]]:
    """

    :param str_middle:
    :param sel_beds:
    :param max_num:
    :return:
    """
    ngramstat = resource_factory.get_ngramstat()
    index = resource_factory.get_index()

    out = []  # type: List[Tuple[int,str]]

    str_middle_esc = re.escape(str_middle.strip())

    # print("----------------------------------------------")
    for row in sel_beds:  # iterate through extract
        (freq, ngram) = row
        bed = ngram.strip()

        new_sets = []
        regex_bed = "^" + re.escape(bed) + "$"
        regex_bed = regex_bed.replace(str_middle_esc, "(.*)")
        compiled_regex_bed = re.compile(regex_bed, re.IGNORECASE)
        surroundings = bed.replace(str_middle + " ", "").split(" ")
        for word in surroundings:
            # logger.debug("Surrounding str_middle: %s", word)
            new_sets.append(index[word])
        ngrams_with_surroundings = list(set.intersection(*new_sets))
        # logger.debug(
        #     "Size of list that includes surrounding elements: %d",
        #     len(ngrams_with_surroundings))
        ngrams_with_surroundings.sort(reverse=True)
        # Surrounding list sorted
        counter = 0
        for ngram_id in ngrams_with_surroundings:
            if counter > max_num:
                break
            (freq, ngram) = ngramstat[ngram_id]
            stripped_ngram = ngram.strip()
            match = compiled_regex_bed.search(stripped_ngram)
            if match is not None:
                # logger.debug(regex_bed)
                # logger.debug(row)
                long_form = match.group(1).strip()
                if len(long_form) > len(str_middle) and \
                        "¶" not in long_form and \
                        "Ð" not in long_form:
                    # logger.debug(ngramfrecquency, long_form, "   [" + ngram + "]")
                    counter += 1
                    rec = (freq, long_form.strip())
                    if rec not in out:
                        out.append(rec)

    out.sort(reverse=True)
    return out
