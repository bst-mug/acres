from acres import functions


def test_get_url():
    url = "https://github.com/bst-mug/acres"
    actual = functions.get_url(url)

    # 200 means OK
    assert 200 == actual.status_code
    assert "Acronym" in actual.text


def test_split_ngram():
    # pass
    assert functions.split_ngram("a b c") == []
    #
    assert functions.split_ngram("a AK b") == [('a', 'AK', 'b')]
    #
    assert functions.split_ngram("l ACR1 b ACR2 c") == [(
        'l', 'ACR1', 'b ACR2 c'), ('l ACR1 b', 'ACR2', 'c')]
    #
    assert functions.split_ngram("ACR") == [('', 'ACR', '')]


def test_extract_acronym_definition():
    max_length = 7

    assert functions.extract_acronym_definition(
        "EKG (Elektrokardiogramm)", max_length) == ('EKG', 'Elektrokardiogramm')
    assert functions.extract_acronym_definition(
        "Elektrokardiogramm (EKG)", max_length) == ('EKG', 'Elektrokardiogramm')
    assert functions.extract_acronym_definition(
        "Elektrokardiogramm", max_length) is None


def test_fix_line_endings():
    expected = "This is a short text\n"
    actual = functions.fix_line_endings("This is a short text")
    assert expected == actual

    expected = "der Patientin\n"
    actual = functions.fix_line_endings("der\nPatientin")
    assert expected == actual

    expected = "DIAGNOSEN\n---------\n"
    actual = functions.fix_line_endings("DIAGNOSEN\n---------")
    assert expected == actual


def test_create_ngram_statistics():
    assert functions.create_ngram_statistics('a', 1, 1) == {'a': 1}
    assert functions.create_ngram_statistics('a b', 1, 1) == {'a': 1, 'b': 1}
    assert functions.create_ngram_statistics('a a', 1, 1) == {'a': 2}
    assert functions.create_ngram_statistics(
        'a b', 1, 2) == {'a': 1, 'b': 1, 'a b': 1}

    expected = {
        'a': 4,
        'ab': 1,
        'aa': 1,
        'ba': 1,
        'ddd': 1,
        'a ab': 1,
        'ab aa': 1,
        'aa a': 1,
        'a a': 2,
        'a ba': 1,
        'ba ddd': 1,
        'a ab aa': 1,
        'ab aa a': 1,
        'aa a a': 1,
        'a a a': 1,
        'a a ba': 1,
        'a ba ddd': 1,
        'a ab aa a': 1,
        'ab aa a a': 1,
        'aa a a a': 1,
        'a a a ba': 1,
        'a a ba ddd': 1}
    actual = functions.create_ngram_statistics('a ab aa a a a ba ddd', 1, 4)
    assert expected == actual


def test_transliterate_to_seven_bit():
    assert "HAETTE" == functions.transliterate_to_seven_bit("hätte")
    assert "HATTE" == functions.transliterate_to_seven_bit("hätte", "en")

    assert "AANGSTROEM" == functions.transliterate_to_seven_bit("ångström")
    assert "ANGSTROM" == functions.transliterate_to_seven_bit("ångström", "en")


def test_substitute_k_and_f_by_context():
    assert "A" == functions.substitute_k_and_f_and_z_by_context("a")

    # Acronyms should not be substituted
    assert "aB" == functions.substitute_k_and_f_and_z_by_context("aB")
    assert "abCdef" == functions.substitute_k_and_f_and_z_by_context("abCdef")

    assert "PHARMACY" == functions.substitute_k_and_f_and_z_by_context("farmacy")

    assert "F" == functions.substitute_k_and_f_and_z_by_context("F")


def test_is_acronym():
    # Single digits are not acronyms
    assert not functions.is_acronym("A", 3)

    # Lower-case are not acronyms
    assert not functions.is_acronym("ecg", 3)
    assert not functions.is_acronym("Ecg", 3)

    # Double upper-case are acronyms
    assert functions.is_acronym("AK", 2)

    # Acronyms should be shorter or equal to the maximum length
    assert not functions.is_acronym("EKG", 2)
    assert functions.is_acronym("EKG", 3)

    # Acronyms can contain diacritics
    # XXX This fails with Python 2, because "Ä".isupper() == False
    assert functions.is_acronym("ÄK", 3)

    # Acronyms can contain numbers
    assert functions.is_acronym("5FU", 7)


