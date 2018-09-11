from acres.web import base, azure, bing


def test_get_best_acronym_web_resolution(monkeypatch):
    # Monkey patch get_web_corpus so that tests do not depend on web results
    def mockreturn(query):
        return "Elektrokardiogramm – Wikipedia Das Elektrokardiogramm (EKG)"

    monkeypatch.setattr(azure, "get_web_corpus", mockreturn)
    monkeypatch.setattr(bing, "get_web_corpus", mockreturn)

    expected = ("Elektrokardiogramm", 2)
    actual = base.get_best_acronym_web_resolution("", "EKG", "", 3, 5)
    assert expected == actual
