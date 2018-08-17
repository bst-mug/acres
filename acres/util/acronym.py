import logging
import re
from typing import Union, Tuple, List

from acres.util import text

logger = logging.getLogger(__name__)


def extract_acronym_definition(str_probe: str, max_length: int, strict=False) -> Union[None, Tuple[str, str]]:
    """
    Identifies potential acronym / definition pairs and extract acronym and definition candidates.
    A necessary criterion is that the initial characters are the same
    TODO: Acronym / definition pairs normally use parentheses, but also quotes and dashes can be found

    :param str_probe:
    :param max_length:
    :return:
    """
    str_probe = str_probe.strip()

    if len(str_probe) > 6:
        if str_probe[-1] == ")" and str_probe.count("(") == 1:
            left = str_probe.split("(")[0].strip()  # potential definition
            right = str_probe.split("(")[1][0:-1].strip()  # potential acronym
            if strict:
                if left[0].lower() != right[0].lower():
                    return None
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


def is_proper_word(str_probe: str, digit_placeholder="Ð") -> bool:
    # a proper word is more than a single letter.
    # the first character may be capitalised or nor,
    # all other characters are lower case
    # It must not include digits or punctuation characters
    # Only dashes are allowed
    str_new = str_probe.replace("-", "").replace(digit_placeholder, "1")
    if len(str_new) < 2:
        return False
    if not (str_probe[0].isalpha() and str_probe[-1].isalpha() and str_new.isalpha()):
        return False
    if not str_new[1:].islower():
        return False
    return True





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


def split_expansion(acro: str, full: str) -> List[Tuple[str, ...]]:
    """

    :param acro:
    :param full:
    :return:
    """
    dia = text.diacritics()
    bina = []
    cleaned_full = _acronym_aware_clean_expansion(acro, full)

    # TODO recursive function instead of Regex

    # TODO obvious morpheme-based scoring does not work well with this unorthodox building patterns

    # List of binary combinations of alternative regex patterns (greedy vs. non-greedy)
    regs = []

    # Iterate over the binary representations of `i`, with "0" being replaced by the greedy
    # regex "*|", and "1" by the non-greedy regex "*?|". The pipe | character is just a separator,
    # later used as a split character.
    for i in range(0, (2 ** (len(acro) - 1))):
        # Takes the binary value of i and fills it with zeroes up to the length of acronym -1
        str_bin = str(bin(i))[2:].zfill(len(acro) - 1)

        # zfill will not drop characters. In the corner case of a single letter acronym, we should
        # generate an empty string.
        if len(acro) == 1:
            str_bin = ""

        bina.append(str_bin.replace("0", "*|").replace("1", "*?|"))

    # Iterate over the built list of expressions, each matching the initial characters in a
    # different way. Then build a list of regular expressions, e.g. for "EKG":
    # ^(E.*)(K.*)(G[A-Za-z0-9 ]*$)
    # ^(E.*)(K.*?)(G[A-Za-z0-9 ]*$)
    # ^(E.*?)(K.*)(G[A-Za-z0-9 ]*$)
    # ^(E.*?)(K.*?)(G[A-Za-z0-9 ]*$)
    for expr in bina:
        lst_exp = expr.split("|")
        z = 0

        # Build capturing groups over each acronym character
        out = "^("
        for ex in lst_exp:
            out = out + re.escape(acro[z]) + "." + ex + ")("
            z += 1

        # TODO Use Unicode matching instead of diacritics
        # TODO Merge greedy and non-greedy in a single non-capturing group?
        # Remove the last 3 remaining characters --- always ".)(" (because last `ex` is empty) ---
        # and replace them with a group matching valid characters (alphanumeric + whitespace +
        # diacritics).
        regs.append(out[0:-3] + "[A-Za-z" + dia + "0-9 ]*$)")

    result = []  # type: List[Tuple[str, ...]]
    for reg in regs:
        if re.search(reg, cleaned_full, re.IGNORECASE) is not None:
            found = re.findall(reg, cleaned_full, re.IGNORECASE)[0]

            # Avoid duplicates
            if found not in result:
                result.append(found)
    return result


def _acronym_aware_clean_expansion(acronym: str, expansion: str) -> str:
    """
    Remove any symbol from the expanded form, preserving hyphens, spaces and chars from the acronym.

    :param acronym:
    :param expansion:
    :return:
    """
    ret = ""
    for c in expansion:
        if c.isalnum() or c in " -" or c in acronym:
            ret = ret + c
        else:
            ret = ret + " "
    return ret.strip()


def is_valid_expansion(acronym: str, expansion: str) -> bool:
    """
    Checks whether a candidate expansion is valid for an acronym.

    :param acronym:
    :param expansion:
    :return:
    """
    return len(split_expansion(acronym, expansion)) > 0


def split_ngram(ngram: str) -> List[Tuple[str, str, str]]:
    """
    Splits a token ngram with acronym(s) into all combinations of left - acro - token.

    :param ngram:
    :return:
    """
    out = []
    tokens = ngram.split(" ")
    counter = 0
    for token in tokens:
        if is_acronym(token, 7, "Ð"):
            tr = (" ".join(tokens[0:counter]),
                  tokens[counter], " ".join(tokens[counter + 1:]))
            out.append(tr)
        counter += 1
    return out
