from acres.web import azure

# TODO use fixture for tests instead of committed azure.p


def test_get_web_corpus():
    expected = ""
    actual = azure.get_web_corpus("akjkjgehwvmewm")
    assert expected == actual

    expected = "Elektrokardiogramm"
    actual = azure.get_web_corpus("EKG")
    assert expected in actual


def test_cached_get_web_results():
    expected = "Elektrokardiogramm – Wikipedia"
    actual = azure.cached_get_web_results("EKG")
    assert expected in [result.name for result in actual]

    # Queries without valid results must not fail
    expected = None
    actual = azure.cached_get_web_results("akjkjgehwvmewm")
    assert expected == actual


def test_get_web_results(monkeypatch, mock_get_url):
    # Monkey patch is_valid_key so that it's always valid
    def valid_key():
        return True
    monkeypatch.setattr(azure, "is_valid_key", valid_key)

    expected = "Elektrokardiogramm – Wikipedia"
    actual = azure.get_web_results("EKG")
    assert expected in [result.name for result in actual]
