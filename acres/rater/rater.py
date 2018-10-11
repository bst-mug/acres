"""
Rating main module.
"""

import logging
from typing import Tuple

from acres.rater import expansion
from acres.rater import full as full_rater
from acres.util import acronym as acro_util
from acres.util import variants as varianter

logger = logging.getLogger(__name__)


def _is_short_form(acro: str, full: str) -> bool:
    """
    Check whether a given expansion is shorter than the acronym.

    :param acro:
    :param full:
    :return:
    """
    if len(full.split()) < len(acro):
        return True
    return False


def _calc_score(acro: str, full: str) -> float:
    """
    Calculates a score for the given expansion.

    TODO all scoring/penalization is pure heuristics. Check with examples.
    TODO evaluate scoring higher shorter valid expansions.

    :param acro:
    :param full:
    :return:
    """
    score = 1.0

    # rightmost expansion should start with upper case initial
    # XXX german-only
    if full.split(" ")[-1][0].islower():
        score = score * 0.25

    # exact match of real acronym with generated acronym
    # XXX german-only
    if acro.upper() == acro_util.create_german_acronym(full):
        score = score * 2

    # if short full form, the coincidence of the first two letters of full and acronym
    # increases score
    if _is_short_form(acro, full):
        if full.upper()[0:2] == acro.upper()[0:2]:
            score = score * 2

    # decapitalized acronym should not occur within decap full form,
    # if acronym has three or more letters
    if acro.lower() in full.lower():
        score = score * 0.2

    return score


def get_acronym_score(acro: str, full: str) -> float:
    """
    Scores acronym/resolution pairs according to a series of well-formedness criteria.

    This scoring function should be used only for cleaned and normalized full forms.

    For forms that may contain acronym-definition pairs, see `get_acronym_definition_pair_score`.
    For forms that should be checked for variants, see `get_acronym_score_variants`.

    TODO Consider again morphosaurus checks.

    :param acro: Acronym to be expanded.
    :param full: Long form to be checked whether it qualifies as an acronym expansion.
    :return: score that rates the likelihood that the full form is a valid expansion of the acronym.
    """
    acro = acro.strip()
    full = full.strip()

    # XXX german-only
    # Plural form of acronym reduced to singular ("s", often not found in non English full
    # forms) e.g. "EKGs", "EKGS", "NTx", "NTX" (Nierentransplantation).
    # These characters cannot be always expected to occur in the full form
    # We assume that plurals and genitives of acronyms are often marked with
    # "s", however not necessarily lower case.
    # This means that "S" and "X" are not required to match
    acro = acro_util.trim_plural(acro)

    # acronym must have at least two characters: all those expressions like "Streptococcus B" or
    # "Vitamin C" should not be considered containg acronyms.
    # Normally these compositions are lexicalised.
    # May be relevant for assessing single letter forms like "A cerebralis"
    if not acro_util.is_acronym(acro):
        return 0

    if not full_rater.is_full_valid(full):
        return 0

    if not expansion.is_expansion_valid(acro, full):
        # TODO avoid score=0 due to acronym-definition pairs
        return 0

    return _calc_score(acro, full)


def get_acronym_score_variants(acro: str, full: str) -> float:
    """
    Wrapper for `get_acronym_score` that takes variants into consideration.

    For checking for valid German expansions it is important to consider variants,
    therefore invoke spelling variant generator from `varianter.generate_all_variants_by_rules`.
    At this place more rules can be added.

    Typical substitutions, mostly concerning the inconsistent use of k, c, and z in clinical texts
    can be enhanced by frequent translations in `varianter.generate_all_variants_by_rules`.

    Return the score of the best variant.

    :param acro:
    :param full:
    :return:
    """
    max_score = 0.0
    variants = varianter.generate_all_variants_by_rules(full)
    for variant in variants:
        max_score = max(max_score, get_acronym_score(acro, variant))
    return max_score


def get_acro_def_pair_score(acro: str, full: str) -> Tuple[str, float]:
    """
    Wrapper function for `get_acronym_score` that takes possible acronym-definition pairs into
    account.

    The scoring function should work both for acronyms extracted from a corpus (for which strict
    matching criteria should be applied) and for acronyms harvested from the Web for which the
    criteria may be relaxed once strong evidence from acronym - definition patterns exist, e.g.
    "ARDS (akutes Atemnotsyndrom)".
    There might be acronym - definition patterns in well-written clinical documents.

    In the latter case, full would take this form, i.e. a string that contains both the acronym and
    the expansion.

    :param acro:
    :param full:
    :return:
    """
    is_acronym_definition_pair = False
    definition = full

    # full form contains an acronym definition pattern (normally only yielded
    # from Web scraping, unlikely in clinical texts)
    # acronym is included; is then removed from full form
    acro_def_pattern = acro_util.extract_acronym_definition(full, 7)
    if acro_def_pattern is not None:
        is_acronym_definition_pair = True
        if acro_def_pattern[0] == acro:
            definition = acro_def_pattern[1]
            # high score, but also might be something else

    # XXX Maybe we shouldn't consider variants in case it's an acronym-definition pair
    score = get_acronym_score_variants(acro, definition)
    if is_acronym_definition_pair:
        score *= 10
    return definition, score
