"""
Stefan Schulz 11 Nov 2017
"""

import logging
import re

# from math import *
from acres import functions
from acres.preprocess import resource_factory

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_acronym_score(acro: str, full: str, language="de") -> float:
    """
    Scores Acronym / resolution pairs according to a series of well-formedness criteria using a
    n-gram frequency list from related corpus.

    Scoring is higher the better the full form is properly split into morphemes.
    Requires identification and removal of affixes (infixes, suffixes, like "Gastr-o",
    "Schmerz-en").

    The scoring function should work both for acronyms extracted from a corpus (for which strict
    matching criteria should be applied) and for acronyms harvested from the Web for which the
    criteria may be relaxed once strong evidence from acronym - definition patterns exist
    E.g., "ARDS (akutes Atemnotsyndrom)"

    In the latter case, full would take this form, i.e. a string that contains both the acronym and
    the expansion

    For checking for valid German expansions it is important to consider the K-C-Z rules
    K-C-Z transformation in medical terms:
    "Correct" German writing avoids " CA", "CE", "CI", "CO", "CU, "CY", "COE", "CÖ", "CAE", "CÄ" , "PH"
    and prefers
    "KA", "ZE", "ZI", "KO", "KU", "ZY", "ZOE", "ZÖ", "ZAE", "ZÄ", "F"

    Acronyms often derive from English where the above avoids do not apply.
    Example:
    CMP = Cardiomyopathy

    In these cases, "wrong" German spelling (Cardiomyopathie) is common and would be a valid expansion.
    But also a "correctly" spelt German word can be the expansion of an English acronym with "C"

    Here CMP = Kardiomyopathie

    (Unlikely the other way round.)

    Let cAcro be an acronym containing a "C" and a ZK-Expansion being a German expanded term that uses correct spelling.
    Then cAcro cannot be resolved.
    Hence for all cAcros check alternatively against German ZK terms in which K-C-Z transformation is done
    this is done by generating a test string using the function substitute_k_and_f_and_z_by_context
    (this test string is upper case and still needs to be decapitalised)


    TODO
    all scoring / penalization is pure heuristics. Plausibility should be tested with many
    examples !

    :param acro: acronym to be expanded
    :param full: long form to be checked whether it qualifies as an acronym expansion
    :param language: Expansion language. Matters especially regarding the possible infixes for
    single noun composition
    :return: score that rates the likelihood that the full form is a valid expansion of the acronym
    """
    # Syntactic sugar
    last_letter_stripped = False  # see below cases in which the lat letter of an acromy is stripped

    # TODO it should also work without morphemes
    morphemes = resource_factory.get_morphemes()

    # TODO check whether it makes sense to set score to zero as baseline
    pen = 1.0  # penalization factor
    acro = acro.strip()
    full = full.strip()
    acro_low = acro.lower()
    full_low = full.lower()

    lst_one_letter_affixes = []
    lst_two_letter_affixes = []
    lst_acronym_suffixes = []

    # XXX Dependent on German medical language
    if language == "de":
        lst_one_letter_affixes = ["a", "e", "i", "n", "o", "s", ]
        lst_two_letter_affixes = ["ae", "en", "er", "em", "es", "is", "um", "us"]
        lst_acronym_suffixes = ["s", "S", "x", "X"]  # currently works only with single characters

    # full form contains an acronym definition pattern (normally only yielded
    # from Web scraping, unlikely in clinical texts)
    ret = functions.extract_acronym_definition(full, 7)
    if ret is not None:
        if ret[0] == acro:
            # full = ret[1]
            # maximally high score: in this case we should just believe that the definition is right
            return 100
            # TODO
            # according to the function .extract_acronym_definition
            # this also works for the case in which the acronym is in parentheses
            # Here, false positives are likely. Must be checked!!
    # acronym must have at least two characters: all those expressions like "Streptococcus B" or
    # "Vitamin C" should not be considered containng acronyms. Normally these compositions are lexicalised
    # May be relevant for assessing two letter forms like "A cerebralis"
    # TODO
    # (variant of "A. cerebralis") which is a short form for "Arteria cerbralis".
    # This should be resolved
    if len(acro) < 2:
        return 0
    # length restriction for full form
    # TODO: could be much greater then 3. Look for cases in which this is an issue
    if len(full) < 3:
        return 0
    # acronym must not occur within full form
    if acro in full:
        return 0  # Check A
    # for each acronym in full form, penalisation
    # TODO: check whether artefact
    for token in full.split(" "):
        if functions.is_acronym(token, 7):
            # TODO check how penalisation works. Do we really need a separate penalisation variable?
            pen = pen / 4
    if language == "de":
        # Plural form of acronym reduced to singular ("s", often not found in non English full
        # forms) e.g. "EKGs", "EKGS", "NTx", "NTX" (Nierentransplantation)
        # These characters cannot be always expected to occur in the full form
        # We assume that plurals and genitives of acronyms are often marked with
        # "s", however not necessarily lower case
        if (acro[-1] in lst_acronym_suffixes) \
                and acro[-2:-1].isupper():  # TODO: don't remember why this was a criterion
            acro = acro[0:-1]
            acro_low = acro_low[0:-1]
            last_letter_stripped = True

    # relative length, cf.
    # SCHWARTZ, Ariel S.; HEARST, Marti A. A simple algorithm for identifying abbreviation
    # definitions in biomedical text. In: Biocomputing 2003. 2002. S. 451-462.
    # TODO: check whether these criteria are really strict
    if full.count(" ") + 1 > len(acro) * 2:
        return 0
    if full.count(" ") + 1 > len(acro) + 5:
        return 0

    # decapitalized acronym must not occur within decap full form,
    # if acronym has three or more letters
    if acro_low in full_low and len(acro_low) > 2:
        return 0  # TODO unify with the check A
        # TODO maybe too strict - make it case-sensitive ?
    # first chars must be the same
    if acro_low[0] != full_low[0]:
        return 0  # this is very strict. The only exception would be a Web-derived
        # unambiguous acro-full pattern (already treated above)
    # last char of acronym must occur in last word of full
    # but not at the end unless it is a single letter
    # "EKG" = "Entwicklung" should not match
    # "Hepatitis A" -> "HEPA" should match
    # HOWEVER: not applicable if last letter stripped
    if not last_letter_stripped:
        last_word = full_low.split(" ")[-1]
        if len(last_word) == 1 and acro_low[-1] != last_word:
            return 0
        if not acro_low[-1] in last_word[0:-1]:
            return 0
    # for each word in full higher than length of acronym, penalisation factor
    # (square)
    if len(acro_low) < full_low.count(" ") + 1:
        # TODO does not use previous penalization factor
        pen = 1 / ((full_low.count(" ") + 1 - len(acro_low)) * 2)
        # logger.debug("Penalization = %f", pen)
    # Extract upper case sequence from full form

    # TODO
    # The more word initials coincide with acronym letters the better
    # special for German (probably exclusively for German:
    # matching first letter capitals (nouns) even better
    # nevertheless, the following clause should be revised
    expanded_upper = ""
    if full.count(" ") > 0:
        lst_token = full.split(" ")
        for tok in lst_token:
            if tok > " ":
                if tok[0].isupper():
                    expanded_upper = expanded_upper + tok[0] + ".*"
    expanded_upper = expanded_upper.upper()  # FIXME not needed?
    # if upper case word initial is not represented in the acronym, then
    # penalisation
    if re.search(expanded_upper, acro) is None:
        pen = pen * 0.25  # FIXME: check whether right

    splits = functions.check_acro_vs_expansion(acro_low, full_low)

    score = 0.0
    # logger.debug(splits)
    for split in splits:
        count = 0
        for fragment in split:
            # !!!! Specific for German
            # TODO
            # check whether the function  substitute_k_and_f_by_context
            # could be used instead (produces 7-Bit string without K and F)
            fragment = functions.simplify_german_string(fragment).strip()
            # C, K, and Z no longer distinguished
            # XXX Soundex as an alternative ??
            # logger.debug("FR: " + fragment)
            # Check whether fragments are in german / english morpheme list from Morphosaurus
            if len(fragment) == 1:
                count += 1
                continue

            if fragment in morphemes:
                logger.debug(fragment)
                count += 1
                continue

            if (len(fragment) > 2) and (
                    fragment[-1] in lst_one_letter_affixes) and (fragment[0:-1] in morphemes):
                # stripping one character suffix or infix
                logger.debug(fragment[0:-1])
                count += 1
                continue

            if (len(fragment)) > 3 and (
                    fragment[-2:] in lst_two_letter_affixes) and (fragment[0:-2] in morphemes):
                # stripping two character suffix
                logger.debug(fragment[0:-2])
                count += 1
                continue

        if count / len(split) > score:
            score = count / len(split)
            if score == 0:
                score = 0.01
            score = score * pen
    return score


if __name__ == "__main__":
    print(get_acronym_score("CMP", "Cardiomyopathie", language="de") )