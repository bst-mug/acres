from acres.web import base, azure, bing


def test_get_best_acronym_web_resolution(monkeypatch):
    # Monkey patch get_web_corpus so that tests do not depend on web results
    def mockreturn(query):
        if query == "EKG":
            return "Elektrokardiogramm – Wikipedia Das Elektrokardiogramm (EKG)"
        if query == "EKG ccc ddd bbb eee aaa":
            return "Elektrokardiogramm Elektrokardiogramm Elektrokardiogramm"

    monkeypatch.setattr(azure, "get_web_corpus", mockreturn)
    monkeypatch.setattr(bing, "get_web_corpus", mockreturn)

    expected = ("Elektrokardiogramm", 2)
    actual = base.get_best_acronym_web_resolution("", "EKG", "", 3, 5)
    assert expected == actual

    expected = ("Elektrokardiogramm", 1)
    actual = base.get_best_acronym_web_resolution("aaa bbb ccc", "EKG", "ddd eee fff", 3, 5)
    assert expected == actual
