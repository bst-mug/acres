"""
Stefan Schulz 11 Nov 2017
"""

import logging
import re
from typing import Tuple

import acres.util.acronym
from acres.util import variants

logger = logging.getLogger(__name__)


def get_acronym_score(acro: str, full: str, language: str = "de") -> Tuple[str, float, str]:
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
    :param language: Expansion language. Matters especially regarding the possible infixes for \
    single noun composition
    :return: score that rates the likelihood that the full form is a valid expansion of the acronym
    """

    # see below cases in which the lat letter of an acronym is stripped
    last_letter_stripped = False
    is_acronym_definition_pair = False
    acro = acro.strip()
    full = full.strip()

    #
    # ELIMINATION RULES
    #

    # acronym must have at least two characters: all those expressions like "Streptococcus B" or
    # "Vitamin C" should not be considered containg acronyms. Normally these compositions are
    # lexicalised
    # May be relevant for assessing single letter forms like "A cerebralis"

    if "(" in full or ")" in full:
        return (full, 0, "Parenthesis in full expression ")

    if len(full) <= 5:
        return (full, 0, "Full expression too short")

    if acres.util.functions.is_stopword(full.split(' ', 1)[0]):
        return (full, 0, "first word in stopword list")

    if len(acro) < 2:
        return (full, 0, "Single letter acronym")
    acro_low = acro.lower()
    full_low = full.lower()

    if language == "de":
        if full.islower():
            return (full, 0, "Full form without capitals")

    # length restrictions (according to analysis of
    # "acro_full_reference.txt" (modified from Wikipedia))
    # TODO: could be much greater then 5. Look for cases in which this is an issue
    if len(acro) / len(full) < 0.05:
        return (full, 0, "Full form too long")

    if len(acro) / len(full) > 0.6:
        return (full, 0, "Full form too short")

    lev = acres.util.functions.levenshtein(acro.upper(),
                                           acres.util.acronym.create_german_acronym(full))
    if lev >= len(acro):
        return (full, 0, "Levenshtein edit distance too high")

    # Schwartz / Hearst rule
    if full.count(" ") + 1 > len(acro) * 2:
        return (full, 0, "Contradicts Schwartz / Hearst rule")
    if full.count(" ") + 1 > len(acro) + 5:
        return (full, 0, "Contradicts Schwartz / Hearst rule")
    # SCHWARTZ, Ariel S.; HEARST, Marti A. A simple algorithm for identifying abbreviation
    # definitions in biomedical text. In: Biocomputing 2003. 2002. S. 451-462.

    # ACRONYM DEFINITION PATTERNS
    # full form contains an acronym definition pattern (normally only yielded
    # from Web scraping, unlikely in clinical texts)
    # acronym is included; is then removed from full form

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

    # from here no elimination

    # GENERATION OF VARIANTS
    # Typical substitutions, mostly concerning the inconsistent use
    # of k, c, and z in clinical texts
    # can be enhanced by frequent translations in acres.util.text.

    lst_var = variants.generate_all_variants_by_rules(full)
    full_old = full
    score = 0.0
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
            if acro[-1] in lst_acronym_suffixes:
                acro = acro[0:-1]
                acro_low = acro_low[0:-1]
                last_letter_stripped = True

        # first chars must be the same, certain tolerance with acronym definition pairs
        if acro_low[0] != full_low[0]:
            if not is_acronym_definition_pair:
                go_next = True

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
            for char in acro_low:
                regex = regex + char + ".*"
            if re.search(regex, full_low) is None:
                if is_acronym_definition_pair:
                    score = score * 0.1
                else:
                    score = 0
            else:

                # rightmost expansion should start with upper case initial
                if language == "de":
                    if full.split(" ")[-1][0].islower():
                        score = score * 0.25

                # exact match of real acronym with generated acronym
                if language == "de":
                    if acro.upper() == acres.util.acronym.create_german_acronym(full):
                        score = score * 2

                # if short full form, the coincidence of the first two letters of full and acronym
                # increases score
                if full.count(" ") + 1 < len(acro):
                    if full.upper()[0:2] == acro.upper()[0:2]:
                        score = score * 2

        if old_score > score:
            score = old_score

    # decapitalized acronym should not occur within decap full form,
    # if acronym has three or more letters

    if is_acronym_definition_pair:
        score = score * 10
    else:

        if acro_low in full_low:
            score = score * 0.2

    return full_old, round(score, 2), 'End'
