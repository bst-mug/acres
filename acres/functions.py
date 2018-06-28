# Stefan Schulz, 18 Mar 2017
"""
Module with functions for corpus analysis.

TODO move to proper function
This function compares and acronym with a potential full form and returns a list of segmentations.
"""

import configparser
import logging
import os
import re
from random import randint
from typing import Dict, List, Tuple, Union

import requests

from acres.preprocess import resource_factory

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def import_conf(key):
    """

    :param key:
    :return:
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    logger.debug(config.sections())
    return config['DEFAULT'][key]


def get_url(url, timeout=1):
    """
    Make a HTTP request to a given URL using proxy if necessary.

    :param url: The URL to make the request to.
    :param timeout: The timeout in seconds.
    :return: Object from requests.get()
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    proxy_config = config["proxy"]

    try:
        if proxy_config["UseProxy"] == "yes":
            http_proxy = proxy_config["ProxyUser"] + ":" + proxy_config["ProxyPass"] + \
                         "@" + proxy_config["ProxyDomain"] + ":" + proxy_config["ProxyPort"]
            https_proxy = http_proxy
            ftp_proxy = http_proxy
            proxy_dict = {
                "http": http_proxy,
                "https": https_proxy,
                "ftp": ftp_proxy}
            return requests.get(url, timeout=timeout, proxies=proxy_dict)
        else:
            return requests.get(url, timeout=timeout)
    except requests.exceptions.RequestException as ex:
        logger.critical(ex)
        return []


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


def fix_line_endings(
        long_text: str,
        line_break_marker="¶",
        char_ngram_length=8,
        line_break_marker_position=3) -> str:
    """
    addresses the problem that many texts come with
           artificial line breaks. These breaks are removed if
           distributional data show that an unbroken continuation of
           the text is more likely than the break
    :param long_text:
    :param line_break_marker:
    :param char_ngram_length:
    :param line_break_marker_position:
    :return:
    """
    char_ngram_dict = resource_factory.get_character_ngrams()
    # TODO line above commented out because problem with loading config file
    # TODO absolute path set because otherwise not found
    # import pickle
    # PICKLE_FOLDER = "C:\\Users\\SchulzS\\PycharmProjects\\acres\\models\\pickle\\"
    # char_ngram_dict = pickle.load(open(PICKLE_FOLDER + "character_ngrams.p", "rb"))

    out = ""
    long_text = long_text.strip().replace("\n", line_break_marker)
    i = 0
    while i + char_ngram_length < len(long_text):
        char = long_text[i]
        ngr = long_text[i:i + char_ngram_length]

        # line break marker at nth position
        if ngr[line_break_marker_position] == line_break_marker:
            ngr_clean = clear_digits(ngr, "°")
            ngr_clean_space = ngr_clean.replace(line_break_marker, " ")
            if ngr_clean in char_ngram_dict:
                n_breaks = char_ngram_dict[ngr_clean]
            else:
                n_breaks = 0
            if ngr_clean_space in char_ngram_dict:
                n_spaces = char_ngram_dict[ngr_clean_space]
            else:
                n_spaces = 0
            # TODO: implement logging
            logger.debug("----")
            logger.debug(ngr)
            logger.debug("With new line: %s", n_breaks)
            logger.debug("With space: %s", n_spaces)
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
    return out.replace(line_break_marker, line_break_marker + "\n")


# for all training files
# added " <EOL>" for end of line and substituted digits by "Ð"


def clear_digits(str_in: str, substitute_char: str) -> str:
    """
       substitutes all digits by a character (or string)

       Example: ClearDigits("Vitamin B12", "°"):

       :param str_in:
       :param substitute_char:

       """
    out = ""
    for c in str_in:
        if c in "0123456789":
            out = out + substitute_char
        else:
            out = out + c
    return out


