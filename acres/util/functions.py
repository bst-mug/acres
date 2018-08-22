# Stefan Schulz, 18 Mar 2017
"""
Module with functions for corpus analysis.

TODO move to proper function
This function compares and acronym with a potential full form and returns a list of segmentations.
"""
import configparser
import logging
import os
from random import randint
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)


def import_conf(key):
    """

    :param key:
    :return:
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    #logger.debug(config.sections())
    return config['DEFAULT'][key]


def get_url(url, timeout=2):
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
        if line == '':
            continue
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

    # Make models consistent among different filesystems
    files.sort()

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


