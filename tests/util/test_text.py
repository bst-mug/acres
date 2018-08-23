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


def test_replace_punctuation():
    expected = "life changing EKG"
    actual = acres.util.text.replace_punctuation("life-changing. EKG. ")
    assert expected == actual


def test_transliterate_to_seven_bit():
    assert "HAETTE" == acres.util.text.transliterate_to_seven_bit("hätte")
    assert "HATTE" == acres.util.text.transliterate_to_seven_bit("hätte", "en")

    assert "AANGSTROEM" == acres.util.text.transliterate_to_seven_bit("ångström")
    assert "ANGSTROM" == acres.util.text.transliterate_to_seven_bit("ångström", "en")


def test_substitute_k_and_f_by_context():
    assert "A" == acres.util.text.substitute_k_and_f_and_z_by_context("a")

    # Acronyms should not be substituted
    assert "aB" == acres.util.text.substitute_k_and_f_and_z_by_context("aB")
    assert "abCdef" == acres.util.text.substitute_k_and_f_and_z_by_context("abCdef")

    assert "PHARMACY" == acres.util.text.substitute_k_and_f_and_z_by_context("farmacy")

    assert "F" == acres.util.text.substitute_k_and_f_and_z_by_context("F")


def test_simplify_german_string():
    assert acres.util.text.simplify_german_string("LEBER") == "leber"

    assert acres.util.text.simplify_german_string("ekg") == "ecg"
    assert acres.util.text.simplify_german_string("heißen") == "heissen"
    assert acres.util.text.simplify_german_string(
        "Elektrokardiogramm") == "electrocardiogramm"

    # XXX Is it expected?
    assert acres.util.text.simplify_german_string("herz") == "herc"
    assert acres.util.text.simplify_german_string("café") == "cafe"
