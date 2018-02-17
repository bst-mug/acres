# Stefan Schulz 17 July 2017
"""
Finds synonyms using a n-gram frequency list from the Web
"""

import html2text
import requests
import logging

from acres import functions
from acres import rate_acronym_resolutions
from acres.functions import import_proxy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG) # Uncomment this to get debug messages

NEWLINE = "¶"
NUMERIC = "Ð"


def ngramsWebDump(url, minNumTokens, maxNumTokens):
    """
    Produces an n gram statistics from a Web Query, parsing the first return page

    Should be used carefully, with delay.

    :param url:
    :param minNumTokens:
    :param maxNumTokens:
    :return:
    """
    proxy_config = import_proxy()
    try:
        if proxy_config["UseProxy"] == "yes":
            http_proxy = proxy_config["ProxyUser"] + ":" + proxy_config["ProxyPass"] + "@" + proxy_config[
                "ProxyDomain"] + ":" + \
                         proxy_config["ProxyPort"]
            https_proxy = http_proxy
            ftp_proxy = http_proxy
            proxy_dict = {
                "http": http_proxy,
                "https": https_proxy,
                "ftp": ftp_proxy}
            response = requests.get(url, timeout=1, proxies=proxy_dict)
        else:
            response = requests.get(url, timeout=1)
    except requests.exceptions.RequestException as e:
        logger.critical(e)
        return []
    outL = []
    txt = html2text.html2text(response.text)
    txt = txt.replace("**", "").replace("\n", " ").replace("[", "[ ").replace("]",
                                                                              " ]")  # .replace("(", "( ").replace(")", " )")
    txt = txt.replace("„", "").replace('"', "").replace("'", "").replace(", ", " , ").replace(". ", " . ")
    out = ""
    # print(txt)
    words = txt.split(" ")
    for word in words:
        if len(word) < 50:
            if not ('\\' in word or '/' in word or '&q=' in word):
                out = out + " " + word
    out = out.replace("  ", "\n").replace("[ ", "\n").replace(" ]", "\n").replace("|", "\n").replace("?", "\n").replace(
        ":", "\n")
    output = functions.create_ngram_statistics(out, minNumTokens, maxNumTokens)
    for ngram in output:
        outL.append('{:0>4}'.format(output[ngram]) + "\t" + ngram)
    outL.sort(reverse=True)
    return outL


if logger.getEffectiveLevel() == logging.DEBUG:
    acro = "AV"
    q = "AV Blocks"
    import pickle

    m = pickle.load(open("pickle//morphemes.p", "rb"))
    # p = ngramsWebDump("https://www.google.at/search?q=EKG+Herz", 1, 10)
    # p = ngramsWebDump("http://www.bing.de/search?cc=de&q=ekg+Herz", 1, 10)
    p = ngramsWebDump('http://www.bing.de/search?cc=de&q="' + q + '"', 1, 10)
    # p = ngramsWebDump('http://www.bing.de/search?cc=de&q=' + q , 1, 10)
    # f = open("c:\\Users\\schulz\\Nextcloud\\Terminology\\Corpora\\staging\\out.txt", 'wt')
    # f.write("\n".join(p))
    # f.close()
    # print(p)

    for line in p:
        full = line.split("\t")[1]
        cnt = line.split("\t")[0]
        s = rate_acronym_resolutions.GetAcronymScore(acro, full, m)
        if s > 0.01:
            logger.debug(str(s * int(cnt)) + "\t" + line)
