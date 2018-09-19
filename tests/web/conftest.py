import pytest
import json

from acres.util import functions


@pytest.fixture()
def mock_get_url(monkeypatch):
    """
    Monketpatch functions.get_url so that it returns a fake web response. Adapted from:
    https://www.angelaambroz.com/blog/posts/2018/Jan/24/a_few_of_my_favorite_pytest_things/
    Licensed under CC BY-SA 4.0

    :param monkeypatch:
    :return:
    """

    def mock_url(query, headers, params):
        class FakeResponse(object):
            def __init__(self):
                self.headers = ""
                self.text = '''{"webPages": {"value": [
                                    {
                                        "name": "Elektrokardiogramm \u2013 Wikipedia",
                                        "url": "",
                                        "language": "",
                                        "snippet": ""
                                    }
                                ]}}'''

            def json(self):
                return json.loads(self.text)
        return FakeResponse()
    monkeypatch.setattr(functions, "get_url", mock_url)