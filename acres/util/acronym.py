import logging
from logging.config import fileConfig

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from typing import Union, Tuple


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