def create_ngram_statistics(input_string: str, n_min: int, n_max: int) -> Dict[str, int]:
    """
    Creates a dictionary that counts each nGram in an input string. Delimiters are spaces.

    Example: bigrams and trigrams
    nMin = 2 ,   nMax = 3
    PROBE: # print(WordNgramStat('a ab aa a a a ba ddd', 1, 4))

    :param input_string:
    :param n_min:
    :param n_max:
    :return:
    """
    output = {}  # type: Dict[str, int]
    lines = input_string.splitlines()
    for line in lines:
        line = line.replace('\r', '')
        line = line.replace('\n', '')
        line = line.strip()
        cleaned_line = line.split(" ")
        for n in range(n_min, n_max + 1):
            for i in range(len(cleaned_line) - n + 1):
                g = ' '.join(cleaned_line[i:i + n])
                output.setdefault(g, 0)
                output[g] += 1
    #    Example for formatted output, sorted, reverse order
    #    for w in sorted(output, key=output.get, reverse = True):
    #       print ('{:>8}'.format(output[w]) + '\t' + w)
    return output


def transliterate_to_seven_bit(str_in: str, language="de") -> str:
    """
    Converts string to 7-bit ASCII, considering language - specific rules,
    such as in German "Ä" -> "AE", in English "Ä" -> "A"
    Considering in-built capitalization rules such as "ß" -> "SS"
    TODO: completing transliteration rules when non-Western languages are used
    consider using unidecode
    :param str_in:
    :param language: the language for which rules are defined (ISO_639-1)
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

    if language == "de":
        substitutions["Ä"] = "AE"
        substitutions["Å"] = "AA"
        substitutions["Ö"] = "OE"
        substitutions["Ø"] = "OE"
        substitutions["Ü"] = "UE"

    return "".join([substitutions.get(c, c) for c in str_in.upper()])


def substitute_c_and_ph_by_context(str_in, language="de"):
    """
    Applies normalization rules that improves retrieval of
    clinical terms. This function transforms an English / Latin spelling
    pattern by a German one
    Also maps to 7bit chars

    :param str_in:
    :param language: the language for which rules are defined (ISO_639-1)
    :return:
    """
    # no Acronym
    if language == "de":
        if len(str_in) == 1:
            return str_in.isupper()
        if len(str_in) == 2 and str_in[1].isupper():
            return str_in
        if str_in[2].isupper():
            return str_in
        str_in = transliterate_to_seven_bit(str_in)
        return str_in.replace("CAE", "ZAE").replace("COE", "ZOE"). \
            replace("CA", "KA").replace("CO", "KO"). \
            replace("CU", "KU").replace("CE", "ZE").replace("CI", "ZI"). \
            replace("CY", "ZY").replace("PH", "F")


def substitute_k_and_f_and_z_by_context(str_in, language="de"):
    """
    Applies normalization rules that improves retrieval of
    clinical terms. This function transforms a German spelling
    pattern by a English / Latin one.
    Also maps to 7bit chars and upper case everything.
    Input should be a single token.

    @todo Enforce it's a single token

    :param str_in:
    :param language: the language for which rules are defined (ISO_639-1)
    :return:
    """
    # no Acronym
    if language == "de":
        if len(str_in) == 1:
            return str_in.upper()

        # Check for acronym
        # TODO Use is_acronym
        if len(str_in) == 2 and str_in[1].isupper():
            return str_in
        if str_in[2].isupper():
            return str_in

        str_in = transliterate_to_seven_bit(str_in)
        return str_in.replace("ZAE", "CAE").replace("ZOE", "COE"). \
            replace("ZI", "CI").replace("ZE", "CE"). \
            replace("KA", "CA").replace("KO", "CO").replace("KU", "CU"). \
            replace("ZY", "CY").replace("F", "PH")


def is_acronym(str_probe: str, max_length: int =7, digit_placeholder="Ð") -> bool:
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


def simplify_german_string(str_in_german: str) -> str:
    """
    Decapitalises, substitutes umlauts, sharp s and converts k and z to c

    TODO ... explain why

    :param str_in_german:
    :return:
    """
    str_in_german = str_in_german.lower()
    str_in_german = str_in_german.replace(
        "k", "c").replace("z", "c").replace("ß", "ss")
    str_in_german = str_in_german.replace("é", "e").replace("à", "a")
    return str_in_german.replace("ä", "ae").replace(
        "ö", "oe").replace("ü", "ue")


def diacritics() -> str:
    """
    TODO ... explain why

    :return: A string of diacritic characters
    """
    return "µÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ"


def random_sub_list(in_list: list, max_num: int) -> list:
    """
    Generates random sublist.

    :param in_list:
    :param max_num:
    :return:
    """
    lst_out = []
    length = len(in_list)
    if length <= max_num:
        return in_list
    counter = 0
    rnumbers = []   # type: List[int]
    while counter < max_num:
        rnumber = (randint(0, length - 1))
        if rnumber not in rnumbers:
            rnumbers.append(rnumber)
            counter = len(rnumbers)
    for rnumber in rnumbers:
        lst_out.append(in_list[rnumber])
    return lst_out


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
    return len(check_acro_vs_expansion(acronym, expansion)) > 0


def check_acro_vs_expansion(acro: str, full: str) -> List[Tuple[str, ...]]:
    """

    :param acro:
    :param full:
    :return:
    """
    dia = diacritics()
    bina = []
    cleaned_full = _acronym_aware_clean_expansion(acro, full)

    # list of binary combinations of
    # alternative regex patterns
    # (greedy vs. non-greedy)
    # XXX: state machines instead of Regex
    # XXX: debug what happens with "TRINS" - "Trikuspidalinsuffizienz"
    # XXX: correct segmentation: 't', 'ricuspidal', 'i', 'n', 'suffizienz'
    # XXX: obvious morpheme-based scoring does not work well
    # XXX with this unorthodox building patterns
    regs = []  # list of alternative regular expressions
    for i in range(0, (2 ** (len(acro) - 1))):
        str_bin = str(bin(i))[2:].zfill(len(acro) - 1)
        bina.append(str_bin.replace("0", "*|").replace("1", "*?|"))
    for expr in bina:
        lst_exp = expr.split("|")
        z = 0
        out = "^("
        for ex in lst_exp:
            out = out + re.escape(acro[z]) + "." + ex + ")("
            z += 1
        regs.append(out[0:-3] + "[A-Za-z" + dia + "0-9 ]*$)")
        # List of all regular expressions
        # logger.debug(regs)
        # logger.debug(cleaned_full)

    result = []
    for reg in regs:
        if re.search(reg, cleaned_full, re.IGNORECASE) is not None:
            found = re.findall(reg, cleaned_full, re.IGNORECASE)[0]

            # Avoid duplicates
            result.append(found) if found not in result else 0
    return result


# Probes
# logger.debug(import_conf("NGRAMFILE"))
# logger.debug(CheckAcroVsFull("KHK", "koronare Herzkrankheit"))
# logger.debug(extractAcroDef("EKG (Elektrokardiogramm)", 7))
# logger.debug(extractAcroDef("Elektrokardiogramm", 7))
# logger.debug(extractAcroDef("Elektrokardiogramm (EKG)", 7))

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


def robust_text_import_from_dir(path: str) -> List[str]:
    """
    Read the content of valid text files from a path into a list of strings.

    :param path: The path to look for documents.
    :return: A list of strings containing the content of each valid file.
    """
    texts = []
    # print(path)
    files = os.listdir(path)
    for filename in files:
        try:
            with open(path + "/" + filename, "r", encoding="utf-8") as file:
                content = file.read()
                texts.append(content)
                # print(file + " " + str(len(content)))
        except UnicodeDecodeError:
            logger.debug("corrupt file: %s", filename)
            continue
        except IOError as e:
            logger.debug("I/O error (%d) while reading %s: %s", e.errno, filename, e.strerror)
            continue

    return texts

# p = import_conf("SAMPLEPATH")
# lst_texts = robust_text_import_from_dir(p)

