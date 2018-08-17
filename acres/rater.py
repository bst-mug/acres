"""
Stefan Schulz 11 Nov 2017
"""

import logging
import re

import acres.util.acronym

logger = logging.getLogger(__name__)


def get_acronym_score(acro: str, full: str, language="de"):
    """
    TODO: All morphosaurus stuff eliminated. Could check past versions later
    TODO: whether this is worth while considering again
    Scores Acronym / resolution pairs according to a series of well-formedness criteria using a
    n-gram frequency list from related corpus.

    The scoring function should work both for acronyms extracted from a corpus (for which strict
    matching criteria should be applied) and for acronyms harvested from the Web for which the
    criteria may be relaxed once strong evidence from acronym - definition patterns exist
    E.g., "ARDS (akutes Atemnotsyndrom)" : There might be acronym - definition patterns
    in well-written clinical documents.

    In the latter case, full would take this form, i.e. a string that contains both the acronym and
    the expansion

    For checking for valid German expansions it is important to consider variants,
    therefore invoke spelling variant generator from acres.util.text.
    At this place more rules can be added


    TODO:
    all scoring / penalization is pure heuristics. Plausibility should be tested with many
    examples !

    :param acro: acronym to be expanded
    :param full: long form to be checked whether it qualifies as an acronym expansion
    :param language: Expansion language. Matters especially regarding the possible infixes for
    single noun composition
    :return: score that rates the likelihood that the full form is a valid expansion of the acronym
    """

    last_letter_stripped = False  # see below cases in which the lat letter of an acronym is stripped
    is_acronym_definition_pair = False
    acro = acro.strip()
    full = full.strip()

    ##
    ## ELIMINATION RULES
    ##

    # acronym must have at least two characters: all those expressions like "Streptococcus B" or
    # "Vitamin C" should not be considered containg acronyms. Normally these compositions are lexicalised
    # May be relevant for assessing single letter forms like "A cerebralis"
    if len(acro) < 2:
        return (full, 0, "Single letter acronym")
    acro_low = acro.lower()
    full_low = full.lower()

    if language == "de":
        if full.islower():
            return (full, 0, "Full form without capitals")

    # length restriction for full form
    # TODO: could be much greater then 5. Look for cases in which this is an issue
    if len(full) < 5:
        return (full, 0, "Full form too short")

    # Schwartz / Hearst rule
    if full.count(" ") + 1 > len(acro) * 2:
        return (full, 0, "Contradicts Schwartz / Hearst rule")
    if full.count(" ") + 1 > len(acro) + 5:
        return (full, 0, "Contradicts Schwartz / Hearst rule")
    # SCHWARTZ, Ariel S.; HEARST, Marti A. A simple algorithm for identifying abbreviation
    # definitions in biomedical text. In: Biocomputing 2003. 2002. S. 451-462.

    ## ACRONYM DEFINITION PATTERNS
    ## full form contains an acronym definition pattern (normally only yielded
    ## from Web scraping, unlikely in clinical texts)
    ## acronym is included; is then removed from full form

    acro_def_pattern = acres.util.acronym.extract_acronym_definition(full, 7)
    if acro_def_pattern is not None:
        is_acronym_definition_pair = True
        if acro_def_pattern[0] == acro:
            full = acro_def_pattern[1]
            # high score, but also might be something else

    else:
        # acronym must not occur within full form (case sensitive)
        if acro in full:
            return (full, 0, "Acronym case-sensitive substring of full")
        if "(" in full or ")" in full:
            return (full, 0, "Parenthesis in full")

    ## from here no elimination

    ## GENERATION OF VARIANTS
    ## Typical substitutions, mostly concerning the inconsistent use
    ## of k, c, and z in clinical texts
    ## can be enhanced by frequent translations in acres.util.text.

    lst_var = acres.util.text.generate_all_variants_by_rules(full)
    full_old = full
    score = 0
    for full in lst_var:
        go_next = False
        old_score = score
        full_low = full.lower()
        # here no direct eliminations

        if language == "de":
            # Plural form of acronym reduced to singular ("s", often not found in non English full
            # forms) e.g. "EKGs", "EKGS", "NTx", "NTX" (Nierentransplantation)
            # These characters cannot be always expected to occur in the full form
            # We assume that plurals and genitives of acronyms are often marked with
            # "s", however not necessarily lower case.
            # This means that "S" and "X" are not required to match
            lst_acronym_suffixes = ["s", "S", "x", "X"]
            if (acro[-1] in lst_acronym_suffixes):
                acro = acro[0:-1]
                acro_low = acro_low[0:-1]
                last_letter_stripped = True

        # first chars must be the same, certain tolerance with acronym definition pairs
        if acro_low[0] != full_low[0]:
            if not is_acronym_definition_pair: go_next = True

        # last char of acronym must occur in last word of full
        # but not at the end unless it is a single letter
        # "EKG" = "Entwicklung" should not match
        # "Hepatitis A" -> "HEPA" should match
        # HOWEVER: not applicable if last letter stripped
        if not last_letter_stripped:
            last_word = full_low.split(" ")[-1]
            if len(last_word) == 1 and acro_low[-1] != last_word:
                # Rightmost acronym character is not equal rightmost single-char word
                if not is_acronym_definition_pair: go_next = True
            if not acro_low[-1] in last_word[0:-1]:
                # Rightmost acronym character is not in rightmost word
                if not is_acronym_definition_pair: go_next = True

        if not go_next:
            score = 1
            regex = "^"
            for c in acro_low:
                regex = regex + c + ".*"
            if re.search(regex, full_low) is None:
                if is_acronym_definition_pair:
                    score = score * 0.1
                else:
                    score = 0
            else:
                # TODO
                # The more word initials coincide with acronym letters the better
                # especially for German (probably exclusively for German:
                # matching first letter capitals (nouns) even better
                # nevertheless, the following clause should be revised

                expanded_upper = ""
                if full.count(" ") > 0:
                    lst_token = full.split(" ")
                    for tok in lst_token:
                        if tok > " ":
                            if tok[0].isupper():
                                expanded_upper = expanded_upper + tok[0] + ".*"

                # if upper case word initial is not represented in the acronym, then
                # penalisation
                if re.search(expanded_upper, acro) is None:
                    score = score * 0.25  # FIXME: check whether right

        if old_score > score:
            score = old_score

    # decapitalized acronym should not occur within decap full form,
    # if acronym has three or more letters

    if is_acronym_definition_pair:
        score = score * 10
    else:

        if acro_low in full_low:
            score = score * 0.2
    return (full_old, score, "End")


def get_best_acronym_web_resolution(left: str, acro: str, right: str, minimum_len, maximum_word_count, language="de"):
    """
    This is the main file to be used to leverage Bing search for resolving acronyms
    :param left: left context of acronym to be expanded (any length)
    :param acro: acronym to be expanded
    :param right: right context of acronym to be expanded (any length)
    :param minimum_len: the minimum length of the context words to be considered (e.g. to exclude short articles etc.)
    :param maximum_word_count: the maximum of context words that are put into the query
    :return: best expansion of acronym
    """
    r = acres.evaluation.corpus.get_web_dump_from_acro_with_context(
        left, acro, right, minimum_len, maximum_word_count)
    old_weight = 0
    for t in r:
        s = get_acronym_score(acro, t[1], language="de")
        if s[1] > 0:
            weight = t[0] * s[1]
            if weight > old_weight:
                out = s[0]
            old_weight = weight
    return out





if __name__ == "__main__":
    print(get_acronym_score("CMP", "Cardiomyopathie", language="de") )