def test_simplify_german_string():
    assert functions.simplify_german_string("LEBER") == "leber"

    assert functions.simplify_german_string("ekg") == "ecg"
    assert functions.simplify_german_string("heißen") == "heissen"
    assert functions.simplify_german_string(
        "Elektrokardiogramm") == "electrocardiogramm"

    # XXX Is it expected?
    assert functions.simplify_german_string("herz") == "herc"
    assert functions.simplify_german_string("café") == "cafe"


def test_random_sub_list():
    # We output the input list if the length requested is larger or equal to
    # the input length
    assert functions.random_sub_list(["a", "b"], 2) == ["a", "b"]
    assert functions.random_sub_list(["a", "b"], 3) == ["a", "b"]

    # TODO use Random.seed() so that the output is deterministic
    assert functions.random_sub_list(["a", "b"], 1) in [["a"], ["b"]]


def test__acronym_aware_clean_expansion():
    # Baseline: return expansion if no symbols are found
    assert "Elektrokardiogramm" == functions._acronym_aware_clean_expansion("EKG",
                                                                            "Elektrokardiogramm")

    # We should clean symbols, unless they appear in the acronym itself
    assert "Angina pectoris" == functions._acronym_aware_clean_expansion("AP", "Angina&pectoris")
    assert "Angina&pectoris" == functions._acronym_aware_clean_expansion("A&P", "Angina&pectoris")

    # We should preserve spaces, happening or not in the acronym itself
    assert "Angina pectoris" == functions._acronym_aware_clean_expansion("AP", "Angina pectoris")
    assert "Angina pectoris" == functions._acronym_aware_clean_expansion("A P", "Angina pectoris")

    # We should preserve hyphens, happening or not in the acronym itself
    assert "Angina-pectoris" == functions._acronym_aware_clean_expansion("AP", "Angina-pectoris")
    assert "Angina-pectoris" == functions._acronym_aware_clean_expansion("A-P", "Angina-pectoris")

    # We strip the output even if the acronym itself is stripped
    assert "Angina pectoris" == functions._acronym_aware_clean_expansion(" AP ",
                                                                         " Angina pectoris ")

    # XXX We do not remove duplicated spaces
    assert "Angina   pectoris" == functions._acronym_aware_clean_expansion("AP",
                                                                           "Angina&&&pectoris")


def test_check_acro_vs_expansion():
    # Baseline
    expected = [('Elektro', 'kardio', 'gramm'),
                ('Ele', 'ktrokardio', 'gramm')]
    actual = functions.check_acro_vs_expansion("EKG", "Elektrokardiogramm")
    assert expected == actual

    # FIXME IndexError: string index out of range
    # expected = [('a')]
    # actual = functions.check_acro_vs_expansion("A", "a")
    # assert expected == actual

    # Expansion = acronym should still work
    expected = [('a', 'b')]
    actual = functions.check_acro_vs_expansion("AB", "ab")
    assert expected == actual

    expected = [('a', 'b', 'c')]
    actual = functions.check_acro_vs_expansion("ABC", "abc")
    assert expected == actual

    expected = [('a', 'b', 'c', 'd', 'e')]
    actual = functions.check_acro_vs_expansion("ABCDE", "abcde")
    assert expected == actual

    # No valid expansion should return empty
    expected = []
    actual = functions.check_acro_vs_expansion("EKG", "Elektro")
    assert expected == actual


def test_find_acronym_expansion():
    assert [] == functions.find_acro_expansions([])

    # FIXME explain reasoning and fix possible bugs
    expected = ['Im normale EKG post50     Im normalen elektrokardiogramm post30']
    actual = functions.find_acro_expansions(["50\tIm normale EKG post",
                                             "30\tIm normalen elektrokardiogramm post"])
    assert expected == actual


def test_robust_text_import_from_dir():
    actual = functions.robust_text_import_from_dir("tests/data")
    print(str(len(actual)))
    assert len(actual) == 20
