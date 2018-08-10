import acres.util


def test_diacritics():
    assert "ä" in acres.util.text.diacritics()


def test_fix_line_endings():
    expected = "This is a short text¶"
    actual = acres.util.text.fix_line_endings("This is a short text")
    assert expected == actual

    expected = "der Patientin¶"
    actual = acres.util.text.fix_line_endings("der\nPatientin")
    assert expected == actual

    expected = "DIAGNOSEN¶---------¶"
    actual = acres.util.text.fix_line_endings("DIAGNOSEN\n---------")
    assert expected == actual
