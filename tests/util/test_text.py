import acres.util
from acres.util import text


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


def test_replace_punctuation():
    expected = "life changing EKG"
    actual = acres.util.text.replace_punctuation("life-changing. EKG. ")
    assert expected == actual


def test_transliterate_to_seven_bit():
    assert "HAETTE" == acres.util.text.transliterate_to_seven_bit("hätte")
    assert "HATTE" == acres.util.text.transliterate_to_seven_bit("hätte", "en")

    assert "AANGSTROEM" == acres.util.text.transliterate_to_seven_bit("ångström")
    assert "ANGSTROM" == acres.util.text.transliterate_to_seven_bit("ångström", "en")


def test_remove_duplicated_whitespaces():
    expected = "abc def ghi z"
    actual = acres.util.text.remove_duplicated_whitespaces("abc    def   ghi z")
    assert expected == actual


def test_tokenize():
    expected = "SB und LAHB , ¶ QRS-Verbreiterung auf ÐÐÐmsec. , QTC ÐÐÐmsec. ,"
    input_text = "SB und LAHB, ¶ QRS-Verbreiterung auf ÐÐÐmsec., QTC ÐÐÐmsec.,"
    assert expected == text.tokenize(input_text)


def test_clean():
    input_text = "SB und LAHB, ¶ QRS-Verbreiterung auf ÐÐÐmsec., QTC ÐÐÐmsec.,"

    expected = "SB und LAHB QRS Verbreiterung auf ÐÐÐmsec QTC ÐÐÐmsec"
    assert expected == text.clean(input_text, preserve_linebreaks=False)

    expected = "SB und LAHB ¶ QRS Verbreiterung auf ÐÐÐmsec QTC ÐÐÐmsec"
    assert expected == text.clean(input_text, preserve_linebreaks=True)

    # Unicode characters should not be cleaned
    assert "herztöne" == text.clean("herztöne")
    assert "heißen" == text.clean("heißen")
