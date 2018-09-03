import logging
from typing import List, Tuple, Dict, Any

import requests

from acres.util import functions

logger = logging.getLogger(__name__)


def get_title_snippets(query: str) -> List[Tuple[str, str]]:
    """
    Queries Bing using a given term and returns a list of tuples with titles and snippets.

    :param query:
    :return:
    """
    headers, response = __query(query)
    # logger.debug(headers)
    # logger.debug(json.dumps(response, indent=4))

    titles_snippets = []
    for value in response["webPages"]["value"]:
        result = (value["name"], value["snippet"])
        titles_snippets.append(result)

    return titles_snippets


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
              "textDecorations": True,
              "textFormat": "HTML"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    return response.headers, response.json()


def __valid_key() -> bool:
    """
    Checks if the Bing key is valid.

    :return:
    """
    return len(functions.import_conf("BingSearchApiKey")) == 32
