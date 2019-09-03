import acres.util
from acres import constants
from acres.util import text


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
    constants.LANGUAGE = "en"
    assert "HATTE" == acres.util.text.transliterate_to_seven_bit("hätte")
    assert "ANGSTROM" == acres.util.text.transliterate_to_seven_bit("ångström")

    constants.LANGUAGE = "de"
    assert "HAETTE" == acres.util.text.transliterate_to_seven_bit("hätte")
    assert "AANGSTROEM" == acres.util.text.transliterate_to_seven_bit("ångström")


def test_context_ngram():
    ngram = "A B C D E F"
    assert text.context_ngram(ngram, 3, True) == "D E F"
    assert text.context_ngram(ngram, 1, True) == "F"
    assert text.context_ngram(ngram, 0, True) == ""

    assert text.context_ngram(ngram, 3, False) == "A B C"
    assert text.context_ngram(ngram, 1, False) == "A"
    assert text.context_ngram(ngram, 0, False) == ""


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
