"""
Utility functions related to text processing.
"""
import nltk
import re
import string

from acres.constants import Constants
from acres.preprocess import resource_factory


nltk.download('punkt')


def diacritics() -> str:
    """
    TODO ... explain why

    :return: A string of diacritic characters
    """
    return "µÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ"


def fix_line_endings(long_text: str, char_ngram_length: int = 8,
                     line_break_marker_position: int = 3) -> str:
    """
    addresses the problem that many texts come with
           artificial line breaks. These breaks are removed if
           distributional data show that an unbroken continuation of
           the text is more likely than the break

    :param long_text:
    :param char_ngram_length:
    :param line_break_marker_position:
    :return:
    """
    char_ngram_dict = resource_factory.get_character_ngrams()

    line_break_marker = Constants.line_break

    out = ""
    long_text = long_text.strip().replace("\n", line_break_marker)
    i = 0
    while i + char_ngram_length < len(long_text):
        char = long_text[i]
        ngr = long_text[i:i + char_ngram_length]

        # line break marker at nth position
        if ngr[line_break_marker_position] == line_break_marker:
            ngr_clean = clear_digits(ngr, Constants.digit_marker)
            ngr_clean_space = ngr_clean.replace(line_break_marker, " ")
            if ngr_clean in char_ngram_dict:
                n_breaks = char_ngram_dict[ngr_clean]
            else:
                n_breaks = 0
            if ngr_clean_space in char_ngram_dict:
                n_spaces = char_ngram_dict[ngr_clean_space]
            else:
                n_spaces = 0
            # logger.debug("----")
            # logger.debug(ngr)
            # logger.debug("With new line: %s", n_breaks)
            # logger.debug("With space: %s", n_spaces)
            if n_spaces > n_breaks:
                # TODO: line_break_marker as delimiter
                # What happens if the break marker symbol also occurs in the original text
                # probably safe: using the "¶" character for line breaks
                # Check for whole code how delimiters are handled and how this
                # might interfere with text processing
                out = out + ngr.replace(line_break_marker, " ")
                i = i + char_ngram_length
                if i >= len(long_text):
                    break
            else:
                out = out + char
                i = i + 1
                if i == len(long_text):
                    break
        else:
            out = out + char
            i = i + 1
            if i == len(long_text):
                break

    out = out + long_text[i:] + line_break_marker
    return out


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


def transliterate_to_seven_bit(str_in: str) -> str:
    """
    Converts string to 7-bit ASCII, considering language - specific rules,
    such as in German "Ä" -> "AE", in English "Ä" -> "A"
    Considering in-built capitalization rules such as "ß" -> "SS"
    TODO: completing transliteration rules when non-Western languages are used
    consider using unidecode
    :param str_in:
    :return:
    """
    substitutions = {
        "À": "A",
        "Á": "A",
        "Â": "A",
        "Ã": "A",
        "Ä": "A",
        "Å": "A",
        "Æ": "AE",
        "Ç": "C",
        "È": "E",
        "É": "E",
        "Ê": "E",
        "Ë": "E",
        "Ì": "I",
        "Í": "I",
        "Î": "I",
        "Ï": "I",
        "Ñ": "N",
        "Ò": "O",
        "Ó": "O",
        "Ô": "O",
        "Õ": "O",
        "Ö": "O",
        "Ø": "O",
        "Ù": "U",
        "Ú": "U",
        "Û": "U",
        "Ü": "U"}

    if Constants.language == "de":
        substitutions["Ä"] = "AE"
        substitutions["Å"] = "AA"
        substitutions["Ö"] = "OE"
        substitutions["Ø"] = "OE"
        substitutions["Ü"] = "UE"

    return "".join([substitutions.get(c, c) for c in str_in.upper()])


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


def replace_punctuation(punctuated: str) -> str:
    """
    Replaces punctuation marks (as defined by pyhton string collection) by a whitespace.

    :param punctuated: Punctuated string.
    :return: A non-punctuated string.
    """
    _punctuation = set(string.punctuation)
    for punct in set(punctuated).intersection(_punctuation):
        punctuated = punctuated.replace(punct, ' ')
    return ' '.join(punctuated.split())


def context_ngram(words: str, size: int, reverse: bool = False) -> str:
    """
    Reduces a given sentence to `size` words, to be used as a context n-gram.

    If `reverse` is `True`, the last `size` words are used, commonly employed as a left context.

    :param words:
    :param size:
    :param reverse:
    :return:
    """
    tokens = words.split(" ")
    return " ".join(tokens[-size:]) if reverse else " ".join(tokens[:size])


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


def tokenize(text: str) -> str:
    """
    Tokenizes a given text.

    :param text:
    :return:
    """
    # XXX german-only
    return " ".join(nltk.word_tokenize(text, "german"))


def clean(text: str, preserve_linebreaks: bool = False) -> str:
    """
    Clean a given text to preserve only alphabetic characters, spaces, and, optionally, line breaks.

    :param text:
    :param preserve_linebreaks:
    :return:
    """
    allowed = [r'\w', r'\s']

    if preserve_linebreaks:
        allowed.append(Constants.line_break)

    disallowed_regex = "[^" + "".join(allowed) + "]"        # [^a-zA-Z\s¶Ð]

    return clean_whitespaces(re.sub(disallowed_regex, " ", text))
