"""
Rating submodule for full form checks.
"""
from acres.util import acronym as acro_util
from acres.util import functions


def _has_parenthesis(full: str) -> bool:
    """
    Check whether a given string contains parenthesis.

    :param full:
    :return:
    """
    if "(" in full or ")" in full:
        return True
    return False


def _is_full_too_short(full: str) -> bool:
    """
    Check whether a given full form is too short.

    @todo ignore whitespaces?

    :param full:
    :return:
    """
    too_short = 5
    if len(full) <= too_short:
        return True
    return False


def _starts_with_stopword(full: str) -> bool:
    """
    Check whether the full form starts with a stopword.

    :param full:
    :return:
    """
    if functions.is_stopword(full.split(' ', 1)[0]):
        return True
    return False


def _has_capitals(full: str) -> bool:
    """
    Check whether a string has at least one capital letter.

    :param full:
    :return:
    """
    if full.islower():
        return False
    return True


def _contain_acronym(full: str) -> bool:
    """

    :param full:
    :return:
    """
    words = full.split()
    for word in words:
        if acro_util.is_acronym(word):
            return True
    return False


def _compute_full_valid(full: str) -> int:
    """
    [For internal use only] Compute all checks on full forms.

    :param full:
    :return: An integer which binary forms indicates the failing test.
    """
    ret = 0
    if _has_parenthesis(full):
        ret += 1

    if _is_full_too_short(full):
        ret += 2

    if _starts_with_stopword(full):
        ret += 4

    # XXX german-only
    # A valid expansion of a german acronym would require at least one noun, which is capitalized.
    if not _has_capitals(full):
        ret += 8

    if _contain_acronym(full):
        ret += 16

    return ret


def is_full_valid(full: str) -> bool:
    """
    Check whether the full form is valid.

    :param full:
    :return:
    """
    return _compute_full_valid(full) == 0
