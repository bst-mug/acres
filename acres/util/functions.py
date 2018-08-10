# Stefan Schulz, 18 Mar 2017
"""
Module with functions for corpus analysis.

TODO move to proper function
This function compares and acronym with a potential full form and returns a list of segmentations.
"""
import logging
from logging.config import fileConfig

from acres.util.acronym import is_acronym

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import configparser
import os
from random import randint
from typing import Dict, List, Tuple

import requests


def import_conf(key):
    """

    :param key:
    :return:
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    #logger.debug(config.sections())
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
    logger.info("Creating ngram statistics...")

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


def robust_text_import_from_dir(path: str) -> List[str]:
    """
    Read the content of valid text files from a path into a list of strings.

    :param path: The path to look for documents.
    :return: A list of strings containing the content of each valid file.
    """
    logger.info("Loading documents from %s...", path)

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
            logger.warning("Corrupt file: %s", filename)
            continue
        except IOError as e:
            logger.warning("I/O error (%d) while reading %s: %s", e.errno, filename, e.strerror)
            continue

    return texts


def reduce_repeated_chars(str_in, char, n):
    """
    :param str_in: text to be cleaned
    :param char: character that should not occur more than n times in sequence
    :param remaining_chars: n
    :return:
    """
    prev = ""
    cnt = 0
    out = ""
    for c in str_in:
        if c == char:
            cnt += 1
            if cnt <= n:
                out = out + c

        else:
            cnt = 0
            out = out + c
    return out
