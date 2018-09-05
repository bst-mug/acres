import pytest

from acres.web import azure

pytestmark = pytest.mark.skipif(not azure.__valid_key(),
                                reason="Place a valid BingSearchApiKey at config.ini")


def test_get_web_results():
    expected = "Elektrokardiogramm – Wikipedia"
    actual = azure.get_web_results("EKG")
    assert expected in [result.name for result in actual]
