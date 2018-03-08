"""

Gets token ngram statistics from a website
Does some cleaning and then returns ngram list
in decreasing frequency

"""

import logging

import html2text
import requests

from acres import functions

# from acres.functions import import_proxy

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# logger.setLevel(logging.INFO)

# Enables logging for under the hood libraries
logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

NEWLINE = "¶"
NUMERIC = "Ð"


def ngrams_web_dump(url, min_num_tokens, max_num_tokens):
    """
    Produces an n gram statistics from a Web Query, parsing the first return page

    Should be used carefully, with delay.

    :param url:
    :param min_num_tokens:
    :param max_num_tokens:
    :return:
    """

    """
    proxy_config = functions.import_proxy()
    # FIXME  The whole proxy stuff desn't work
    
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
           response = requests.get(url, timeout=1, proxies=proxy_dict)
       else:
           response = requests.get(url, timeout=1)
    except requests.exceptions.RequestException as ex:
       logger.critical(ex)
       return []
    """

    response = requests.get(url, timeout=1)
    out_l = []
    txt = html2text.html2text(response.text)
    txt = txt.replace("**", "").replace("\n", " ").replace("[", "[ ").replace("]", " ]")
    # .replace("(", "( ").replace(")", " )")
    txt = txt.replace("„", "").replace('"', "").replace("'", "").replace(", ", " , ").replace(". ", " . ")
    out = ""
    logger.debug(txt)

    words = txt.split(" ")
    for word in words:
        if len(word) < 50:
            if not ('\\' in word or '/' in word or '&q=' in word):
                out = out + " " + word
    out = out.replace("  ", "\n").replace("[ ", "\n").replace(" ]", "\n")
    out = out.replace("|", "\n").replace("?", "\n").replace(":", "\n")
    logger.debug(out)

    output = functions.create_ngram_statistics(out, min_num_tokens, max_num_tokens)
    for ngram in output:
        out_l.append('{:0>4}'.format(output[ngram]) + "\t" + ngram)
    out_l.sort(reverse=True)
    logger.debug(out_l)

    return out_l


"""
if logger.getEffectiveLevel() == logging.DEBUG:
    ACRO = "AV"
    QUERY = "AV Blocks"
    import pickle
    from acres import functions
    from acres import resource_factory

    MORPHEMES = resource_factory.get_morphemes()
    # p = ngrams_web_dump("https://www.google.at/search?q=EKG+Herz", 1, 10)
    # p = ngrams_web_dump("http://www.bing.de/search?cc=de&q=ekg+Herz", 1, 10)
    p = ngrams_web_dump('http://www.bing.de/search?cc=de&q="' + QUERY + '"', 1, 10)
    # p = ngrams_web_dump('http://www.bing.de/search?cc=de&q=' + q , 1, 10)
    # f = open("c:\\Users\\schulz\\Nextcloud\\Terminology\\Corpora\\staging\\out.txt", 'wt')
    # f.write("\n".join(p))
    # f.close()
    # logger.debug(p)

    for line in p:
        full = line.split("\t")[1]
        cnt = line.split("\t")[0]
        s = rate_acronym_resolutions.get_acronym_score(ACRO, full, MORPHEMES)
        if s > 0.01:
            logger.debug(str(s * int(cnt)) + "\t" + line)
"""
