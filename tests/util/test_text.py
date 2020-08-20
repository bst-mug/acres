import acres.util
from acres import constants
from acres.util import text


def test_remove_duplicated_whitespaces():
    expected = "abc def ghi z"
    actual = acres.util.text.remove_duplicated_whitespaces("abc    def   ghi z")
    assert expected == actual


def test_clean():
    input_text = "SB und LAHB, ¶ QRS-Verbreiterung auf ÐÐÐmsec., QTC ÐÐÐmsec.,"

    expected = "SB und LAHB QRS Verbreiterung auf ÐÐÐmsec QTC ÐÐÐmsec"
    assert expected == text.clean(input_text, preserve_linebreaks=False)

    expected = "SB und LAHB ¶ QRS Verbreiterung auf ÐÐÐmsec QTC ÐÐÐmsec"
    assert expected == text.clean(input_text, preserve_linebreaks=True)

    # Unicode characters should not be cleaned
    assert "herztöne" == text.clean("herztöne")
    assert "heißen" == text.clean("heißen")

    # This should also be cleaned
    assert "RG s" == text.clean("RG?s")
    assert "EKG s" == text.clean("EKG's")
