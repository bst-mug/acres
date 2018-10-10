from acres.util import functions
from acres.util import acronym as acro_util


def _is_schwarzt_hearst_valid(acro: str, full: str) -> bool:
    """
    Check whether the full form length is within the bounds defined by Park/Roy and used by
    Schwarzt/Hearst.

    Park, Youngja, and Roy J. Byrd.
    "Hybrid text mining for finding abbreviations and their definitions."
    Proceedings of the 2001 conference on empirical methods in natural language processing. 2001.

    Schwartz, Ariel S., and Marti A. Hearst.
    "A simple algorithm for identifying abbreviation definitions in biomedical text."
    Biocomputing 2003. 2002. 451-462.

    :param acro:
    :param full:
    :return:
    """
    if len(full.split()) > min(len(acro) + 5, len(acro) * 2):
        return False
    return True


def _is_relative_length_valid(acro: str, full: str) -> bool:
    """
    Check whether the relative length of acronym to full form are within reasonable bounds.

    A full form can be up to 20 times longer than the acronym and the acronym has to be at most 60%
    of the full form.

    According to analysis of `acro_full_reference.txt` (modified from Wikipedia).

    @todo could be much greater then 5. Look for cases in which this is an issue

    :param acro:
    :param full:
    :return:
    """
    if 0.05 <= len(acro) / len(full) <= 0.6:
        return True
    return False


def _is_levenshtein_distance_too_high(acro: str, full: str) -> bool:
    """
    Check whether the Levenshtein distance between the given acronym and a generated one is too
    high.

    :param acro:
    :param full:
    :return:
    """
    distance = functions.levenshtein(acro.upper(), acro_util.create_german_acronym(full))
    if distance < len(acro):
        return False
    return True


def _is_possible_expansion(acro: str, full: str) -> bool:
    """
    Check whether all acronym characters are present in the full form.

    :param acro:
    :param full:
    :return:
    """
    # Empty acronym is presented everywhere
    if len(acro) == 0:
        return True

    # Non-empty acronym is not presented in empty full form
    if len(full) == 0:
        return False

    # First char must be the same
    if acro[0].lower() != full[0].lower():
        return False

    j = 0
    # We then skip the first char, as it has already been checked
    for i in range(1, len(acro)):
        j += 1
        while j < len(full):
            if acro[i].lower() == full[j].lower():
                break
            j += 1

    if j < len(full):
        return True

    return False


def _is_acronym_tail_on_last_word(acro: str, full: str) -> bool:
    """
    Check whether the acronym last character is present on the last word of the full form,
    but not at the end, unless it is a single letter.

    :param acro:
    :param full:
    :return:
    """
    # "EKG" = "Entwicklung" should not match
    # "Hepatitis A" -> "HEPA" should match
    last_word = full.lower().split()[-1]
    if len(last_word) == 1:
        if acro.lower()[-1] != last_word:
            # TODO avoid score=0 due to acronym-definition pairs
            # Rightmost acronym character is not equal rightmost single-char word
            return False
    else:
        if acro.lower()[-1] not in last_word[0:-1]:
            # Rightmost acronym character is not in rightmost word
            # TODO avoid score=0 due to acronym-definition pairs
            return False

    return True


def _compute_expansion_valid(acro: str, full: str) -> int:
    """
    [For internal use only] Compute all checks on expansions.

    :param acro:
    :param full:
    :return: An integer which binary forms indicates the failing test.
    """
    ret = 0

    if not _is_schwarzt_hearst_valid(acro, full):
        ret += 1

    if not _is_relative_length_valid(acro, full):
        ret += 2

    if _is_levenshtein_distance_too_high(acro, full):
        ret += 4

    if acro in full:
        ret += 8

    if not _is_possible_expansion(acro, full):
        ret += 16

    if not _is_acronym_tail_on_last_word(acro, full):
        ret += 32

    return ret


def is_expansion_valid(acro: str, full: str) -> bool:
    """
    Check whether an expansion is valid for a given acronym.

    :param acro:
    :param full:
    :return:
    """
    return _compute_expansion_valid(acro, full) == 0
