"""
Utility functions related to acronyms.
"""
import logging
import re
from collections import namedtuple
from typing import Tuple, List, Optional

from acres import constants
from acres.util import text

logger = logging.getLogger(__name__)

Acronym = namedtuple('Acronym', ['acronym', 'left_context', 'right_context'])


def is_acronym(str_probe: str, max_length: int = 7) -> bool:
    """
    Identifies Acronyms, restricted by absolute length
    XXX look for "authoritative" definitions for acronyms

    :param str_probe:
    :param max_length:
    :return:
    """
    ret = False
    replaced_probe = str_probe.replace(constants.DIGIT_MARKER, "0")
    lower = 0
    upper = 0
    if len(replaced_probe) <= max_length:
        for char in replaced_probe:
            if char.isupper():
                upper = upper + 1
            if char.islower():
                lower = lower + 1
    if upper > 1 and upper > lower:
        ret = True
    return ret


def create_german_acronym(full: str) -> str:
    """
    Creates an acronym out of a given multi-word expression.

    @todo Use is_stopword?

    :param full: A full form containing whitespaces.
    :return:
    """
    out = ""
    neg_list = ("and", "auf", "bei", "bei", "beim", "by", "der", "des", "die", "et", "for", "für",
                "gegen", "im", "in", "mit", "nach", "not", "of", "on", "than", "the", "to", "und",
                "vom", "von", "vor", "with", "zum", "zur")
    full = text.clean_whitespaces(full.replace("-", " ").replace("/", " "))
    for word in full.split():
        if word not in neg_list:
            out = out + word[0].upper()
    return out


def trim_plural(acronym: str) -> str:
    """
    Trim the german plural form out of an acronym.

    @todo rewrite as regex

    :param acronym:
    :return:
    """
    # Do not trim two-chars acronyms, as this would lead to a single-char (and invalid) acronym.
    if len(acronym) <= 2:
        return acronym

    acronym_plurals = ["s", "S", "x", "X"]

    singular_acronym = acronym
    if acronym[-1] in acronym_plurals:
        singular_acronym = acronym[0:-1]
    return singular_acronym
