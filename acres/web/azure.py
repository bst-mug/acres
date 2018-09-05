import logging
from collections import namedtuple
from typing import List, Tuple, Dict, Any

import requests

from acres.util import functions

logger = logging.getLogger(__name__)

WebResult = namedtuple('WebResult', ['name', 'url', 'language', 'snippet'])


def get_web_results(query: str) -> List[WebResult]:
    """
    Queries Bing using a given term and returns a list of WebResults.

    :param query:
    :return:
    """
    headers, response = __query(query)
    logger.debug(headers)
    logger.debug(response)
    # logger.debug(json.dumps(response, indent=4))

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
    assert __valid_key()
    subscription_key = functions.import_conf("BingSearchApiKey")

    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"

    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": query,
              "count": 10,  # max: 50
              "mkt": "de-AT",
              "responseFilter": "Webpages"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    return response.headers, response.json()


def __valid_key() -> bool:
    """
    Checks if the Bing key is valid.

    :return:
    """
    return len(functions.import_conf("BingSearchApiKey")) == 32
