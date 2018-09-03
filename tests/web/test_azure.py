import pytest

from acres.web import azure

pytestmark = pytest.mark.skipif(not azure.__valid_key(),
                                reason="Place a valid BingSearchApiKey at config.ini")


def test_get_title_snippets():
    expected = "Elektrokardiogramm – Wikipedia"
    actual = azure.get_title_snippets("EKG")
    assert expected in [k for (k, v) in actual]
