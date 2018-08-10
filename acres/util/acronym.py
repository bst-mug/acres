import logging
import re
from logging.config import fileConfig

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from typing import Union, Tuple, List


def extract_acronym_definition(str_probe: str, max_length: int) -> Union[None, Tuple[str, str]]:
    """
    Identifies potential acronym / definition pairs and extract acronym and definition candidates.

    :param str_probe:
    :param max_length:
    :return:
    """
    str_probe = str_probe.strip()
    if len(str_probe) > 1:
        if str_probe[-1] == ")" and str_probe.count("(") == 1:
            left = str_probe.split("(")[0].strip()  # potential definition
            right = str_probe.split("(")[1][0:-1].strip()  # potential acronym
            if is_acronym(left, max_length, "Ð") and not is_acronym(right, max_length, "Ð"):
                return left, right
            if is_acronym(right, max_length, "Ð") and not is_acronym(left, max_length, "Ð"):
                return right, left

    return None


def is_acronym(str_probe: str, max_length: int = 7, digit_placeholder="Ð") -> bool:
    """
    Identifies Acronyms, restricted by absolute length
    "Ð" as default placeholder for digits. (e.g. "Ð")
    XXX look for "authoritative" definitions for acronyms

    :param str_probe:
    :param max_length:
    :param digit_placeholder:
    :return:
    """
    if len(digit_placeholder) > 1:
        logger.error("Digit placeholders must be empty or a single character")
        return False

    ret = False
    replaced_probe = str_probe.replace(digit_placeholder, "0")
    lower = 0
    upper = 0
    if len(replaced_probe) <= max_length:
        for c in replaced_probe:
            if c.isupper():
                upper = upper + 1
            if c.islower():
                lower = lower + 1
    if upper > 1 and upper > lower:
        ret = True
    return ret


def find_acro_expansions(lst_n_gram_stat: List[str]) -> List[str]:
    """
    Identifies acronyms and looks for possible expansions.
    Takes the most frequent one.
    Uses ngrams with the second token_not_acronym being an acronym.

    TODO: check for what it is needed, complete it

    :param lst_n_gram_stat: A list in which ngrams extracted
    from a corpus are counted in decreasing frequency

    :return:
    """
    letter = ""
    count_per_ngram = {}
    acronyms = []
    non_acronyms = []
    is_acro = False
    # TODO: check initialization

    ret = []

    for line in lst_n_gram_stat:
        ngram = line.split("\t")[1]
        count = line.split("\t")[0]
        count_per_ngram[ngram] = count
        if " " in ngram:  # has at least 2 tokens
            other_tokens = ngram.split(" ")[1:]
            if len(other_tokens) > 2:
                if is_acronym(other_tokens[1], 7):
                    acronyms.append(ngram)
                else:
                    for word in ngram.split(" "):
                        is_acro = False
                        if len(word) > 1:
                            # XXX Should call is_acronym()?
                            if word[1].isupper() or not word.isalpha():
                                is_acro = True
                                break
                    if not is_acro:
                        non_acronyms.append(ngram)

    for token_acronym in acronyms:
        counter = 0
        end = " ".join(token_acronym.split(" ")[1:])
        regex = "^"
        for letter in end:
            # regex = regex + letter.upper() + ".*\s" # space required
            regex = regex + letter.upper() + ".*"  # no space required

        for token_not_acronym in non_acronyms:
            end_n = " ".join(token_not_acronym.split(" ")[1:])
            last_n = " ".join(token_not_acronym.split(" ")[-1])

            first_condition = token_not_acronym.split(" ")[0] == token_acronym.split(" ")[0]
            second_condition = token_not_acronym.split(" ")[1].upper() == token_acronym.split(" ")[
                1].upper()
            if first_condition and not second_condition:
                if re.search(regex, end_n.upper()):
                    if letter.upper() in last_n.upper():
                        stat = token_acronym + count_per_ngram[
                            token_acronym] + "     " + token_not_acronym + count_per_ngram[
                                   token_not_acronym]
                        logger.debug(stat)
                        ret.append(stat)
                        counter += 1
                        if counter > 4:
                            break

    return ret
