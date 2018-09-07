from acres.web import azure


def test_get_web_corpus():
    expected = ""
    actual = azure.get_web_corpus("akjkjgehwvmewm")
    assert expected == actual


def test_get_web_results():
    expected = "Elektrokardiogramm – Wikipedia"
    actual = azure.cached_get_web_results("EKG")
    assert expected in [result.name for result in actual]

    # Queries without valid results must not fail
    expected = None
    actual = azure.cached_get_web_results("akjkjgehwvmewm")
    assert expected == actual
