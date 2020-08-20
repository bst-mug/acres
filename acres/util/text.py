"""
Utility functions related to text processing.
"""
import re

from acres import constants


def clear_digits(str_in: str, substitute_char: str) -> str:
    """
    Substitutes all digits by a character (or string)

    Example: ClearDigits("Vitamin B12", "°"):

    TODO rewrite as regex

    :param str_in:
    :param substitute_char:
    """
    out = ""
    for character in str_in:
        if character in "0123456789":
            out = out + substitute_char
        else:
            out = out + character
    return out


def reduce_repeated_chars(str_in: str, char: str, remaining_chars: int) -> str:
    """
    :param str_in: text to be cleaned
    :param char: character that should not occur more than remaining_chars times in sequence
    :param remaining_chars: remaining_chars
    :return:
    """
    cnt = 0
    out = ""
    for k in str_in:
        if k == char:
            cnt += 1
            if cnt <= remaining_chars:
                out = out + k

        else:
            cnt = 0
            out = out + k
    return out


def remove_duplicated_whitespaces(whitespaced: str) -> str:
    """
    Clean up an input string out of any number of repeated whitespaces.

    :param whitespaced:
    :return:
    """
    cleaner = re.compile(r"\s+")
    return cleaner.sub(" ", whitespaced)


def clean_whitespaces(whitespaced: str) -> str:
    """
    Clean up an input string of repeating and trailing whitespaces.

    :param whitespaced:
    :return:
    """
    return remove_duplicated_whitespaces(whitespaced).strip()


def clean(text: str, preserve_linebreaks: bool = False) -> str:
    """
    Clean a given text to preserve only alphabetic characters, spaces, and, optionally, line breaks.

    :param text:
    :param preserve_linebreaks:
    :return:
    """
    allowed = [r'\w', r'\s']

    if preserve_linebreaks:
        allowed.append(constants.LINE_BREAK)

    disallowed_regex = "[^" + "".join(allowed) + "]"        # [^a-zA-Z\s¶Ð]

    return clean_whitespaces(re.sub(disallowed_regex, " ", text))
