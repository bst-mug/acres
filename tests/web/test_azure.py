from acres.web import azure


def test_get_web_results():
    expected = "Elektrokardiogramm – Wikipedia"
    actual = azure.cached_get_web_results("EKG")
    assert expected in [result.name for result in actual]
