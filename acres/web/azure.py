"""
Module for querying the Bing Web Search API v7.
"""
import logging
import os.path
import pickle
from collections import namedtuple
from typing import List, Tuple, Dict, Any, Optional

import requests

from acres.util import functions

logger = logging.getLogger(__name__)

WebResult = namedtuple('WebResult', ['name', 'url', 'language', 'snippet'])

RESULTS_CACHE = {}  # type: Dict[str, List[WebResult]]


def get_web_corpus(query: str) -> str:
    """
    Generates a pseudo-corpus out of the web results for a given query.

    :param query:
    :return: A string containing all titles and snippets for 50 web results for the query.
    """
    web_results = cached_get_web_results(query)
    if not web_results:
        return ""

    output = []
    for result in web_results:
        output.append(result.name)
        output.append(result.snippet)
    return ' '.join(output)


def cached_get_web_results(query: str) -> Optional[List[WebResult]]:
    """
    Cached version of `get_web_results`.

    :param query:
    :return:
    """
    global RESULTS_CACHE

    if not RESULTS_CACHE:
        _load_cache()

    if query not in RESULTS_CACHE:
        web_results = get_web_results(query)
        RESULTS_CACHE[query] = web_results
        _persist_cache()

    return RESULTS_CACHE[query]


def _load_cache() -> None:
    global RESULTS_CACHE

    if os.path.isfile(_get_cache_name()):
        RESULTS_CACHE = pickle.load(open(_get_cache_name(), "rb"))


def _persist_cache() -> None:
    pickle.dump(RESULTS_CACHE, open(_get_cache_name(), "wb"))


def _get_cache_name() -> str:
    return "cache/azure.p"


def get_web_results(query: str) -> Optional[List[WebResult]]:
    """
    Queries Bing using a given term and returns a list of WebResults.

    If nothing is found, returns `None`.

    When possible, prefer cached_get_web_results, which uses a cache of results.

    :param query:
    :return:
    """

    headers, response = __query(query)
    logger.debug(headers)
    logger.debug(response)
    # logger.debug(json.dumps(response, indent=4))

    if "webPages" not in response:
        return None

    # 'id': 'https://api.cognitive.microsoft.com/api/v7/#WebPages.0',
    # 'name': 'Elektrokardiogramm – Wikipedia',
    # 'url': 'https://de.wikipedia.org/wiki/Elektrokardiogramm',
    # 'about': [{'name': 'Electrocardiography'}],
    # 'isFamilyFriendly': True,
    # 'displayUrl': 'https://de.wikipedia.org/wiki/Elektrokardiogramm',
    # 'snippet': 'Das Elektrokardiogramm (EKG) (zu altgriechisch καρδία kardía, deutsch ‚Herz‘, und
    # γράμμα grámma, deutsch ‚Geschriebenes‘) ist die Aufzeichnung ...',
    # 'dateLastCrawled': '2018-08-18T10:10:00.0000000Z',
    # 'language': 'de',
    # 'isNavigational': False
    results = []
    for value in response["webPages"]["value"]:
        web_result = WebResult(name=value['name'], url=value['url'], language=value['language'],
                               snippet=value['snippet'])
        results.append(web_result)

    return results


def __query(query: str) -> Tuple[Dict, Any]:
    """
    Queries Bing using a given term and returns a JSON representation of the results.
    Requires a valid `BingSearchApiKey` set on config.ini.

    :param query: A query term.
    :return: A tuple containining response headers and a JSON representation of the web results.
    """
    assert is_valid_key()
    subscription_key = functions.import_conf("BingSearchApiKey")

    logger.warning("Querying Bing... This API call will be charged.")

    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"

    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": query,
              "count": 50,  # max: 50
              "mkt": "de-AT",
              "responseFilter": "Webpages"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    return response.headers, response.json()


def is_valid_key() -> bool:
    """
    Checks if the Bing key is valid.

    :return:
    """
    key = functions.import_conf("BingSearchApiKey")
    return isinstance(key, str) and len(key) == 32
